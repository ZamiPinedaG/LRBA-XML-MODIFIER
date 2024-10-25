# config.py
AMBIENTE_CALIDAD = "calidad"
AMBIENTE_PRODUCCION = "produccion"

CONFIGURACION_CALIDAD = {
    "letra_cambio": 'C',
    "nuevo_nodeid": 'LCVWCOAXFT01S',
    "nuevo_nodeidlrba": 'LRBA_CO_QA',
    "nuevo_cmdline_ambiente": '.au',
    "nuevo_variable_ambiente": '.au',
    "nuevo_datacenter": 'Ctrlm_Desarrollo',
    "output_file": 'output_quality.xml',
    "nuevo_condicion": 'Q',
    "domail_destino": 'lraco.group@bbva.com',
    "sub_app_ctrlm": '-CCR'
}

CONFIGURACION_PRODUCCION = {
    "letra_cambio": 'P',
    "nuevo_nodeid": 'lcvpcoaxft00',
    "nuevo_nodeidlrba": 'LRBA_CO_PROD',
    "nuevo_cmdline_ambiente": '.pro',
    "nuevo_variable_ambiente": '.pro',
    "nuevo_datacenter": 'CTM_CTRLMCCR',
    "output_file": 'output_prod.xml',
    "nuevo_condicion": 'P',
    "domail_destino": 'monitoreo.colombia@bbva.com',
    "sub_app_ctrlm": '-CCR'
}

# Inicializar los contadores en un diccionario
CONTADORES = {
    'modificaciones': 0,
    'nodeid': 0,
    'cmdline': 0,
    'namespace': 0,
    'domail': 0,
    'odate': 0,
    'quan': 0,
}

PREFIJOS_GRANDES = ['CCUGH', 'CCBTQ', 'CCBGH', 'CCBGU', 'CCTSU', 'CCMOL', 'CCPAN', 'CCZXH', 'CCBNT']
PREFIJOS_PEQUENOS = ['CBTQ', 'CCOG']

AMBIENTES = ["calidad", "produccion"]

PATRON_PREFIJOS_GRANDES = '|'.join(PREFIJOS_GRANDES)
PATRON_PREFIJOS_PEQUENOS = '|'.join(PREFIJOS_PEQUENOS)
