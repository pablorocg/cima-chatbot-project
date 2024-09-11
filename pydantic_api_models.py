from langchain.pydantic_v1 import BaseModel, Field
from typing import List, Optional, Dict

# Definimos submodelos para representar partes más complejas del medicamento
# Estado del medicamento
class Estado(BaseModel):
    """
    Devuelve la información de los estados de un medicamento. Si está autorizado solo devolverá
    la fecha de autorización. Si está revocado o suspendido devolverá también esas fechas.
    """
    aut: Optional[int] = Field(None, description="Fecha de autorización del medicamento/presentación")
    susp: Optional[int] = Field(None, description="Fecha de suspensión del medicamento/presentación")
    rev: Optional[int] = Field(None, description="Fecha de revocación del medicamento/presentación")


class ProblemaSuministro(BaseModel):
    """
    Contiene la información relativa a los problemas de suministro asociados a una presentación.
    """
    cn: Optional[str] = Field(None, description="Código nacional")
    nombre: Optional[str] = Field(None, description="Nombre de la presentación")
    fini: Optional[int] = Field(None, description="Fecha de inicio del problema de suministro en formato Unix Epoch (milisegundos)")
    ffin: Optional[int] = Field(None, description="Fecha prevista de fin del problema de suministro en formato Unix Epoch (milisegundos). Si no está activo, es la fecha en la que se solucionó")
    observ: Optional[str] = Field(None, description="Observaciones asociadas")
    activo: Optional[bool] = Field(None, description="Indica si el problema de suministro sigue activo o si ya se ha solucionado")


class Seccion(BaseModel):
    """
    Contiene la información de una sección de un documento asociado a un medicamento.
    """
    seccion: Optional[str] = Field(None, description="Indica el número de sección, puede contener hasta tres niveles separados por '.'")
    titulo: Optional[str] = Field(None, description="Título de la sección")
    orden: Optional[int] = Field(None, description="Orden de la sección en el documento")
    contenido: Optional[str] = Field(None, description="Texto de la sección en formato HTML")


# Documento asociado a un medicamento
class Documento(BaseModel):
    """
    Contiene la información relativa a los documentos asociados a un medicamento.
    """
    tipo: Optional[int] = Field(None, description="1: Ficha Técnica, 2: Prospecto, 3: Informe Público Evaluación, 4: Plan de gestión de riesgos")
    url: Optional[str] = Field(None, description="URL del documento asociado")
    secc: Optional[bool] = Field(None, description="Indica si el documento está disponible en HTML por secciones")
    urlHtml: Optional[str] = Field(None, description="URL en formato HTML solo si secc = true")
    fecha: Optional[int] = Field(None, description="Fecha de modificación del documento")

class Nota(BaseModel):
    """
    Contiene la informacion relativa a las notas de seguridad o informativas asociadas a un medicamento.
    """
    tipo: int = Field(..., description="Tipo de nota: 1: Seguridad")
    num: str = Field(..., description="Número de la nota")
    ref: str = Field(..., description="Referencia asociada a la nota")
    asunto: str = Field(..., description="Asunto de la nota")
    fecha: int = Field(..., description="Fecha de la nota en formato Unix Epoch (milisegundos)")
    url: str = Field(..., description="URL de la nota publicada en la web de la AEMPS")

class DocumentoMaterial(BaseModel):
    """"
    Contiene la información relativa a los documentos asociados a un medicamento
    """
    # nombre, url, fecha
    nombre: Optional[str] = Field(None, description="Título del documento")
    url: Optional[str] = Field(None, description="URL para acceder al documento asociado")
    fecha: Optional[int] = Field(None, description="Fecha de actualización del documento")

class Material(BaseModel):
    """"
    Contiene la información relativa a los materiales informativos sobre seguridad asociados a un medicamento
    """
    titulo : Optional[str] = Field(None, description="Título del material informativo")
    listaDocsPaciente: Optional[List[DocumentoMaterial]] = Field(None, description="Lista de documentos para el paciente")
    listaDocsProfesional: Optional[List[DocumentoMaterial]] = Field(None, description="Lista de documentos para el profesional")
    video: Optional[str] = Field(None, description="URL para acceder al vídeo (solo si el formato de los materiales es vídeo)")

class DescripcionClinica(BaseModel):
    """"
    Contiene la información relativa a la descripción clínica (VMP/VMPP)
    """
    vmp: Optional[str] = Field(None, description="Código de VMP")
    vmpDesc: Optional[str] = Field(None, description="Nombre del VMP")
    vmpp: Optional[str] = Field(None, description="Código de VMPP")
    vmppDesc: Optional[str] = Field(None, description="Nombre del VMPP")
    presComerc: Optional[str] = Field(None, description="Número de presentaciones comercializadas para el VMPP")

class ATC(BaseModel):
    """"
    Contiene la información relativa al código ATC
    """
    codigo: Optional[str] = Field(None, description="Código ATC")
    nombre: Optional[str] = Field(None, description="Nombre descriptivo")
    nivel: Optional[int] = Field(None, description="Nivel del código ATC")

class Presentacion(BaseModel):
    """
    Contiene la información relativa a una presentación de un medicamento
    """
    cn: Optional[str] = Field(None, description="Código nacional nº de registro")
    nombre: Optional[str] = Field(None, description="Nombre de la presentación")
    estado: Optional[Estado] = Field(None, description="Estado de autorización de la presentación")
    comerc: Optional[bool] = Field(None, description="Indica si la presentación está comercializada")
    psum: Optional[bool] = Field(None, description="Indica si la presentación es de uso hospitalario")


class PrincipioActivo(BaseModel):
    """"
    Contiene la información relativa al principio activo
    """
    id: Optional[int] = Field(None, description="ID del principio activo")
    nombre: Optional[str] = Field(None, description="Nombre del principio activo")
    cantidad: Optional[str] = Field(None, description="Cantidad del principio activo")
    unidad: Optional[str] = Field(None, description="Unidad para la cantidad")
    orden: Optional[int] = Field(None, description="Orden en la lista de principios activos de un medicamento")


# Modelo Pydantic para Excipiente
class Excipiente(BaseModel):
    id: Optional[int] = Field(None, description="ID de excipiente")
    nombre: Optional[str] = Field(None, description="Nombre del excipiente")
    cantidad: Optional[str] = Field(None, description="Cantidad del excipiente")
    unidad: Optional[str] = Field(None, description="Unidad para la cantidad")
    orden: Optional[int] = Field(None, description="Orden en la lista de excipientes de un medicamento")


# Modelo Pydantic para Foto
class Foto(BaseModel):
    tipo: Optional[str] = Field(None, description="Indica el tipo de foto: materialas - 'material de acondicionamiento secundario' o formafarmac - 'forma farmacéutica'")
    url: Optional[str] = Field(None, description="URL para acceder a la imagen")
    fecha: Optional[int] = Field(None, description="Fecha de actualización de la imagen")

# Modelo Pydantic para Item
class Item(BaseModel):
    """Representa un elemento con identificador numérico, código alfanumérico y nombre."""
    id: Optional[int] = Field(None, description="Identificador numérico del elemento")
    codigo: Optional[str] = Field(None, description="Identificador alfanumérico del elemento")
    nombre: Optional[str] = Field(None, description="Nombre del elemento")

# Modelo principal del Medicamento
class Medicamento(BaseModel):
    """
    Contiene la información relativa a un medicamento.
    """
    nregistro: str = Field(..., description="Número de registro del medicamento")
    nombre: str = Field(..., description="Nombre del medicamento")
    pactivos: Optional[str] = Field(..., description="Lista de principios activos separada por comas. Solo aparece el nombre")
    labtitular: Optional[str] = Field(None, description="Laboratorio titular del medicamento")
    estado: Optional[Estado] = Field(None, description="Estado de registro del medicamento")
    cpresc: Optional[str] = Field(None, description="Condiciones de prescripción del medicamento")

    comerc: bool = Field(..., description="Indica si tiene alguna presentación comercializada")
    receta: bool = Field(..., description="Indica si el medicamento necesita receta para su dispensación")
    conduc: bool = Field(..., description="Indica si el medicamento afecta a la conducción")
    triangulo: bool = Field(..., description="Indica si el medicamento tiene asociado el triángulo negro")
    huerfano: bool = Field(..., description="Indica si el medicamento está considerado como medicamento huérfano")
    biosimilar: bool = Field(..., description="Indica si el medicamento está considerado como biosimilar")
    ema: bool = Field(..., description="Indica si el medicamento se ha registrado por procedimiento centralizado (EMA) o no")
    psum: bool = Field(..., description="Indica si el medicamento tiene problemas de suministro abiertos")

    # Listas de objetos relacionados
    docs: List[Documento] = Field([], description="Lista de documentos asociados al medicamento")
    fotos: List[Foto] = Field([], description="Lista de imágenes asociadas al medicamento")
    notas: bool = Field(..., description="Indica si existen notas asociadas al medicamento")
    materialesInf: bool = Field(..., description="Indica si existen materiales informáticos asociados al medicamento")
    
    # Listas adicionales
    atcs: List[Item] = Field([], description="Lista de códigos ATC asociados al medicamento")
    principiosActivos: List[PrincipioActivo] = Field([], description="Lista de los principios activos del medicamento")
    excipientes: List[Excipiente] = Field([], description="Lista de excipientes del medicamento")
    viasAdministracion: List[Item] = Field([], description="Lista de vías de administración autorizadas para el medicamento")
    nosustituible: Optional[Item] = Field(None, description="Indica si el tipo de medicamento es sustituible o no")

    # Presentaciones y formas farmacéuticas
    presentaciones: List[Item] = Field([], description="Lista de presentaciones del medicamento")
    formaFarmaceutica: Optional[Item] = Field(None, description="Forma farmacéutica del medicamento")
    formaFarmaceuticaSimplificada: Optional[Item] = Field(None, description="Forma farmacéutica simplificada")
    
    # Dosis
    dosis: Optional[str] = Field(None, description="Dosis de los principios activos. En caso de más de un principio activo, se separan por '/' en el mismo orden que los principios activos.")


class ListaPresentaciones(BaseModel):
    """
    Contiene la información relativa a las presentaciones de un medicamento.
    """
    nregistro: str = Field(..., description="Número de registro del medicamento")
    cn: str = Field(..., description="Código nacional de la presentación")
    nombre: str = Field(..., description="Nombre de la presentación")
    
    pactivos: str = Field(..., description="Lista de principios activos separados por comas")
    labtitular: Optional[str] = Field(None, description="Laboratorio titular del medicamento")
    estado: Optional[Estado] = Field(None, description="Estado de registro de la presentación")
    cpresc: Optional[str] = Field(None, description="Condiciones de prescripción del medicamento")
    
    comerc: bool = Field(..., description="Indica si la presentación está comercializada o no")
    conduc: bool = Field(..., description="Indica si el medicamento afecta o no a la conducción")
    triangulo: bool = Field(..., description="Indica si el medicamento tiene asociado el triángulo negro")
    huerfano: bool = Field(..., description="Indica si el medicamento está considerado como medicamento huérfano")
    
    ema: bool = Field(..., description="Indica si el medicamento se ha registrado por procedimiento centralizado (EMA)")
    psum: bool = Field(..., description="Indica si la presentación tiene problemas de suministro abiertos")
    
    docs: List[Documento] = Field([], description="Lista de documentos asociados al medicamento")
    notas: bool = Field(..., description="Indica si existen notas asociadas al medicamento")


class ListaMedicamentos(BaseModel):
    """
    Contiene la información relativa a la lista de medicamentos.
    """
    nregistro: str = Field(..., description="Número de registro del medicamento")
    nombre: str = Field(..., description="Nombre comercial del medicamento (sin nada mas)")
    labtitular: str = Field(..., description="Laboratorio titular del medicamento")
    estado: Estado = Field(..., description="Estado de autorización del medicamento")
    cpresc: str = Field(..., description="Condiciones de prescripcion del medicamento")
    comerc: bool = Field(..., description="Indica si tiene alguna presentación comercializada")
    receta: bool = Field(..., description="Indica si el medicamento requiere receta")
    conduc: bool = Field(..., description="Indica si afecta a la conducción o no")
    triangulo: bool = Field(..., description="Indica si el medicamento tienen asociado el triángulo negro")
    # huerfano, biosimilar, nosustituible, psum, ema, notas, materialesInf, docs, fotos, viasAdministracion, formaFarmaceutica, formaFarmaceuticaSimplificada, dosis
    huerfano: bool = Field(..., description="Indica si el medicamento está considerado como huérfano")
    biosimilar: bool = Field(..., description="Indica si el medicamento está considerado como biosimilar")
    nosustituible: Item = Field(None, description="Indica si es un medicamento No Sustituible y el tipo en caso de serlo")
    psum: bool = Field(..., description="Indica si el medicamento tiene problemas de suministro abiertos")
    ema: bool = Field(..., description="Indica si el medicamento se ha registrado por procedimiento centralizado (EMA) o no")
    notas: bool = Field(..., description="Indica si existen notas asociadas al medicamento")
    materialesInf: bool = Field(..., description="Indica si existen materiales informáticos de seguridad asociados al medicamento")
    
    # Lista de documentos y fotos asociadas al medicamento
    docs: List[Documento] = Field([], description="Lista de documentos asociados al medicamento")
    fotos: List[Foto] = Field([], description="Lista de imágenes asociadas al medicamento")
    
    # Lista de vías de administración y formas farmacéuticas
    viasAdministracion: List[Item] = Field([], description="Lista de las vías de administración para las que está autorizado el medicamento")
    formaFarmaceutica: Optional[Item] = Field(None, description="Forma farmacéutica del medicamento")
    formaFarmaceuticaSimplificada: Optional[Item] = Field(None, description="Forma farmacéutica simplificada del medicamento")
    
    # Dosis del medicamento
    dosis: Optional[str] = Field(None, description="Dosis del o los principios activos. En el caso de que haya más de un principio activo, aparecerán separados por '/' y en el mismo orden que los principios activos.")




# Modelo Pydantic para Registro de Cambios
class RegistroCambios(BaseModel):
    """Contiene la información sobre los cambios realizados en un medicamento."""
    nregistro: Optional[str] = Field(None, description="Nº de registro del medicamento")
    fecha: Optional[int] = Field(None, description="Fecha en la que se ha producido el cambio en formato Unix Epoch (milisegundos)")
    tipoCambio: Optional[int] = Field(None, description="Tipo de cambio (1: Nuevo, 2: Baja, 3: Modificado)")
    cambios: List[str] = Field([], description="""Lista con cadenas de texto que identifican los cambios que se han producido: "estado": estado de autorizacion, "comerc": estado de comercializacion, "prosp": prospecto, "ft": ficha tecnica, "psum": problemas de suministro, "notasSeguridad": notas de seguridad, "matinf": materiales informativos, "otros": cualquier otro cambio.""")
