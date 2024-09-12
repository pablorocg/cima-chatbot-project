
from lxml import etree
import json

# Cargar y parsear el archivo XML
archivo_xml = '/app/docs/bbdd_completa_con_nomenclator_de_prescripcion/DICCIONARIO_ATC.xml'
tree = etree.parse(archivo_xml)
root = tree.getroot()


#
# Función recursiva para convertir el XML en un diccionario
def xml_to_dict(element):
    result = {}
    
    # Si el elemento tiene hijos, recorremos los hijos y los convertimos a diccionario
    if len(element):
        for child in element:
            child_result = xml_to_dict(child)
            # Si el tag ya existe en el diccionario, lo convertimos en una lista
            if child.tag in result:
                if isinstance(result[child.tag], list):
                    result[child.tag].append(child_result)
                else:
                    result[child.tag] = [result[child.tag], child_result]
            else:
                result[child.tag] = child_result
    # Si no tiene hijos, guardamos los atributos y el texto
    else:
        result = element.text if element.text is not None else ''
    
    # Agregar atributos si los tiene, convirtiéndolos explícitamente a un diccionario estándar
    if element.attrib:
        result['@attributes'] = dict(element.attrib)

    return result


# Convertir el árbol XML en un diccionario
xml_dict = xml_to_dict(root)

# Convertir el diccionario a JSON
json_data = json.dumps(xml_dict, indent=4, ensure_ascii=False)

# Visualizar el JSON
print(json_data)
