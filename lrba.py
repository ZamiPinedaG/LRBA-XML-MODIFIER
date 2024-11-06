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
    """
    Incrementa el valor de un contador dependiendo del diccionario dado.
    Parámetros:
    contador_dict (dict): El diccionario que contiene los contadores.
    key (str): La clave del contador que se desea incrementar.
    Si la clave existe en el diccionario, el valor asociado a la clave se incrementa en 1.
    Si la clave no existe, se registra un error en los logs indicando que el contador no fue encontrado.
    Ejemplo:
    >>> contadores = {'modificaciones': 5}
    >>> incrementar_contador(contadores, 'modificaciones')
    >>> contadores['modificaciones']
    6
    """
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
    # Agregar argumento para el modo dry-run
    parser.add_argument('--dry-run', action='store_true', help=constants.HELP_DRY)
    # Parsear los argumentos
    args = parser.parse_args()
    # Extraer la lista de jobs a modificar si se especifica el argumento
    if args.modificar_jobs:
        jobs_a_modificar = args.modificar_jobs.split(',')
        # Asegurar que cada job tenga dos dígitos
        jobs_a_modificar = [job.zfill(3) for job in jobs_a_modificar]
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
    if args.dry_run:
        logger.info(constants.OPCION_DRY)    
        
    modificar_xml(
        args.archivo_xml,
        args.ambiente,
        args.modificar_quantitative,
        args.modificar_domail,
        args.modificar_odate,
        jobs_a_modificar,
        args.dry_run
    )
    
def modificar_xml(archivo_xml, ambiente, modificar_quan, modificar_domail, modificar_odate, jobs_a_modificar, dry_run):
    """
    Modifica un archivo XML de configuración de trabajos (jobs) según el ambiente especificado y parámetros dados.
    Parámetros:
    archivo_xml (str): Ruta al archivo XML a modificar.
    ambiente (str): El ambiente (e.g., 'dev', 'prod') que determina cómo se realizarán las modificaciones.
    modificar_quan (bool): Flag para modificar la etiqueta 'QUANTITATIVE'.
    modificar_domail (bool): Flag para modificar las etiquetas 'DOMAIL'.
    modificar_odate (bool): Flag para modificar la etiqueta 'ODATE'.
    jobs_a_modificar (list): Lista de sufijos de JOBNAME que deben ser modificados. Si es None, se modifican todos.
    dry_run (bool): Si es True, realiza una simulación sin guardar los cambios reales en el archivo.
    El proceso de modificación de la configuración incluye:
    - Cambiar los valores de JOBNAME, CMDLINE, NODEID, INCOND, OUTCOND, entre otros, según el ambiente.
    - Si dry_run es False, guarda el archivo modificado con un nuevo nombre.
    - Si dry_run es True, guarda una simulación del archivo modificado.
    """
    # Carga el archivo XML y obtiene su raíz.    
    tree, root = cargar_xml(archivo_xml)
    if root is None:
        return # Si no se pudo cargar el archivo XML, retorna inmediatamente.
    
    # Selecciona la configuración correspondiente al ambiente dado.
    conf = seleccionar_configuracion(ambiente)
    # Inicializa la modificación de la carpeta del datacenter.
    modificar_folder(root, conf["nuevo_datacenter"])
    # Recorre todos los elementos JOB en el archivo XML.
    for job in root.findall(constants.JOB):
        jobname = job.get(constants.JOBNAME)
        run_as = job.get(constants.RUN_AS)
        parent_folder = job.get(constants.PARENT_FOLDER)
        application = job.get(constants.APPLICATION)
        sub_application = job.get(constants.SUB_APPLICATION)
        # Definición de los patrones de correo para la etiqueta DOMAIL.
        DOMAIL_SUBJECT = 'Error %%JOBNAME - %%$ODATE M malla ' + parent_folder
        DOMAIL_MESSAGE = '0051Error %%JOBNAME - %%$ODATE M malla ' + parent_folder
        # Si se proporcionó una lista de jobs específicos, filtrar por los últimos tres caracteres de JOBNAME
        if jobs_a_modificar and jobname[-3:] not in jobs_a_modificar:
            continue
        # Modifica el JOBNAME según la configuración del ambiente.
        nuevo_jobname = modificar_jobname(jobname, conf["letra_cambio"], PREFIJOS_GRANDES, PREFIJOS_PEQUENOS, constants.AMB_PERMITIDO_LRBA)
        if nuevo_jobname != jobname:
            job.set(constants.JOBNAME, nuevo_jobname)
            incrementar_contador(CONTADORES, constants.CONTADOR_MODIFICACIONES)
            logger.debug(f'JOBNAME modificado de "{jobname}" a "{nuevo_jobname}"')
        # Modifica NODEID según la configuración del ambiente.
        modificar_nodeid(job, conf)
        # Modifica CMDLINE (por ejemplo, cambiar .dev por .au o .prod según el ambiente).
        modificar_cmdline(job, conf)
        # Modifica la etiqueta ON y sus subetiquetas DOMAIL si se requiere.
        modificar_domail_en_on(job, conf, ambiente, modificar_domail, parent_folder, DOMAIL_SUBJECT, DOMAIL_MESSAGE)             
        # Modifica las condiciones de entrada (INCOND) según la configuración.
        inconds = job.findall(constants.INCOND)
        modificar_condiciones(inconds, conf["letra_cambio"], conf["nuevo_condicion"], '|'.join(PREFIJOS_GRANDES), '|'.join(PREFIJOS_PEQUENOS))
        # Modifica las condiciones de salida (OUTCOND) según la configuración.
        outconds = job.findall(constants.OUTCOND)
        modificar_condiciones(outconds, conf["letra_cambio"], conf["nuevo_condicion"], '|'.join(PREFIJOS_GRANDES), '|'.join(PREFIJOS_PEQUENOS))
        # Si RUN_AS es "lrba-ctm", se modifica la etiqueta QUANTITATIVE.
        modificar_quantitative(job, conf, ambiente, modificar_quan)
        # Modificar SUB_APPLICATION
        procesar_application(job, conf, CONTADORES)
    # Modifica las variables globales en el archivo XML.
    for variable in root.findall(constants.VARIABLE):
        modificar_variable(variable, ambiente, modificar_odate, CONTADORES)
    # Si es una simulación (dry_run), guarda el archivo modificado con un sufijo "-generate".    
    if dry_run:    
        xml_str = ET.tostring(root, constants.VAR_UTF)
        parsed_string = MD.parseString(xml_str)
        pretty_xml_as_string = parsed_string.toprettyxml(indent=constants.VAR_INDENT, encoding=constants.VAR_UTF).decode(constants.VAR_UTF)
        pretty_xml_as_string = constants.VAR_BACK_SLASH.join([line for line in pretty_xml_as_string.splitlines() if line.strip()])
        with open(parent_folder+'-generate.xml', constants.VAR_W, encoding=constants.VAR_UTF) as f:
                f.write(pretty_xml_as_string)    
        #tree.write(parent_folder+'-generate.xml', encoding="utf-8", xml_declaration=True)
        logger.info(f'Archivo modificado guardado como {parent_folder}-generate.xml')
    else:
        # Si no es una simulación, guarda el archivo modificado con un nuevo nombre.
        new_parent_folder = re.sub(r"-(?=[^-]*$)", f"{conf['malla_letra_cambio']}-", parent_folder)
        xml_str = ET.tostring(root, constants.VAR_UTF)
        parsed_string = MD.parseString(xml_str)
        pretty_xml_as_string = parsed_string.toprettyxml(indent=constants.VAR_INDENT, encoding=constants.VAR_UTF).decode(constants.VAR_UTF)
        pretty_xml_as_string = constants.VAR_BACK_SLASH.join([line for line in pretty_xml_as_string.splitlines() if line.strip()])
        with open(new_parent_folder + constants.VAR_XML_EXT, constants.VAR_W, encoding=constants.VAR_UTF) as f:
                f.write(pretty_xml_as_string)
        logger.info(f'Archivo modificado guardado como {new_parent_folder}.xml')
    
    # Imprime los mensajes acumulados al final
    for mensaje in mensajes:
        logger.info(f'mensaje')
    # Muestra la cantidad de JOBNAME modificados
    registrar_modificaciones(CONTADORES)

def modificar_jobname(jobname, letra_cambio, prefijos_grandes, prefijos_pequenos, amb_permitido):
    # Compilar los patrones de expresiones regulares para los prefijos grandes y pequeños.
    # Estos patrones se usarán para verificar si el jobname comienza con uno de los prefijos especificados.
    patron_prefijos_grandes = re.compile(r'^(' + '|'.join(prefijos_grandes) + r').*')
    patron_prefijos_pequenos = re.compile(r'^(' + '|'.join(prefijos_pequenos) + r').*')
    # Definimos una función interna para modificar el JOBNAME si está permitido.
    def modificar_si_permitido(posicion):
        # Si la longitud del jobname es suficiente y la letra en la posición dada está en amb_permitido,
        # se modifica el jobname en esa posición reemplazándola con letra_cambio.
        if len(jobname) > posicion and jobname[posicion] in amb_permitido:
            nuevo_jobname = jobname[:posicion] + letra_cambio + jobname[posicion+1:]
            logger.info(f"JOBNAME modificado en posición {posicion}: '{nuevo_jobname}'")
            return nuevo_jobname
        return None # Si no se cumple la condición, no se modifica el jobname.
    logger.info(f"Modificando JOBNAME: '{jobname}'")
    # Si el jobname comienza con uno de los prefijos grandes, intentamos modificarlo en las posiciones 6 o 7.
    if patron_prefijos_grandes.match(jobname):
        return modificar_si_permitido(6) or modificar_si_permitido(7) or jobname
    # Si el jobname comienza con uno de los prefijos pequeños, intentamos modificarlo en la posición 5.
    elif patron_prefijos_pequenos.match(jobname):
        return modificar_si_permitido(5) or jobname
    # Si no se cumple ninguna de las condiciones anteriores, se devuelve el jobname original sin cambios.
    return jobname

# Función para cargar el XML
def cargar_xml(archivo_xml):
    try:
        # Intentamos parsear el archivo XML utilizando ElementTree (ET).
        # 'ET.parse' carga el archivo XML y lo convierte en un árbol de elementos.
        tree = ET.parse(archivo_xml)
        # Devuelve el árbol de elementos (tree) y la raíz del XML (getroot())
        return tree, tree.getroot()
    except ET.ParseError as e:
        # Si ocurre un error al parsear el archivo (archivo mal formado o no válido),
        # se captura el error y se registra en el log.
        logger.error(f"Error al parsear el archivo XML: {e}")
        # Retorna None para ambos valores si hubo un error al parsear.
        return None, None
    except FileNotFoundError as e:
        # Si el archivo no se encuentra en la ruta especificada, se captura el error
        # y se registra en el log.
        logger.error(f"Archivo XML no encontrado: {e}")
        # Retorna None para ambos valores si el archivo no fue encontrado.
        return None, None
    
# Función para seleccionar configuración según ambiente
def seleccionar_configuracion(ambiente):
    """
    Selecciona y retorna la configuración correspondiente al ambiente proporcionado.
    Parámetros:
    ambiente (str): El nombre del ambiente (e.g., 'calidad', 'desarrollo', etc.).
    Retorna:
    dict: La configuración correspondiente al ambiente.
    Si el ambiente no se encuentra en las opciones definidas, retorna la configuración por defecto (CONFIGURACION_AU).
    """    
    # Diccionario que mapea ambientes a configuraciones
    configuraciones = {
        AMBIENTE_CALIDAD: CONFIGURACION_CALIDAD,
        AMBIENTE_DESARROLLO: CONFIGURACION_DESARROLLO,
        AMBIENTE_PRODUCCION: CONFIGURACION_PRODUCCION,
        AMBIENTE_INT: CONFIGURACION_INT
    }
    # Retorna la configuración correspondiente al ambiente, o la configuración por defecto (CONFIGURACION_AU) si no se encuentra el ambiente.
    return configuraciones.get(ambiente, CONFIGURACION_AU)   

# Función para modificar el folder
def modificar_folder(root, nuevo_datacenter):
    """
    Modifica el valor de la etiqueta 'DATACENTER' dentro del 'FOLDER' en el XML.
    Parámetros:
    root (Element): El nodo raíz del XML donde se encuentra el 'FOLDER'.
    nuevo_datacenter (str): El nuevo valor para el atributo 'DATACENTER' dentro del 'FOLDER'.
    Esta función busca la etiqueta 'FOLDER' dentro del XML y, si existe, actualiza su atributo 'DATACENTER'
    con el valor proporcionado en 'nuevo_datacenter'. Luego, registra un mensaje de depuración indicando el cambio.
    """    
    # Buscar el nodo 'FOLDER' en el árbol XML    
    folder = root.find(constants.FOLDER)
    # Verificar si se encontró el nodo 'FOLDER'
    if folder is not None:
        # Modificar el atributo 'DATACENTER' del nodo 'FOLDER' con el nuevo valor
        folder.set(constants.DATACENTER, nuevo_datacenter)
        logger.debug(f'FOLDER modificado: DATACENTER="{nuevo_datacenter}"')

# Función para modificar NODEID
def modificar_nodeid(job, conf):
    """
    Modifica el valor de la etiqueta 'NODEID' en un job dependiendo de su valor actual y el entorno de configuración.
    Parámetros:
    job (Element): El nodo que contiene la información del job en el XML.
    conf (dict): Un diccionario con las configuraciones necesarias para determinar el nuevo valor de NODEID.
    Retorna:
    bool: Devuelve True si se realizó la modificación del NODEID, False en caso contrario.
    La función verifica el valor actual de 'NODEID' y, si se encuentra en los nodos permitidos, lo actualiza
    con el nuevo valor de acuerdo con la configuración proporcionada.
    """    
    nodeid = job.get(constants.NODEID)
    # Verificar si el NODEID está en los nodos permitidos para Datax
    if nodeid and nodeid in constants.NODO_PERMITIDO_DATAX:
        # Modificar NODEID con el valor correspondiente en la configuración
        job.set(constants.NODEID, conf["nuevo_nodeid"])
        incrementar_contador(CONTADORES, constants.CONTADOR_NODEID)
        logger.debug(f'NODEID modificado de {nodeid} a {conf["nuevo_nodeid"]}')
        return True
    # Verificar si el NODEID está en los nodos permitidos para LRBA
    elif nodeid in constants.NODO_PERMITIDO_LRBA:
        # Modificar NODEID con el valor para LRBA
        job.set(constants.NODEID, conf["nuevo_nodeidlrba"])
        incrementar_contador(CONTADORES, constants.CONTADOR_NODEID)
        logger.debug(f'NODEID modificado de {nodeid} a {conf["nuevo_nodeidlrba"]}')
        return True
    # Si el NODEID no está en ninguno de los nodos permitidos, registrar una advertencia
    else:
        logger.warn(f"No se modifico el NODEID por no cumplir con los nodos permitidos.")
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
        elif ambiente == constants.AU:
            nuevo_value = constants.PREFIJO_COBD_CALIDAD + value[4:]  # Cambia COB
        elif ambiente == constants.INT:
            nuevo_value = constants.PREFIJO_COBD_DESARROLLO + value[4:]  # Cambia COB                        
        elif ambiente == constants.PRODUCCION:
            nuevo_value = constants.PREFIJO_COBD_PRODUCCION + value[4:]  # Cambia COB

    elif value.startswith(tuple(constants.PREFIJOS_OF)):
        # Cambia el prefijo en calidad y producción
        if ambiente == constants.DESARROLLO:
            nuevo_value = constants.PREFIJO_DOF_DESARROLLO + value[3:]
        elif ambiente == constants.CALIDAD:
            nuevo_value = constants.PREFIJO_DOF_CALIDAD + value[3:]  # Cambia OF
        elif ambiente == constants.AU:
            nuevo_value = constants.PREFIJO_DOF_CALIDAD + value[4:]  # Cambia COB
        elif ambiente == constants.INT:
            nuevo_value = constants.PREFIJO_DOF_DESARROLLO + value[4:]  # Cambia COB         
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

def procesar_application(job, conf, contadores):
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
        incrementar_contador(contadores, constants.CONTADOR_SUBAPP)
        logger.debug(f'SUB_APPLICATION modificado a "{sub_application_value}" para job {job.get(constants.JOBNAME)}')
    else:
        logger.debug(f'SUB_APPLICATION no modificado para job {job.get(constants.JOBNAME)} ya que no contiene "-CO-"')

def registrar_modificaciones(contadores):
    # Lista de registros para las modificaciones
    if contadores[constants.CONTADOR_MODIFICACIONES] > 0:
        logger.warning(f'Total de JOBNAME modificados: {contadores["modificaciones"]}')
    if contadores[constants.CONTADOR_NODEID] > 0:
        logger.warning(f'Total de NODEID modificados: {contadores["nodeid"]}')
    if contadores[constants.CONTADOR_SUBAPP] > 0:
        logger.warning(f'Total de SUB_APPLICATION modificados: {contadores["subapp"]}')
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