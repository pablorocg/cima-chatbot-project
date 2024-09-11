from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain.pydantic_v1 import BaseModel, Field
from typing import Dict, Union, Optional
from langchain.output_parsers import PydanticOutputParser
from langchain_community.document_loaders import UnstructuredPDFLoader
from unstructured.cleaners.core import clean_extra_whitespace
from langchain.text_splitter import RecursiveCharacterTextSplitter



def answer_question(question: str) -> str:
    
    template = """
    
    Question: {question}

    Answer: 
    """

    prompt = ChatPromptTemplate.from_template(template)

    model = OllamaLLM(model="gemma2:2b", base_url="http://ollama:11434")

    chain = prompt | model | StrOutputParser()

    response = chain.invoke({"question": question})

    return response


class KnowledgeBase(BaseModel):
    ## Fields of the BaseModel, which will be validated/assigned when the knowledge base is constructed
    topic: str = Field('general', description="Current conversation topic")
    user_preferences: Dict[str, Union[str, int]] = Field({}, description="User preferences and choices")
    session_notes: str = Field("", description="Notes on the ongoing session")
    unresolved_queries: list = Field([], description="Unresolved user queries")
    action_items: list = Field([], description="Actionable items identified during the conversation")



if __name__ == "__main__":
    if False:
        question = "What is the capital of France?"
        print(answer_question(question))
        print(repr(KnowledgeBase(topic = "Travel")))
        instruct_string = PydanticOutputParser(pydantic_object=KnowledgeBase).get_format_instructions()
        print(instruct_string)

    ## Load the document https://python.langchain.com/v0.2/docs/how_to/document_loader_pdf/#using-unstructured
    document = UnstructuredPDFLoader("/app/TFM_Pablo_Rocamora_García.pdf", extract_images=False, post_processors=[clean_extra_whitespace]).load()
    print(document)

    

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", ";", ",", " ", ""],
    )

    chunks = text_splitter.split_documents(document)
    print(chunks)
    print(len(chunks))

    for i in (0, 1, 2, 15, -1):
        print(f"[Document {i}]")
        print(chunks[i].page_content)
        print("="*64)

    from langchain_core.runnables import RunnableLambda
    from langchain_core.runnables.passthrough import RunnableAssign
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain.output_parsers import PydanticOutputParser

    # from langchain_nvidia_ai_endpoints import ChatNVIDIA

    from langchain_core.pydantic_v1 import BaseModel, Field
    from typing import List
    # from IPython.display import clear_output


    class DocumentSummaryBase(BaseModel):
        running_summary: str = Field("", description="Running description of the document. Do not override; only update!")
        main_ideas: List[str] = Field([], description="Most important information from the document (max 3)")
        loose_ends: List[str] = Field([], description="Open questions that would be good to incorporate into summary, but that are yet unknown (max 3)")


    summary_prompt = ChatPromptTemplate.from_template(
        "You are generating a running summary of the document. Make it readable by a technical user."
        " After this, the old knowledge base will be replaced by the new one. Make sure a reader can still understand everything."
        " Keep it short, but as dense and useful as possible! The information should flow from chunk to (loose ends or main ideas) to running_summary."
        " The updated knowledge base keep all of the information from running_summary here: {info_base}."
        "\n\n{format_instructions}. Follow the format precisely, including quotations and commas"
        "\n\nWithout losing any of the info, update the knowledge base with the following: {input}"
    )

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


    latest_summary = ""

    ## TODO: Use the techniques from the previous notebook to complete the exercise
    def RSummarizer(knowledge, llm, prompt, verbose=False):
        '''
        Exercise: Create a chain that summarizes
        '''
        ###########################################################################################
        ## START TODO:

        def summarize_docs(docs):        
            ## TODO: Initialize the parse_chain appropriately; should include an RExtract instance.
            ## HINT: You can get a class using the <object>.__class__ attribute...
            # parse_chain = RunnableAssign({'info_base' : (lambda x: None)})
            parse_chain = RunnableAssign({'info_base' : RExtract(knowledge.__class__, llm, prompt)})
            ## TODO: Initialize a valid starting state. Should be similar to notebook 4
            # state = {}
            state = {'info_base' : knowledge}

            global latest_summary  ## If your loop crashes, you can check out the latest_summary
            
            for i, doc in enumerate(docs):
                ## TODO: Update the state as appropriate using your parse_chain component
                state['input'] = doc.page_content
                state = parse_chain.invoke(state)

                assert 'info_base' in state 
                if verbose:
                    print(f"Considered {i+1} documents")
                    print(state['info_base'])
                    latest_summary = state['info_base']
                    # clear_output(wait=True)

            return state['info_base']
            
        ## END TODO
        ###########################################################################################
        
        return RunnableLambda(summarize_docs)

    
    instruct_model = OllamaLLM(model="gemma2:2b", base_url="http://ollama:11434").bind(max_tokens=2048)
    instruct_llm = instruct_model | StrOutputParser()

    ## Take the first 10 document chunks and accumulate a DocumentSummaryBase
    summarizer = RSummarizer(DocumentSummaryBase(), instruct_llm, summary_prompt, verbose=True)
    summary = summarizer.invoke(chunks[:15])

    print(summary)
