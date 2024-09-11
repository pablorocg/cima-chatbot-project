import requests, json, os, sys
import httpx
from langchain.pydantic_v1 import BaseModel, Field
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from pydantic_api_models import ListaMedicamentos, Medicamento, ListaPresentaciones

# Base URL for the CIMA API
CIMA_BASE_URL = "https://cima.aemps.es/cima/rest"
CIMA_DOCS_BASE_URL = "https://cima.aemps.es/cima/dochtml"


class MedicamentosQueryParams(BaseModel):
    nombre: Optional[str] = Field(None, description="Nombre comercial del medicamento (sin información adicional)")
    laboratorio: Optional[str] = Field(None, description="Nombre del laboratorio")
    practiv1: Optional[str] = Field(None, description="Nombre del principio activo")
    practiv2: Optional[str] = Field(None, description="Nombre del segundo principio activo")
    idpractiv1: Optional[str] = Field(None, description="ID del principio activo")
    idpractiv2: Optional[str] = Field(None, description="ID del segundo principio activo")
    cn: Optional[str] = Field(None, description="Código nacional")
    atc: Optional[str] = Field(None, description="Código ATC o descripción")
    nregistro: Optional[str] = Field(None, description="Nº de registro")
    npactiv: Optional[int] = Field(None, description="Nº de principios activos asociados al medicamento")
    triangulo: Optional[int] = Field(None, description="1 – Tienen triángulo, 0 –No tienen triángulo")
    huerfano: Optional[int] = Field(None, description="1 – Huérfano, 0 –No huérfano")
    biosimilar: Optional[int] = Field(None, description="1 – Biosimilar, 0 –No biosimilar")
    sust: Optional[int] = Field(None, description="""1 – Biológicos, 
                                                2 – Medicamentos con principios activos de estrecho margen terapéutico, 
                                                3 – Medicamentos de especial control médico o con medidas especiales de seguridad,
                                                4 – Medicamentos para el aparato respiratorio administrados por vía inhalatoria, 
                                                5 – Medicamentos de estrecho margen terapéutico""")
    vmp: Optional[str] = Field(None, description="ID del código VMP")
    comerc: Optional[int] = Field(None, description="1 – Comercializados, 0 – No comercializado")
    autorizados: Optional[int] = Field(None, description="1 – Solo medicamentos autorizados, 0 – Solo medicamentos no autorizados")
    receta: Optional[int] = Field(None, description="1 – Medicamentos con receta, 0 – Medicamentos sin receta")
    estupefaciente: Optional[int] = Field(None, description="1 – Devuelve los medicamentos estupefacientes")
    psicotropo: Optional[int] = Field(None, description="1 – Devuelve los medicamentos psicotropos")
    estuopsico: Optional[int] = Field(None, description="1 – Devuelve los medicamentos estupefacientes o psicotropos")

# Fetch list of medications based on given conditions 
#Devuelve una lista de objetos ListaMedicamentos o None si hay un error
def get_medicamentos(params: MedicamentosQueryParams) -> Optional[List[ListaMedicamentos]]:
    # Prepare the query parameters, excluding unset fields
    query_params = params.dict(exclude_unset=True)
    
    try:
        # Make the request to the CIMA API
        response = requests.get(f"{CIMA_BASE_URL}/medicamentos", params=query_params)
        response.raise_for_status()  # Raises an HTTPError if the status is 4xx/5xx
        response = response.json()  # Return the response in JSON format
        print(response)
        resultados = response["resultados"]
        return [ListaMedicamentos(**med) for med in resultados]
    
    except requests.exceptions.RequestException as e:
        # Imprimir el error en caso de una solicitud fallida
        print(f"Error al hacer la consulta a la API de CIMA: {e}")
        return None

#================================================================================================
class MedicamentosQueryParamsV2(BaseModel):
    nombre: Optional[str] = Field(None, description="Nombre comercial del medicamento (sin información adicional)")
    laboratorio: Optional[str] = Field(None, description="Nombre del laboratorio")
    practiv1: Optional[str] = Field(None, description="Nombre del principio activo")
    

def get_medicamentos_v2(params: MedicamentosQueryParams) -> Optional[List[ListaMedicamentos]]:
    
    query_params = params.dict(exclude_unset=True)
    
    try:
        # Make the request to the CIMA API
        response = requests.get(f"{CIMA_BASE_URL}/medicamentos", params=query_params)
        response.raise_for_status()  # Raises an HTTPError if the status is 4xx/5xx
        response = response.json()  # Return the response in JSON format
        print(response)
        resultados = response["resultados"]
        return [ListaMedicamentos(**med) for med in resultados]
    
    except requests.exceptions.RequestException as e:
        # Imprimir el error en caso de una solicitud fallida
        print(f"Error al hacer la consulta a la API de CIMA: {e}")
        return None

#================================================================================================
# Define the Pydantic model for the query parameters
class MedicamentoQueryParams(BaseModel):
    cn: Optional[str] = Field(None, description="Código nacional")
    nregistro: Optional[str] = Field(None, description="Nº de registro")

# Función para hacer la solicitud a la API de CIMA
def get_medicamento(params: MedicamentoQueryParams):
    # Convertir los parámetros a un diccionario, excluyendo aquellos no proporcionados
    query_params = params.dict(exclude_unset=True)

    try:
        # Hacer la solicitud GET a la API de CIMA con los parámetros proporcionados
        response = requests.get(f"{CIMA_BASE_URL}/medicamento", params=query_params)
        response.raise_for_status()  # Levantar excepción en caso de un error HTTP (4xx/5xx)
        response = response.json()  # Devolver la respuesta en formato JSON
        return Medicamento(**response)  # Convertir el JSON a un objeto Medicamento


    except requests.exceptions.RequestException as e:
        # Imprimir el error en caso de una solicitud fallida
        print(f"Error al hacer la consulta a la API de CIMA: {e}")
        return None

#================================================================================================

# Pydantic model for JSON body in POST request
class FichaTecnicaQuery(BaseModel):
    seccion: str = Field(..., description="Sección en la que se buscará. Desde 1 hasta 10")
    texto: str = Field(..., description="Texto a buscar")
    contiene: int = Field(..., description="0 si no se quiere que contenga el texto, 1 si se quiere que lo contenga")

# Función para hacer la solicitud POST a la API de CIMA
def buscar_en_ficha_tecnica(queries: List[FichaTecnicaQuery]):
    # Convertir la lista de objetos FichaTecnicaQuery a una lista de diccionarios (JSON)
    query_list = [query.dict() for query in queries]
    headers = {"Content-Type": "application/json"}

    try:
        # Hacer la solicitud POST a la API de CIMA
        response = requests.post(f"{CIMA_BASE_URL}/buscarEnFichaTecnica", json=query_list, headers=headers)
        response.raise_for_status()  # Levantar excepción en caso de error HTTP (4xx/5xx)
        response = response.json()  # Return the response in JSON format
        resultados = response["resultados"]
        return [ListaMedicamentos(**med) for med in resultados]
    



    except requests.exceptions.RequestException as e:
        # Manejar errores en la solicitud HTTP
        print(f"Error al hacer la consulta a la API de CIMA: {e}")
        return None

#================================================================================================
# Pydantic model for Presentaciones query parameters
class PresentacionesQueryParams(BaseModel):
    cn: Optional[str] = Field(None, description="Código nacional")
    nregistro: Optional[str] = Field(None, description="Nº de registro")
    vmp: Optional[str] = Field(None, description="ID del código VMP")
    vmpp: Optional[str] = Field(None, description="ID del código VMPP")
    idpractiv1: Optional[str] = Field(None, description="ID del principio activo")
    comerc: Optional[int] = Field(None, description="1 – Comercializados, 0 – No comercializados")
    estupefaciente: Optional[int] = Field(None, description="1 – Devuelve los medicamentos estupefacientes")
    psicotropo: Optional[int] = Field(None, description="1 – Devuelve los medicamentos psicotropos")
    estuopsico: Optional[int] = Field(None, description="1 – Devuelve los medicamentos estupefacientes o psicotropos")


def get_presentaciones(query_params: PresentacionesQueryParams) -> Optional[List[ListaPresentaciones]]:
    params = query_params.dict(exclude_unset=True)
    
    try:
        # Make the GET request to the CIMA API
        response = requests.get(f"{CIMA_BASE_URL}/presentaciones", params=params)
        response.raise_for_status()
        response = response.json()
        resultados = response["resultados"]
        return [ListaPresentaciones(**med) for med in resultados]  # Convertir a objetos
    
    # ListaPresentaciones
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from CIMA API: {e}")
        return None
#================================================================================================
class PresentacionQueryParams(BaseModel):
    codNacional: str = Field(..., description="Código nacional del medicamento")

def get_presentacion(params: PresentacionQueryParams) -> Optional[Dict[str, Any]]:
    #Devuelve la información de una presentación pasando el código nacional
    try:
        response = requests.get(f"{CIMA_BASE_URL}/presentacion", params=params.dict())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from CIMA API: {e}")
        return None

#================================================================================================
# Pydantic model for VMP/VMPP query parameters
class VmppQueryParams(BaseModel):
    practiv1: Optional[str] = Field(None, description="Nombre del principio activo")
    idpractiv1: Optional[str] = Field(None, description="ID del principio activo")
    dosis: Optional[str] = Field(None, description="Dosis")
    forma: Optional[str] = Field(None, description="Nombre de la forma farmacéutica")
    atc: Optional[str] = Field(None, description="Código ATC o descripción")
    nombre: Optional[str] = Field(None, description="Nombre del medicamento")
    modoArbol: Optional[bool] = Field(None, description="Modo jerárquico")


def get_vmpp(query_params: VmppQueryParams):
    params = query_params.dict(exclude_unset=True)
    
    try:
        # Make the GET request to the CIMA API
        response = requests.get(f"{CIMA_BASE_URL}/vmpp", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from CIMA API: {e}")
        return None


#================================================================================================
# Definir una clase Pydantic para los parámetros de consulta de maestras
class MaestrasQueryParams(BaseModel):
    maestra: Optional[int] = Field(None, description="ID de la maestra a devolver (1: Principios activos, 3: Formas farmacéuticas, etc.)")
    nombre: Optional[str] = Field(None, description="Nombre del elemento a recuperar")
    Id: Optional[str] = Field(None, description="ID del elemento a recuperar")
    codigo: Optional[str] = Field(None, description="Código del elemento a recuperar")
    estupefaciente: Optional[int] = Field(None, description="1 – Devuelve los principios activos estupefacientes")
    psicotropo: Optional[int] = Field(None, description="1 – Devuelve los principios activos psicotropos")
    estuopsico: Optional[int] = Field(None, description="1 – Devuelve los medicamentos estupefacientes o psicotropos")
    enuso: Optional[int] = Field(None, description="0 – Devuelve tanto los principios activos asociados como los que no están")


def get_maestras(query_params: MaestrasQueryParams) -> dict:
    params = query_params.dict(exclude_unset=True)
    
    try:
        response = requests.get(f"{CIMA_BASE_URL}/maestras", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from CIMA API: {e}")
        return None
    

#================================================================================================
# Definir una clase Pydantic para los parámetros de consulta de registro de cambios
class RegistroCambiosQueryParams(BaseModel):
    fecha: Optional[str] = Field(None, description="Fecha a partir de la cual se desean conocer cambios (formato dd/mm/yyyy)")
    nregistro: Optional[str] = Field(None, description="Número de registro del medicamento a limitar la búsqueda")


def get_registro_cambios(query_params: RegistroCambiosQueryParams) -> dict:
    params = query_params.dict(exclude_unset=True)
    
    try:
        response = requests.get(f"{CIMA_BASE_URL}/registroCambios", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from CIMA API: {e}")
        return None


def post_registro_cambios(query_params: RegistroCambiosQueryParams) -> dict:
    params = query_params.dict(exclude_unset=True)
    
    try:
        response = requests.post(f"{CIMA_BASE_URL}/registroCambios", json=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from CIMA API: {e}")
        return None

#================================================================================================
# Definir una clase Pydantic para los parámetros de consulta del docSegmentado/secciones
# Pydantic model para los parámetros del documento segmentado secciones
class DocSegmentadoSeccionesParams(BaseModel):
    tipoDoc: int = Field(..., description="Tipo de documento (1: Ficha técnica, 2: Prospecto)")
    nregistro: str = Field(..., description="Nº de registro del medicamento")

# Función para obtener las secciones del documento segmentado
def get_doc_segmentado_secciones(query_params: DocSegmentadoSeccionesParams) -> Optional[Dict[str, Any]]:
    url = f"{CIMA_BASE_URL}/docSegmentado/secciones/{query_params.tipoDoc}"
    params = query_params.dict(exclude={"tipoDoc"})  # Excluir tipoDoc del diccionario de parámetros, ya que está en la URL

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Levantar excepción en caso de error HTTP (4xx/5xx)
        return response.json()  # Devolver la respuesta JSON
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener las secciones del documento: {e}")
        return None

#================================================================================================
# Definir una clase Pydantic para los parámetros de consulta del docSegmentado/contenido
# Definir una clase Pydantic para los parámetros de consulta del docSegmentado/contenido
# Pydantic model para los parámetros del documento segmentado contenido
class DocSegmentadoContenidoParams(BaseModel):
    tipoDoc: int = Field(..., description="Tipo de documento (1: Ficha técnica, 2: Prospecto)")
    nregistro: str = Field(..., description="Nº de registro del medicamento")
    seccion: Optional[str] = Field(None, description="ID de la sección a devolver. Si es nulo, devuelve todas las secciones")

# Función para limpiar el marcado HTML usando BeautifulSoup
def filter_html_text(html_texto: str) -> str:
    soup = BeautifulSoup(html_texto, "html.parser")
    return soup.get_text()


# Función para obtener el contenido del documento segmentado
def get_doc_segmentado_contenido(query_params: DocSegmentadoContenidoParams, accept: Optional[str] = None) -> Optional[Any]:
    url = f"{CIMA_BASE_URL}/docSegmentado/contenido/{query_params.tipoDoc}"
    params = query_params.dict(exclude={"tipoDoc"})  # Excluir tipoDoc del diccionario de parámetros, ya que está en la URL
    headers = {"Accept": accept} if accept else {}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Levantar excepción en caso de error HTTP (4xx/5xx)
        
        # Procesar la respuesta en función del valor de "Accept"
        if accept == "application/json":
            return response.json()  # Devolver la respuesta en formato JSON
        elif accept == "text/plain":
            return response.text  # Devolver texto plano
        elif accept == "text/html":
            return response.text  # Devolver el contenido HTML tal cual
        else:
            # Si no se especifica un tipo, devolver en formato JSON por defecto
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el contenido del documento: {e}")
        return None
#================================================================================================

# Modelo para los parámetros de la ficha técnica completa
class FichaTecnicaCompletaParams(BaseModel):
    nregistro: str = Field(..., description="Número de registro del medicamento")

# Función para obtener la ficha técnica completa en formato HTML
def get_ficha_tecnica_completa(params: FichaTecnicaCompletaParams) -> Optional[str]:
    url = f"{CIMA_DOCS_BASE_URL}/ft/{params.nregistro}/FichaTecnica.html"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verificar si hay errores HTTP
        return response.text  # Devolver el contenido HTML
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la ficha técnica completa: {e}")
        return None

#================================================================================================
# Modelo para los parámetros de una sección específica de la ficha técnica
class FichaTecnicaSeccionParams(BaseModel):
    nregistro: str = Field(..., description="Número de registro del medicamento")
    seccion: str = Field(..., description="Sección a consultar de la ficha técnica")

# Función para obtener una sección específica de la ficha técnica
def get_ficha_tecnica_seccion(params: FichaTecnicaSeccionParams) -> Optional[str]:
    url = f"{CIMA_DOCS_BASE_URL}/ft/{params.nregistro}/{params.seccion}/FichaTecnica.html"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verificar si hay errores HTTP
        return response.text  # Devolver el contenido HTML
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la sección {params.seccion} de la ficha técnica: {e}")
        return None
#================================================================================================
# Modelo para los parámetros del prospecto completo
class ProspectoCompletoParams(BaseModel):
    nregistro: str = Field(..., description="Número de registro del medicamento")


# Función para obtener el prospecto completo en formato HTML
def get_prospecto_completo(params: ProspectoCompletoParams) -> Optional[str]:
    url = f"{CIMA_DOCS_BASE_URL}/p/{params.nregistro}/Prospecto.html"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verificar si hay errores HTTP
        return filter_html_text(response.text)  # Devolver el contenido HTML filtrado
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el prospecto completo: {e}")
        return None

#================================================================================================
# Modelo para los parámetros de una sección específica del prospecto
class ProspectoSeccionParams(BaseModel):
    nregistro: str = Field(..., description="Número de registro del medicamento")
    seccion: str = Field(..., description="Sección a consultar del prospecto")

# Función para obtener una sección específica del prospecto
def get_prospecto_seccion(params: ProspectoSeccionParams) -> Optional[str]:
    url = f"{CIMA_DOCS_BASE_URL}/p/{params.nregistro}/{params.seccion}/Prospecto.html"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verificar si hay errores HTTP
        return response.text  # Devolver el contenido HTML
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la sección {params.seccion} del prospecto: {e}")
        return None









#================================================================================================
if __name__ == "__main__":
    # Probar todas las funciones aquí
    prueba = "Nada"
   

    if prueba == "medicamentos":
        # Crear una instancia de los parámetros de consulta
        params = MedicamentosQueryParams(nombre="duloxetina")
        
        # Realizar la consulta con los parámetros definidos
        resultados = get_medicamentos(params)
        print(resultados)
        print(len(resultados))
    elif prueba == "medicamento":
        # Crear una instancia de los parámetros de consulta
        params = MedicamentoQueryParams(cn="765692")
        
        # Realizar la consulta con los parámetros definidos
        resultado = get_medicamento(params)
        print(resultado)
    elif prueba == "buscar_en_ficha_tecnica":
        # Crear una lista de objetos FichaTecnicaQuery
        queries = [
            FichaTecnicaQuery(seccion="4.1", texto="acidez", contiene=1),
            FichaTecnicaQuery(seccion="4.1", texto="estomago", contiene=0),
            FichaTecnicaQuery(seccion="4.2", texto="dolor", contiene=1)
        ]
        
        # Realizar la consulta con los parámetros definidos
        resultado = buscar_en_ficha_tecnica(queries)
        print(resultado)
    elif prueba == "presentaciones":
        # Crear una instancia de los parámetros de consulta
        params = PresentacionesQueryParams(cn="765699")
        
        # Realizar la consulta con los parámetros definidos
        resultado = get_presentaciones(params)
        print(resultado)
    elif prueba == "presentacion":
        # Crear una instancia de los parámetros de consulta
        params = PresentacionQueryParams(codNacional="765699")
        
        # Realizar la consulta con los parámetros definidos
        resultado = get_presentacion(params)
        print(resultado)


    



    

