# Extract info from prompt and fill the pydantic object using the LLM
from api_calls import (
    MedicamentoQueryParams, get_medicamento,
    MedicamentosQueryParamsV2, get_medicamentos_v2,
)
from pydantic_api_models import (
    Medicamento, ListaMedicamentos

)
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema.runnable import RunnableBranch, RunnablePassthrough
from langchain.schema.runnable.passthrough import RunnableAssign
from langchain_chroma import Chroma
from langchain_community.document_loaders import OnlinePDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from typing import List
from langchain.schema import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableBranch
from langchain_core.tools import BaseTool
import unicodedata
import string

## Definition of RExtract
def RExtract(pydantic_class, llm, prompt):
    '''
    Runnable Extraction module
    Returns a knowledge dictionary populated by slot-filling extraction
    '''
    parser = PydanticOutputParser(pydantic_object=pydantic_class)
    instruct_merge = RunnableAssign({'format_instructions' : lambda x: parser.get_format_instructions()})
    def preparse(string):
        if '{' not in string: string = '{' + string
        if '}' not in string: string = string + '}'
        string = (string
            .replace("\\_", "_")
            .replace("\n", " ")
            .replace("\]", "]")
            .replace("\[", "[")
        )
        print(string)  ## Good for diagnostics
        return string
    return instruct_merge | prompt | llm | preparse | parser


def parameter_extractor(pydantic_class, user_query):
    instruct_llm = OllamaLLM(model="gemma2:9b", base_url="http://ollama:11434")# "gemma2:2b" o "gemma2:9b"

    parser_prompt = ChatPromptTemplate.from_template(
        "Eres un asistente virtual especializado en la búsqueda de información de medicamentos para el servicio SearchMed. "
        "Tu objetivo es extraer información relevante de la conversación actual del usuario de manera precisa y concisa. "
        "Debes completar el esquema con base en la información proporcionada en el mensaje del usuario, sin agregar detalles adicionales o inventar datos que no estén explícitamente mencionados."
        "\n\n{format_instructions}"
        "\n\nMENSAJE DEL USUARIO: {input}"
        "\n\nCONTEXTUALIZACIÓN: Usa solo la información proporcionada para completar el esquema. No utilices datos externos ni supongas detalles no mencionados explícitamente por el usuario."
    )
    extractor = RExtract(
        pydantic_class, 
        instruct_llm, 
        parser_prompt
    )

    knowledge = extractor.invoke({'input' : user_query})

    return knowledge


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def search_queries_about_drug(drug_info: ListaMedicamentos, user_query: str):
    """
    Searches for queries related to a specific drug.
    Args:
        drug_info (ListaMedicamentos): Information about the drug, including documents.
        user_query (str): The user's query.
    Returns:
        list: URLs of the documents related to the drug.
    """
  
    documents_urls = [doc.url for doc in drug_info.docs]

    # Load only the first document for testing purposes
    documents_urls = documents_urls[:1]

    loaded_documents = []
    for url in documents_urls:
        doc = OnlinePDFLoader(file_path=url).load_and_split()
        loaded_documents.extend(doc)
        print(f"Documento cargado y dividido desde {url}")
    
    # Inicializar el embebido y almacenamiento vectorial
    embedder = OllamaEmbeddings(model="all-minilm", base_url="http://ollama:11434")
    vectorstore = Chroma("langchain_store", embedder)
    vectorstore.add_documents(loaded_documents)
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    prompt = ChatPromptTemplate.from_template("""
        Eres un asistente para tareas de respuesta a preguntas.
        Utiliza los siguientes fragmentos de contexto obtenidos para responder a la pregunta.
        Si no conoces la respuesta, simplemente di que no lo sabes.
        Utiliza un máximo de tres oraciones y mantén la respuesta concisa. Responde en español.

        Pregunta: {question}

        Contexto: {context}

        Respuesta:
    """)

    llm = OllamaLLM(model="gemma2:9b", base_url="http://ollama:11434")

    rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
    )

    response = rag_chain.invoke({"question": user_query})
  
    return response


class EndpointMedicamentoTool(BaseTool):
    """
    Este servicio se utiliza cuando el usuario proporciona información específica y única como 
    el código nacional (CN) o el número de registro de un medicamento. Permite obtener detalles 
    sin ambigüedad directamente de la base de datos de la AEMPS.
    Devuelve un objeto Pydantic con toda la información disponible del medicamento.

    Ejemplo de Query:
    "Quiero obtener información sobre el medicamento con código nacional 726684"
    """
    name = "Búsqueda de medicamento por código o registro"
    description = "Proporciona información detallada sobre un medicamento específico cuando el usuario aporta un código nacional (CN) o número de registro."

    
    def _run(self, query: str) -> Medicamento:
        knowledge = parameter_extractor(MedicamentoQueryParams, query)  # Extrae el código o registro del medicamento de la consulta
        medicamento = get_medicamento(knowledge)  # Llama al servicio API de la AEMPS
        return medicamento


class EndpointMedicamentosTool(BaseTool):
    """
    Este servicio se utiliza cuando el usuario proporciona información distinta al código nacional (CN) 
    o al número de registro de un medicamento. Permite obtener detalles sin ambigüedad directamente de la base de datos de la AEMPS.
    Devuelve una lista de objetos Pydantic con los resultados obtenidos en la búsqueda, conteniendo toda la información disponible del medicamento.

    Ejemplo de Query:
    "Quiero obtener información sobre la aspirina vía oral"
    """
    name = "Búsqueda de medicamentos por descripción o características"
    description = "Proporciona información detallada sobre medicamentos a partir de descripciones generales, como el nombre, la forma farmacéutica, la vía de administración u otras características, sin requerir el código nacional (CN) o número de registro."

    def _run(self, query: str) -> List[ListaMedicamentos]:
        knowledge = parameter_extractor(MedicamentosQueryParamsV2, query)  # Extrae los parámetros de la consulta
        medicamentos = get_medicamentos_v2(knowledge)  # Llama al servicio API de la AEMPS
        return medicamentos

    



# Función para limpiar y normalizar la query
def normalize_query(query: str) -> str:
    
    # Eliminar acentos y convertir a minúsculas
    query = unicodedata.normalize('NFKD', query).encode('ascii', 'ignore').decode('utf-8').lower()
    # Eliminar puntuación y espacios
    query = query.translate(str.maketrans('', '', string.punctuation)).replace(" ", "")
    return query

# Función para clasificar la query y decidir qué cadena utilizar
def route(info):
    query = normalize_query(info["query"])
    
    # Palabras clave para identificar si la consulta es sobre un medicamento concreto o una lista
    list_keywords_medicamento = ["medicamento", "codigo", "registro", "nacional", "cn"]
    
    if any(keyword in query for keyword in list_keywords_medicamento):
        return EndpointMedicamentoTool()
    else:
        return EndpointMedicamentosTool()


def answer_question(user_query: str) -> str:
    # Crear la cadena principal utilizando RunnableLambda para enrutamiento
    full_chain = {"query": lambda x: x["query"]} | RunnableLambda(route)
    response = full_chain.invoke({"query": user_query}) # Response es un objeto Pydantic con las respuestas de la AEMPS

    if isinstance(response, list):
        medicamento = response[0]
    else:
        medicamento = response

    answer_question = search_queries_about_drug(medicamento, user_query)
    return answer_question

if __name__ == "__main__":
    
    print(answer_question("Quiero obtener información general sobre el medicamento con código nacional 726684"))
    print(answer_question("¿Es el medicamento con codigo nacional 726684 apto para mujeres embarazadas?"))
    print(answer_question("¿Qué reacciones adversas puede tener la aspirina?"))

