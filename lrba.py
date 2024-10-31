# lrba.py
import xml.etree.ElementTree as ET
import xml.dom.minidom as MD
import re
import constants
import argparse
from config import CONTADORES, AMBIENTES, AMBIENTE_DESARROLLO, AMBIENTE_INT, AMBIENTE_CALIDAD, AMBIENTE_AU, AMBIENTE_PRODUCCION, CONFIGURACION_DESARROLLO, CONFIGURACION_INT, CONFIGURACION_CALIDAD, CONFIGURACION_AU, CONFIGURACION_PRODUCCION, PREFIJOS_PEQUENOS, PREFIJOS_GRANDES ,PATRON_PREFIJOS_GRANDES, PATRON_PREFIJOS_PEQUENOS
from logger_setup import setup_logger

# Configuración de logger
logger = setup_logger()

# Lista para almacenar los mensajes de advertencia
mensajes = []

def incrementar_contador(contador_dict, key):
    if key in contador_dict:
        contador_dict[key] += 1
    else:
        logger.error(f"Contador '{key}' no existe.")

def main():
    # Mostrar ejemplo de uso
    epilog_text = f"{constants.EJEMPLO_USO_PRODUCCION}{constants.EJEMPLO_USO_CALIDAD}"
    # Inicializar el parser
    parser = argparse.ArgumentParser(description=constants.DESCRIPTION, epilog=epilog_text, formatter_class=argparse.RawTextHelpFormatter)
    # Argumentos para definir el ambiente y archivo XML
    parser.add_argument('--ambiente',type=str,choices=AMBIENTES,required=True,help=constants.HELP_AMB)
    parser.add_argument('--archivo-xml',type=str,required=True,help=constants.HELP_ARC)
    # Opciones de modificación
    parser.add_argument('--modificar-quantitative',action='store_true',help=constants.HELP_QUA)
    parser.add_argument('--modificar-domail',action='store_true',help=constants.HELP_DOM)
    parser.add_argument('--modificar-odate',action='store_true',help=constants.HELP_ODA)
    parser.add_argument('--modificar-jobs',type=str,help=constants.HELP_JOB)
    # Parsear los argumentos
    args = parser.parse_args()
    # Extraer la lista de jobs a modificar si se especifica el argumento
    if args.modificar_jobs:
        jobs_a_modificar = args.modificar_jobs.split(',')
        # Asegurar que cada job tenga dos dígitos
        jobs_a_modificar = [job.zfill(2) for job in jobs_a_modificar]
    else:
        jobs_a_modificar = None
        
    # Mensaje de bienvenida
    logger.info(constants.BIENVENIDA)
    logger.info(f"Ambiente seleccionado: {args.ambiente}")
    logger.info(f"Archivo XML a modificar: {args.archivo_xml}")
    if args.modificar_quantitative:
        logger.info(constants.OPCION_QUAN)
    if args.modificar_domail:
        logger.info(constants.OPCION_DOMAIL)
    if args.modificar_odate:
        logger.info(constants.OPCION_ODATE)
        
    modificar_xml(
        args.archivo_xml,
        args.ambiente,
        args.modificar_quantitative,
        args.modificar_domail,
        args.modificar_odate,
        jobs_a_modificar
    )
    
def modificar_xml(archivo_xml, ambiente, modificar_quan, modificar_domail, modificar_odate, jobs_a_modificar):
    tree, root = cargar_xml(archivo_xml)
    if root is None:
        return
    conf = seleccionar_configuracion(ambiente)
    # Inicializamos un contador para las modificaciones de JOBNAME/QUANTITATIVE
    modificar_folder(root, conf["nuevo_datacenter"])
    # Recorremos cada etiqueta JOB
    for job in root.findall(constants.JOB):
        jobname = job.get(constants.JOBNAME)
        run_as = job.get(constants.RUN_AS)
        parent_folder = job.get(constants.PARENT_FOLDER)
        application = job.get(constants.APPLICATION)
        sub_application = job.get(constants.SUB_APPLICATION)
        # Constantes para patrones de email
        DOMAIL_SUBJECT = 'Error %%JOBNAME - %%$ODATE M malla ' + parent_folder
        DOMAIL_MESSAGE = '0051Error %%JOBNAME - %%$ODATE M malla ' + parent_folder
        # Si se proporcionó una lista de jobs específicos, filtrar por los últimos dos caracteres de JOBNAME
        if jobs_a_modificar and jobname[-2:] not in jobs_a_modificar:
            continue
        # Modifica JOBNAME
        nuevo_jobname = modificar_jobname(jobname, conf["letra_cambio"], PREFIJOS_GRANDES, PREFIJOS_PEQUENOS)
        if nuevo_jobname != jobname:
            job.set(constants.JOBNAME, nuevo_jobname)
            incrementar_contador(CONTADORES, constants.CONTADOR_MODIFICACIONES)
            logger.debug(f'JOBNAME modificado de "{jobname}" a "{nuevo_jobname}"')
        # Modifica NODEID (cambiar a los valores dependiendo del ambiente)
        modificar_nodeid(job, conf)
        # Modifica CMDLINE (cambiar .dev por .au o .prod dependiendo del ambiente)
        modificar_cmdline(job, conf)
        # Modificar la etiqueta ON y sus subetiquetas DOMAIL
        modificar_domail_en_on(job, conf, ambiente, modificar_domail, parent_folder, DOMAIL_SUBJECT, DOMAIL_MESSAGE)             
        # Modificar INCOND
        inconds = job.findall(constants.INCOND)
        modificar_condiciones(inconds, conf["letra_cambio"], conf["nuevo_condicion"], '|'.join(PREFIJOS_GRANDES), '|'.join(PREFIJOS_PEQUENOS))
        # Modificar OUTCOND
        outconds = job.findall(constants.OUTCOND)
        modificar_condiciones(outconds, conf["letra_cambio"], conf["nuevo_condicion"], '|'.join(PREFIJOS_GRANDES), '|'.join(PREFIJOS_PEQUENOS))
        # Comprobar si RUN_AS es igual a "lrba-ctm"
        modificar_quantitative(job, conf, ambiente, modificar_quan)
        # Modificar SUB_APPLICATION
        procesar_application(job, conf)
    
    for variable in root.findall(constants.VARIABLE):
        modificar_variable(variable, ambiente, modificar_odate, CONTADORES)
        
    xml_str = ET.tostring(root, constants.VAR_UTF)
    parsed_string = MD.parseString(xml_str)
    pretty_xml_as_string = parsed_string.toprettyxml(indent=constants.VAR_INDENT, encoding=constants.VAR_UTF).decode(constants.VAR_UTF)
    pretty_xml_as_string = constants.VAR_BACK_SLASH.join([line for line in pretty_xml_as_string.splitlines() if line.strip()])
    with open(parent_folder+'-generate.xml', constants.VAR_W, encoding=constants.VAR_UTF) as f:
            f.write(pretty_xml_as_string)    
    #tree.write(parent_folder+'-generate.xml', encoding="utf-8", xml_declaration=True)
    logger.info(f'Archivo modificado guardado como {parent_folder}-generate.xml')
    
    # Imprime los mensajes acumulados al final
    for mensaje in mensajes:
        logger.info(f'mensaje')
    # Muestra la cantidad de JOBNAME modificados
    registrar_modificaciones(CONTADORES)

def modificar_jobname(jobname, letra_cambio, prefijos_grandes, prefijos_pequeños):
    # Crea las expresiones regulares una vez
    patron_prefijos_grandes = '|'.join(prefijos_grandes)
    patron_prefijos_pequeños = '|'.join(prefijos_pequeños)
    
    logger.info(f"Modificando JOBNAME: '{jobname}'")
    
    # Modifica el JOBNAME basado en prefijos grandes
    if re.match(r'^(' + PATRON_PREFIJOS_GRANDES + ').*', jobname):
        if len(jobname) > 6 and jobname[6] in constants.AMB_PERMITIDO_LRBA:
            nuevo_jobname = jobname[:6] + letra_cambio + jobname[7:]
            logger.info(f"JOBNAME modificado (prefijos grandes, posición 6): '{nuevo_jobname}'")
            return nuevo_jobname
        elif len(jobname) > 6 and jobname[7] in constants.AMB_PERMITIDO_LRBA:
            nuevo_jobname = jobname[:7] + letra_cambio + jobname[8:]
            logger.info(f"JOBNAME modificado (prefijos grandes, posición 7): '{nuevo_jobname}'")
            return nuevo_jobname

    # Modifica el JOBNAME basado en prefijos pequeños
    elif re.match(r'^(' + PATRON_PREFIJOS_PEQUENOS + ').*', jobname):
        if len(jobname) > 5 and jobname[5] in constants.AMB_PERMITIDO_LRBA:
            nuevo_jobname = jobname[:5] + letra_cambio + jobname[6:]
            logger.info(f"JOBNAME modificado (prefijos pequeños, posición 5): '{nuevo_jobname}'")
            return nuevo_jobname
    
    return jobname  # Si no se hace ninguna modificación, devolver el original

# Función para cargar el XML
def cargar_xml(archivo_xml):
    try:
        tree = ET.parse(archivo_xml)
        return tree, tree.getroot()
    except ET.ParseError as e:
        logger.error(f"Error al parsear el archivo XML: {e}")
        return None, None
    except FileNotFoundError as e:
        logger.error(f"Archivo XML no encontrado: {e}")
        return None, None
    
# Función para seleccionar configuración según ambiente
def seleccionar_configuracion(ambiente):
    if ambiente == AMBIENTE_CALIDAD:
        return CONFIGURACION_CALIDAD
    elif ambiente == AMBIENTE_DESARROLLO:
        return CONFIGURACION_DESARROLLO
    elif ambiente == AMBIENTE_PRODUCCION:
        return CONFIGURACION_PRODUCCION
    elif ambiente == AMBIENTE_INT:
        return CONFIGURACION_INT
    else:
        return CONFIGURACION_AU     

# Función para modificar el folder
def modificar_folder(root, nuevo_datacenter):
    folder = root.find(constants.FOLDER)
    if folder is not None:
        folder.set(constants.DATACENTER, nuevo_datacenter)
        logger.debug(f'FOLDER modificado: DATACENTER="{nuevo_datacenter}"')

# Función para modificar NODEID
def modificar_nodeid(job, conf):
    nodeid = job.get(constants.NODEID)
    if nodeid and nodeid in constants.NODO_PERMITIDO_DATAX:
        job.set(constants.NODEID, conf["nuevo_nodeid"])
        incrementar_contador(CONTADORES, constants.CONTADOR_NODEID)
        logger.debug(f'NODEID modificado de {nodeid} a {conf["nuevo_nodeid"]}')
        return True
    elif nodeid in constants.NODO_PERMITIDO_LRBA:
        job.set(constants.NODEID, conf["nuevo_nodeidlrba"])
        incrementar_contador(CONTADORES, constants.CONTADOR_NODEID)
        logger.debug(f'NODEID modificado de {nodeid} a {conf["nuevo_nodeidlrba"]}')
        return True
    return False

# Función para modificar CMDLINE
def modificar_cmdline(job, conf):
    cmdline = job.get(constants.CMDLINE)
    variables = [constants.VAR_DEV, constants.VAR_INT, constants.VAR_AU, constants.VAR_QA, constants.VAR_PROD]
    # Verificación y reemplazo en CMDLINE
    if cmdline and constants.LLNAMESPACE in cmdline:
        for var in variables:
            if var in cmdline:
                nuevo_cmdline = cmdline.replace(var, conf["nuevo_cmdline_ambiente"])
                job.set(constants.CMDLINE, nuevo_cmdline)
                incrementar_contador(CONTADORES, constants.CONTADOR_CMDLINE)
                logger.debug(f'CMDLINE modificado de {cmdline} a {nuevo_cmdline}')
                return True
    # Verificación y reemplazo en VARIABLES
    for variable in job.findall(constants.VARIABLE):
        name = variable.get(constants.NAME)
        value = variable.get(constants.VALUE)
        if name in constants.NODO_PERMITIDO_VAR_NAMESPACE and value:
            for var in variables:
                if var in value:
                    nuevo_value = value.replace(var, conf["nuevo_variable_ambiente"])
                    variable.set(constants.VALUE, nuevo_value)
                    incrementar_contador(CONTADORES, constants.CONTADOR_NAMESPACE)
                    logger.debug(f'VARIABLE modificado de {value} a {nuevo_value}')
                    return True  
    return False

# Función para modificar DOMAIL
def modificar_domail_en_on(job, conf, ambiente, modificar_domail, parent_folder, subject, message):
    if modificar_domail:
        on_tags = job.findall(constants.ON)
        if not on_tags:
            nueva_etiqueta = crear_domail(ambiente, conf["domail_destino"], subject, message)
            # Insertar la nueva etiqueta ON después de la última etiqueta OUTCOND
            job.append(nueva_etiqueta)
            # Incrementar contador
            incrementar_contador(CONTADORES, constants.CONTADOR_DOMAIL)
            logger.debug(f'Etiqueta ON añadida al final del JOB con RUN_AS "lrba-ctm": {ET.tostring(nueva_etiqueta).decode()}')
        else:
            # Si existen etiquetas ON, modificar las etiquetas DOMAIL dentro de ellas
            for on in on_tags:
                for domail in on.findall(constants.DOMAIL):
                    domail.set(constants.VAR_DEST, conf["domail_destino"])
                    domail.set(constants.VAR_SUBJECT, subject)
                    domail.set(constants.VAR_MESSAGE, message)
                    incrementar_contador(CONTADORES, constants.CONTADOR_DOMAIL_M)
                    logger.debug(f'DOMAIL modificado: DEST="{domail.get("DEST")}", SUBJECT="{subject}", MESSAGE="{message}"')

def crear_domail(ambiente, conf, subject, message):
    on_element = ET.Element(constants.ON, {
        "STMT": "*",
        "CODE": "NOTOK"
    })
    # Crear la etiqueta QUANTITATIVE según el ambiente
    if ambiente in constants.AMBIENTES_PREVIOS:
        element = ET.Element(constants.DOMAIL, {
            "URGENCY": constants.VAR_URGENCY,
            "DEST": conf,
            "SUBJECT": subject,
            "MESSAGE": message,
            "ATTACH_SYSOUT": constants.VAR_Y
        })
    elif ambiente == constants.PRODUCCION:
        element = ET.Element(constants.DOMAIL, {
            "URGENCY": constants.VAR_URGENCY,
            "DEST": conf,
            "SUBJECT": subject,
            "MESSAGE": message,
            "ATTACH_SYSOUT": constants.VAR_Y
        })
    # Agregar QUANTITATIVE a ON
    on_element.append(element)
    return on_element

# Función para modificar INCOND y OUTCOND
def modificar_condiciones(condiciones, letra_cambio, nuevo_condicion, patron_prefijos_grandes, patron_prefijos_pequeños):
    for condicion in condiciones:
        name = condicion.get(constants.NAME)
        if name and name.startswith(constants.VAR_COXCRX) and len(name) > 8:
            nuevo_name = name[:7] + nuevo_condicion + name[8:]  # Modificar el carácter en la posición 7
            condicion.set(constants.NAME, nuevo_name)
            logger.debug(f'{condicion.tag} modificado: NAME="{name}" a "{nuevo_name}"')
        else:
            logger.debug(f'Entrando en ELSE para {condicion.tag}: NAME="{name}"')
            # Buscamos los patrones de UUAA y modificamos en consecuencia
            if re.match(r'^(' + patron_prefijos_grandes + ').*', name):  
                partes = name.split(constants.VAR_TO)
                if len(partes) == 2:
                    parte_izquierda = partes[0]
                    parte_derecha = partes[1]
                    # Cambia el carácter en la posición deseada
                    nuevo_nombre_izquierda = parte_izquierda[:6] + letra_cambio + parte_izquierda[7:]
                    nuevo_nombre_derecha = parte_derecha[:6] + letra_cambio + parte_derecha[7:]
                    nuevo_name = nuevo_nombre_izquierda + constants.VAR_TO + nuevo_nombre_derecha
                    condicion.set(constants.NAME, nuevo_name)
                    logger.debug(f'{condicion.tag} modificado: NAME="{name}" a "{nuevo_name}"')

            elif re.match(r'^(' + patron_prefijos_pequeños + ').*', name):
                partes = name.split(constants.VAR_TO)
                if len(partes) == 2:
                    parte_izquierda = partes[0]
                    parte_derecha = partes[1]
                    # Cambia el carácter en la posición deseada (un carácter menos)
                    nuevo_nombre_izquierda = parte_izquierda[:5] + letra_cambio + parte_izquierda[6:]
                    nuevo_nombre_derecha = parte_derecha[:5] + letra_cambio + parte_derecha[6:]
                    nuevo_name = nuevo_nombre_izquierda + constants.VAR_TO + nuevo_nombre_derecha
                    condicion.set(constants.NAME, nuevo_name)
                    logger.debug(f'{condicion.tag} modificado: NAME="{name}" a "{nuevo_name}"')
            else:
                print(f'No se encontró un patrón para {condicion.tag}: NAME="{name}"')

# Función para modificar QUANTITATIVE
def modificar_quantitative(job, conf, ambiente, modificar_quantitative):
    run_as = job.get(constants.RUN_AS)
    if modificar_quantitative and run_as == constants.LRBA_CTM:
        quantitative = job.find(constants.QUANTITATIVE)
        existe_quantitative = job.find(constants.QUANTITATIVE) is not None
        if not existe_quantitative:
            nueva_etiqueta = crear_quantitative(ambiente)
            on_tag = job.find(constants.OUTCOND2)
            if on_tag is not None:
                for idx, child in enumerate(job):
                    if child == on_tag:
                        job.insert(idx, nueva_etiqueta)
                        incrementar_contador(CONTADORES, constants.CONTADOR_QUAN)
                        logger.debug(f'Etiqueta QUANTITATIVE añadida antes de la etiqueta ON en JOB con RUN_AS "lrba-ctm": {ET.tostring(nueva_etiqueta).decode()}')
                        return True
        else:
            actualizar_quantitative(quantitative, ambiente)
            incrementar_contador(CONTADORES, constants.CONTADOR_QUAN_M)
            logger.debug(f'Etiqueta QUANTITATIVE actualizada en JOB con RUN_AS "lrba-ctm": {ET.tostring(quantitative).decode()}')
            return True
    return False

# Función para crear etiqueta QUANTITATIVE
def crear_quantitative(ambiente):
    if ambiente in constants.AMBIENTES_PREVIOS:
        return ET.Element("QUANTITATIVE", {
            "NAME": constants.VAR_QUAN_WORK,
            "QUANT": constants.VAR_NUMBER_ONE,
            "ONFAIL": constants.VAR_URGENCY,
            "ONOK": constants.VAR_URGENCY
        })
    elif ambiente == constants.PRODUCCION:
        return ET.Element("QUANTITATIVE", {
            "NAME": constants.VAR_QUAN_LIVE,
            "QUANT": constants.VAR_NUMBER_ONE,
            "ONFAIL": constants.VAR_URGENCY,
            "ONOK": constants.VAR_URGENCY
        })

def actualizar_quantitative(quantitative, ambiente):
    if ambiente in constants.AMBIENTES_PREVIOS:
        quantitative.set("NAME", constants.VAR_QUAN_WORK)
    elif ambiente == constants.PRODUCCION:
        quantitative.set("NAME", constants.VAR_QUAN_LIVE)
    quantitative.set("QUANT", constants.VAR_NUMBER_ONE)
    quantitative.set("ONFAIL", constants.VAR_URGENCY)
    quantitative.set("ONOK", constants.VAR_URGENCY)

def modificar_variable(variable, ambiente, modificar_odate, contadores):
    value = variable.get(constants.VALUE)
    nuevo_value = value  # Inicializar el valor a modificar
    
    # Verifica si el VALUE comienza con COB o DOF
    if value.startswith(tuple(constants.PREFIJOS_COB)):
        # Cambia el prefijo en calidad y producción
        if ambiente == constants.DESARROLLO:
            nuevo_value = constants.PREFIJO_COBD_DESARROLLO + value[4:]
        elif ambiente == constants.CALIDAD:  # Suponiendo que 'ambiente' es una variable que define el ambiente
            nuevo_value = constants.PREFIJO_COBD_CALIDAD + value[4:]  # Cambia COB
        elif ambiente == constants.PRODUCCION:
            nuevo_value = constants.PREFIJO_COBD_PRODUCCION + value[4:]  # Cambia COB

    elif value.startswith(tuple(constants.PREFIJOS_OF)):
        # Cambia el prefijo en calidad y producción
        if ambiente == constants.DESARROLLO:
            nuevo_value = constants.PREFIJO_DOF_DESARROLLO + value[3:]
        elif ambiente == constants.CALIDAD:
            nuevo_value = constants.PREFIJO_DOF_CALIDAD + value[3:]  # Cambia OF
        elif ambiente == constants.PRODUCCION:
            nuevo_value = constants.PREFIJO_DOF_PRODUCCION + value[3:]  # Cambia OF

    # Verifica si VALUE contiene %%ODATE
    if modificar_odate and '%%ODATE' in nuevo_value:
        # Verifica de que no termina con %%ODATE
        if not nuevo_value.endswith('%%ODATE'):
            # Asegúrate de que tenga exactamente dos puntos después de %%ODATE
            index_odate = nuevo_value.index('%%ODATE') + 8
            if index_odate < len(nuevo_value) and nuevo_value[index_odate] != '.':
                if nuevo_value[index_odate:index_odate + 2] != constants.VAR_DOBPOINT:  # Verifica que no haya ya dos puntos
                    nuevo_value = nuevo_value.replace('%%ODATE', '%%ODATE..')  # Modifica para añadir los dos puntos
                    incrementar_contador(contadores, constants.CONTADOR_ODATE)

    # Asegura que no se agreguen más de dos puntos
    if nuevo_value.count(constants.VAR_DOBPOINT) > 1:  # Si ya hay más de un par de puntos
        nuevo_value = nuevo_value.replace(constants.VAR_DOBPOINT, '', nuevo_value.count(constants.VAR_DOBPOINT) - 1)  # Elimina los extras

    # Actualiza el VALUE de la VARIABLE
    variable.set(constants.VALUE, nuevo_value)
    logger.debug(f'VARIABLE VALUE modificado de "{value}" a "{nuevo_value}"')

def procesar_application(job, conf):
    application = job.get(constants.APPLICATION)
    sub_application = job.get(constants.SUB_APPLICATION)

    # Verificar si "-CO-" está presente en la etiqueta application
    if constants.VAR_CO in application:
        # Extraer lo que sigue a "-CO-"
        index_co = application.index(constants.VAR_CO)
        sub_application_value = application[index_co + 1:]  # Obtener la subcadena empezando en "-CO-"
        sub_ccr = conf["sub_app_ctrlm"]
        # Asignar el nuevo valor a sub_application
        job.set(constants.SUB_APPLICATION, sub_application_value + sub_ccr)
        logger.debug(f'SUB_APPLICATION modificado a "{sub_application_value}" para job {job.get(constants.JOBNAME)}')
    else:
        logger.debug(f'SUB_APPLICATION no modificado para job {job.get(constants.JOBNAME)} ya que no contiene "-CO-"')

def registrar_modificaciones(contadores):
    # Lista de registros para las modificaciones
    if contadores[constants.CONTADOR_MODIFICACIONES] > 0:
        logger.warning(f'Total de JOBNAME modificados: {contadores["modificaciones"]}')
    if contadores[constants.CONTADOR_NODEID] > 0:
        logger.warning(f'Total de NODEID modificados: {contadores["nodeid"]}')
    if contadores[constants.CONTADOR_CMDLINE] > 0:
        logger.warning(f'Total de CMDLINE--namespace modificados: {contadores["cmdline"]}')
    if contadores[constants.CONTADOR_NAMESPACE] > 0:
        logger.warning(f'Total de VARIABLES%%namespace modificados: {contadores["namespace"]}')
    if contadores[constants.CONTADOR_DOMAIL] > 0:
        logger.warning(f'Total de DOMAIL agregados: {contadores["domail"]}')
    if contadores[constants.CONTADOR_DOMAIL_M] > 0:
        logger.warning(f'Total de DOMAIL modificados: {contadores["domailm"]}')       
    if contadores[constants.CONTADOR_ODATE] > 0:
        logger.warning(f'Total de %%ODATE modificados: {contadores["odate"]}')        
    if contadores[constants.CONTADOR_QUAN] > 0:
        logger.warning(f'Total de QUANTITATIVE agregados: {contadores["quan"]}')
    if contadores[constants.CONTADOR_QUAN_M] > 0:
        logger.warning(f'Total de QUANTITATIVE modificados: {contadores["quanm"]}')
        
if __name__ == "__main__":
    main()