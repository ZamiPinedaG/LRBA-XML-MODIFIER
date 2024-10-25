# Prefijos para los ambientes
PREFIJO_COBD_CALIDAD = 'COBQ'
PREFIJO_COBD_PRODUCCION = 'COBP'
PREFIJO_COBD_DESARROLLO = 'COBD'
PREFIJO_DOF_CALIDAD = 'QOF'
PREFIJO_DOF_PRODUCCION = 'GOF'
PREFIJO_DOF_DESARROLLO = 'DOF'

# Etiquetas ambiente
CALIDAD = 'calidad'
PRODUCCION = 'produccion'

# Etiquetas y contadores
CONTADOR_MODIFICACIONES = 'modificaciones'
CONTADOR_NODEID = 'nodeid'
CONTADOR_CMDLINE = 'cmdline'
CONTADOR_NAMESPACE = 'namespace'
CONTADOR_DOMAIL = 'domail'
CONTADOR_ODATE = 'odate'
CONTADOR_QUAN = 'quan'

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
VARD = 'D'
VARC = 'C'
DATAX_CTRLM = "datax-ctrlm"
VAR_LRBA1 = '%%NAMESPACES'
VAR_LRBA2 = '%%namespace'
VAR_DEV = '.dev'
VAR_AU = '.au'
VAR_QA = '.qa'

AMB_PERMITIDO_LRBA = [
    VARC,
    VARD,
    # Puedes agregar más constantes aquí
]

VARS_AMBIENTE = [
    VAR_DEV,
    VAR_AU,
    VAR_QA
    # Puedes agregar más constantes aquí
]

NODO_PERMITIDO_LRBA = [
    LRBA_CO_DESA,
    LRBA_CO_DEV,
    LRBA_CO_QA
    # Puedes agregar más constantes aquí
]

NODO_PERMITIDO_DATAX = [
    DATAX_CTRLM
    # Puedes agregar más constantes aquí
]

NODO_PERMITIDO_VAR_NAMESPACE = [
    VAR_LRBA1,
    VAR_LRBA2
    # Puedes agregar más constantes aquí
]

# Otros
VAR_TO = '-TO-'
VAR_DOBPOINT = '..'
VAR_COXCRX = 'COXCRX_'
VAR_DEST = 'DEST'
VAR_SUBJECT = 'SUBJECT'
VAR_MESSAGE = 'MESSAGE'