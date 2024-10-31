# Prefijos para los ambientes
PREFIJO_COBD_CALIDAD = 'COBQ'
PREFIJO_COBD_PRODUCCION = 'COBP'
PREFIJO_COBD_DESARROLLO = 'COBD'
PREFIJO_DOF_CALIDAD = 'QOF'
PREFIJO_DOF_PRODUCCION = 'GOF'
PREFIJO_DOF_DESARROLLO = 'DOF'

PREFIJOS_COB = [
    PREFIJO_COBD_DESARROLLO,
    PREFIJO_COBD_CALIDAD,
    PREFIJO_COBD_PRODUCCION
]

PREFIJOS_OF = [
    PREFIJO_DOF_DESARROLLO,
    PREFIJO_DOF_CALIDAD,
    PREFIJO_DOF_PRODUCCION
]

# Etiquetas ambiente
DESARROLLO = 'desarrollo'
INT = 'int'
CALIDAD = 'calidad'
AU = 'au'
PRODUCCION = 'produccion'

AMBIENTES_PREVIOS = [
    DESARROLLO,
    INT,
    CALIDAD,
    AU
]

# Etiquetas y contadores
CONTADOR_MODIFICACIONES = 'modificaciones'
CONTADOR_NODEID = 'nodeid'
CONTADOR_CMDLINE = 'cmdline'
CONTADOR_NAMESPACE = 'namespace'
CONTADOR_DOMAIL = 'domail'
CONTADOR_DOMAIL_M = 'domailm'
CONTADOR_ODATE = 'odate'
CONTADOR_QUAN = 'quan'
CONTADOR_QUAN_M = 'quanm'

# Etiquietas Control-M
INCOND = './INCOND'
OUTCOND = './OUTCOND'
OUTCOND2 = './/OUTCOND'
VARIABLE = './/VARIABLE'
JOB = './/JOB'
FOLDER = './/FOLDER'
ON = './/ON'
QUANTITATIVE = './/QUANTITATIVE'
JOBNAME = 'JOBNAME'
ON = 'ON'
RUN_AS = 'RUN_AS'
PARENT_FOLDER = 'PARENT_FOLDER'
NODEID = 'NODEID'
VALUE = 'VALUE'
CMDLINE = 'CMDLINE'
DOMAIL = 'DOMAIL'
APPLICATION = 'APPLICATION'
SUB_APPLICATION = 'SUB_APPLICATION'
NAME = 'NAME'
DATACENTER = 'DATACENTER'
LLNAMESPACE = '--namespace'

# LRBA/DATAX constants
LRBA_CTM = "lrba-ctm"
LRBA_CO_DEV = "LRBA_CO_DEV"
LRBA_CO_DESA = "LRBA_CO_DESA"
LRBA_CO_QA = "LRBA_CO_QA"
LRBA_CO_AU = "LRBA_CO_AU"
LRBA_CO_PROD = "LRBA_CO_PROD"
VARD = 'D'
VARC = 'C'
VARP = 'P'
DATAX_CTRLM = "datax-ctrlm"
DATAX_CTRLMQ = "LCVWCOAXFT01S"
DATAX_CTRLMP = "lcvpcoaxft00"
VAR_LRBA1 = '%%NAMESPACES'
VAR_LRBA2 = '%%namespace'
VAR_DEV = '.dev'
VAR_INT = '.int'
VAR_AU = '.au'
VAR_QA = '.qa'
VAR_PROD = '.pro'

AMB_PERMITIDO_LRBA = [
    VARC,
    VARD,
    VARP
    # Puedes agregar más constantes aquí
]

VARS_AMBIENTE = [
    VAR_DEV,
    VAR_INT,
    VAR_AU,
    VAR_QA,
    VAR_PROD
    # Puedes agregar más constantes aquí
]

NODO_PERMITIDO_LRBA = [
    LRBA_CO_DESA,
    LRBA_CO_DEV,
    LRBA_CO_AU,
    LRBA_CO_QA,
    LRBA_CO_PROD
    # Puedes agregar más constantes aquí
]

NODO_PERMITIDO_DATAX = [
    DATAX_CTRLM,
    DATAX_CTRLMQ,
    DATAX_CTRLMP
    # Puedes agregar más constantes aquí
]

NODO_PERMITIDO_VAR_NAMESPACE = [
    VAR_LRBA1,
    VAR_LRBA2
    # Puedes agregar más constantes aquí
]

# Otros
VAR_TO = '-TO-'
VAR_CO = "-CO-"
VAR_DOBPOINT = '..'
VAR_COXCRX = 'COXCRX_'
VAR_DEST = 'DEST'
VAR_SUBJECT = 'SUBJECT'
VAR_MESSAGE = 'MESSAGE'
VAR_UTF = "utf-8"
VAR_BACK_SLASH = "\n"
VAR_W = "w"
VAR_Y = "Y"
VAR_URGENCY = 'R'
VAR_QUAN_WORK = "MAX-LRA_BATCH-WORK-CO"
VAR_QUAN_LIVE = "MAX-LRA_BATCH-LIVE-CO"
VAR_NUMBER_ONE = "1"
VAR_INDENT = "     "
# Variables help
EJEMPLO_USO_PRODUCCION = """
Ejemplo de ejecución Produccion:
py lrba.py --ambiente produccion --archivo-xml CR-COCBGHDIA-T03.xml --modificar-quantitative --modificar-domail --modificar-odate --modificar-jobs 01,02
"""
EJEMPLO_USO_CALIDAD = """
Ejemplo de ejecución Calidad:
py lrba.py --ambiente calidad --archivo-xml CR-COCBGHDIAC-T03.xml --modificar-quantitative --modificar-domail --modificar-odate --modificar-jobs 01,02
"""
BIENVENIDA = "BIENVENIDO A LA TRANSFORMACIÓN DE MALLAS DE LRBA"
DESCRIPTION = "Script para transformar archivos XML de Control-M a diferentes ambientes."
OPCION_QUAN = "Opción de modificación QUANTITATIVE activada."
OPCION_DOMAIL = "Opción de modificación DOMAIL activada."
OPCION_ODATE = "Opción de modificación ODATE activada."
HELP_AMB = "Especifica el ambiente de destino. Opciones: 'desarrollo', 'int', 'calidad', 'au' o 'produccion'."
HELP_ARC = "Especifica el nombre del archivo XML que se va a modificar (incluye la extensión .xml)."
HELP_QUA = "Modifica o agrega las etiquetas QUANTITATIVE en el archivo XML. Estas etiquetas se usan para controlar recursos y la cantidad de tareas simultáneas permitidas en LRBA."
HELP_DOM = "Modifica o agrega las etiquetas DOMAIL, que suelen indicar la configuración de dominio para un ambiente específico."
HELP_ODA = "Modifica las variables %%ODATE en el archivo XML, que representan fechas operativas, agregando '..' si es necesario."
HELP_JOB = "Modifica solo jobs específicos, proporcionando los últimos dos caracteres de los JOBNAME separados por comas (ej: 01,02,03)"