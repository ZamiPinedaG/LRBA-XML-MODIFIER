# lrba.py
import xml.etree.ElementTree as ET
import re
import constants
import argparse
from config import CONTADORES, AMBIENTES, AMBIENTE_DESARROLLO, AMBIENTE_CALIDAD, AMBIENTE_PRODUCCION, CONFIGURACION_DESARROLLO, CONFIGURACION_CALIDAD, CONFIGURACION_PRODUCCION, PREFIJOS_PEQUENOS, PREFIJOS_GRANDES ,PATRON_PREFIJOS_GRANDES, PATRON_PREFIJOS_PEQUENOS
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
    # Inicializar el parser
    parser = argparse.ArgumentParser(
        description="Script para transformar archivos XML de Control-M a diferentes ambientes."
    )
    # Argumentos para definir el ambiente y archivo XML
    parser.add_argument(
        '--ambiente',
        type=str,
        choices=AMBIENTES,
        required=True,
        help="Especifica el ambiente de destino (desarrollo, calidad, producción)"
    )
    parser.add_argument(
        '--archivo-xml',
        type=str,
        required=True,
        help="Especifica el nombre del archivo XML (con extensión)"
    )
    # Opciones de modificación
    parser.add_argument(
        '--modificar-quantitative',
        action='store_true',
        help="Modifica/Agrega las etiquetas QUANTITATIVE en el archivo XML"
    )
    parser.add_argument(
        '--modificar-domail',
        action='store_true',
        help="Modifica las etiquetas DOMAIL en el archivo XML"
    )
    parser.add_argument(
        '--modificar-odate',
        action='store_true',
        help="Modifica las variables %%ODATE en el archivo XML para agregar '..' de ser necesario"
    )
    parser.add_argument(
        '--modificar-jobs',
        type=str,
        help="Modifica solo jobs específicos, proporcionando los últimos dos caracteres de los JOBNAME separados por comas (ej: 01,02,03)"
    )
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
    logger.info("BIENVENIDO A LA TRANSFORMACIÓN DE MALLAS DE LRBA")
    modificar_xml(args.archivo_xml, args.ambiente, args.modificar_quantitative, args.modificar_domail, args.modificar_odate, jobs_a_modificar)
    
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
        logger.info(f'{jobs_a_modificar}')
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
        modificar_domail_en_on(job, conf, modificar_domail, parent_folder, DOMAIL_SUBJECT, DOMAIL_MESSAGE)
                        
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
        
    # Guarda el XML modificado con el nombre correspondiente
    tree.write(parent_folder+'-generate.xml', encoding="utf-8", xml_declaration=True)
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
    if cmdline and constants.LLNAMESPACE in cmdline:
        index_namespace = cmdline.find(constants.LLNAMESPACE)
        namespace_part = cmdline[index_namespace:]
        if constants.VAR_DEV in namespace_part:
            nuevo_cmdline = cmdline.replace(constants.VAR_DEV, conf["nuevo_cmdline_ambiente"])
            job.set(constants.CMDLINE, nuevo_cmdline)
            incrementar_contador(CONTADORES, constants.CONTADOR_CMDLINE)
            logger.debug(f'CMDLINE modificado de {cmdline} a {nuevo_cmdline}')
            return True
        elif constants.VAR_AU in namespace_part:
            nuevo_cmdline = cmdline.replace(constants.VAR_AU, conf["nuevo_cmdline_ambiente"])
            job.set(constants.CMDLINE, nuevo_cmdline)
            incrementar_contador(CONTADORES, constants.CONTADOR_CMDLINE)
            logger.debug(f'CMDLINE modificado de {cmdline} a {nuevo_cmdline}')
            return True
        elif constants.VAR_QA in namespace_part:
            nuevo_cmdline = cmdline.replace(constants.VAR_QA, conf["nuevo_cmdline_ambiente"])
            job.set(constants.CMDLINE, nuevo_cmdline)
            incrementar_contador(CONTADORES, constants.CONTADOR_CMDLINE)
            logger.debug(f'CMDLINE modificado de {cmdline} a {nuevo_cmdline}')
            return True
        elif constants.VAR_PROD in namespace_part:
            nuevo_cmdline = cmdline.replace(constants.VAR_PROD, conf["nuevo_cmdline_ambiente"])
            job.set(constants.CMDLINE, nuevo_cmdline)
            incrementar_contador(CONTADORES, constants.CONTADOR_CMDLINE)
            logger.debug(f'CMDLINE modificado de {cmdline} a {nuevo_cmdline}')
            return True
        else:
            # Si no está en CMDLINE, buscamos en las etiquetas VARIABLE
            for variable in job.findall(constants.VARIABLE):
                name = variable.get(constants.NAME)
                value = variable.get(constants.VALUE)
                if name in constants.NODO_PERMITIDO_VAR_NAMESPACE and value and constants.VAR_DEV in value:
                    nuevo_value = value.replace(constants.VAR_DEV, conf["nuevo_variable_ambiente"])
                    variable.set(constants.VALUE, nuevo_value)
                    incrementar_contador(CONTADORES, constants.CONTADOR_NAMESPACE)
                    logger.debug(f'VARIABLE modificado de {value} a {nuevo_value}')
                    break
                elif name in constants.NODO_PERMITIDO_VAR_NAMESPACE and value and constants.VAR_AU in value:
                    nuevo_value = value.replace(constants.VAR_AU, conf["nuevo_variable_ambiente"])
                    variable.set(constants.VALUE, nuevo_value)
                    incrementar_contador(CONTADORES, constants.CONTADOR_NAMESPACE)
                    logger.debug(f'VARIABLE modificado de {value} a {nuevo_value}')
                    break
                elif name in constants.NODO_PERMITIDO_VAR_NAMESPACE and value and constants.VAR_QA in value:
                    nuevo_value = value.replace(constants.VAR_QA, conf["nuevo_variable_ambiente"])
                    variable.set(constants.VALUE, nuevo_value)
                    incrementar_contador(CONTADORES, constants.CONTADOR_NAMESPACE)
                    logger.debug(f'VARIABLE modificado de {value} a {nuevo_value}')
                    break
                elif name in constants.NODO_PERMITIDO_VAR_NAMESPACE and value and constants.VAR_PROD in value:
                    nuevo_value = value.replace(constants.VAR_PROD, conf["nuevo_variable_ambiente"])
                    variable.set(constants.VALUE, nuevo_value)
                    incrementar_contador(CONTADORES, constants.CONTADOR_NAMESPACE)
                    logger.debug(f'VARIABLE modificado de {value} a {nuevo_value}')
                    break
            return True    
    return False

# Función para modificar DOMAIL
def modificar_domail_en_on(job, conf, modificar_domail, parent_folder, subject, message):
    logger.info(f'modificar_domail: {modificar_domail} (tipo: {type(modificar_domail)})')
    if modificar_domail:
        for on in job.findall(constants.ON):
            for domail in on.findall(constants.DOMAIL):
                domail.set(constants.VAR_DEST, conf["domail_destino"])
                domail.set(constants.VAR_SUBJECT, subject)
                domail.set(constants.VAR_MESSAGE, message)
                incrementar_contador(CONTADORES, constants.CONTADOR_DOMAIL)
                logger.debug(f'DOMAIL modificado: DEST="{domail.get("DEST")}", SUBJECT="{subject}", MESSAGE="{message}"')

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
        existe_quantitative = job.find(constants.QUANTITATIVE) is not None
        if not existe_quantitative:
            incrementar_contador(CONTADORES, constants.CONTADOR_QUAN)
            nueva_etiqueta = crear_quantitative(ambiente)
            on_tag = job.find(constants.OUTCOND2)
            if on_tag is not None:
                for idx, child in enumerate(job):
                    if child == on_tag:
                        job.insert(idx, nueva_etiqueta)
                        logger.debug(f'Etiqueta QUANTITATIVE añadida antes de la etiqueta ON en JOB con RUN_AS "lrba-ctm": {ET.tostring(nueva_etiqueta).decode()}')
                        return True
            else:
                mensajes.append(f'WARN - El JOB "{job.get("JOBNAME")}" no tiene etiqueta ON.')
                return True
    return False

# Función para crear etiqueta QUANTITATIVE
def crear_quantitative(ambiente):
    if ambiente in constants.AMBIENTES_PREVIOS:
        return ET.Element("QUANTITATIVE", {
            "NAME": "MAX-LRA_BATCH-WORK-CO",
            "QUANT": "1",
            "ONFAIL": "R",
            "ONOK": "R"
        })
    elif ambiente == constants.PRODUCCION:
        return ET.Element("QUANTITATIVE", {
            "NAME": "MAX-LRA_BATCH-LIVE-CO",
            "QUANT": "1",
            "ONFAIL": "R",
            "ONOK": "R"
        })

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
    if "-CO-" in application:
        # Extraer lo que sigue a "-CO-"
        index_co = application.index("-CO-")
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
        logger.warning(f'Total de DOMAIL modificados/agregados: {contadores["domail"]}')    
    if contadores[constants.CONTADOR_ODATE] > 0:
        logger.warning(f'Total de %%ODATE modificados: {contadores["odate"]}')        
    if contadores[constants.CONTADOR_QUAN] > 0:
        logger.warning(f'Total de QUANTITATIVE agregados: {contadores["quan"]}')
        logger.info(f'Para evitar errores en el formato, haz un "enter" después de cada etiqueta generada de QUANTITATIVE (Antes de la etiqueta OUTCOND)')
if __name__ == "__main__":
    main()