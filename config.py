# config.py
AMBIENTE_DESARROLLO = "dev"
AMBIENTE_INT = "int"
AMBIENTE_CALIDAD = "qa"
AMBIENTE_AU = "au"
AMBIENTE_PRODUCCION = "pro"

CONFIGURACION_DESARROLLO = {
    "letra_cambio": 'D',
    "malla_letra_cambio": 'D',
    "nuevo_nodeid": 'datax-ctrlm',
    "nuevo_nodeidlrba": 'LRBA_CO_DESA',
    "nuevo_cmdline_ambiente": '.dev',
    "nuevo_variable_ambiente": '.dev',
    "nuevo_datacenter": 'Ctrlm_Desarrollo',
    "nuevo_condicion": 'D',
    "domail_destino": '', # En desarrollo poner su correo para pruebas
    "sub_app_ctrlm": '-CCR'
}

CONFIGURACION_INT = {
    "letra_cambio": 'D',
    "malla_letra_cambio": 'D',
    "nuevo_nodeid": 'datax-ctrlm',
    "nuevo_nodeidlrba": 'LRBA_CO_DESA',
    "nuevo_cmdline_ambiente": '.int',
    "nuevo_variable_ambiente": '.int',
    "nuevo_datacenter": 'Ctrlm_Desarrollo',
    "nuevo_condicion": 'D',
    "domail_destino": '', # En desarrollo poner su correo para pruebas
    "sub_app_ctrlm": '-CCR'
}

CONFIGURACION_AU = {
    "letra_cambio": 'C',
    "malla_letra_cambio": 'C',
    "nuevo_nodeid": 'LCVWCOAXFT01S',
    "nuevo_nodeidlrba": 'LRBA_CO_QA',
    "nuevo_cmdline_ambiente": '.au',
    "nuevo_variable_ambiente": '.au',
    "nuevo_datacenter": 'Ctrlm_Desarrollo',
    "nuevo_condicion": 'Q',
    "domail_destino": 'lraco.group@bbva.com',
    "sub_app_ctrlm": '-CCR'
}

CONFIGURACION_CALIDAD = {
    "letra_cambio": 'C',
    "malla_letra_cambio": 'C',
    "nuevo_nodeid": 'LCVWCOAXFT01S',
    "nuevo_nodeidlrba": 'LRBA_CO_QA',
    "nuevo_cmdline_ambiente": '.qa',
    "nuevo_variable_ambiente": '.qa',
    "nuevo_datacenter": 'Ctrlm_Desarrollo',
    "nuevo_condicion": 'Q',
    "domail_destino": 'lraco.group@bbva.com',
    "sub_app_ctrlm": '-CCR'
}

CONFIGURACION_PRODUCCION = {
    "letra_cambio": 'P',
    "malla_letra_cambio": 'D',
    "nuevo_nodeid": 'lcvpcoaxft00',
    "nuevo_nodeidlrba": 'LRBA_CO_PROD',
    "nuevo_cmdline_ambiente": '.pro',
    "nuevo_variable_ambiente": '.pro',
    "nuevo_datacenter": 'CTM_CTRLMCCR',
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
    'domailm': 0,
    'odate': 0,
    'quan': 0,
    'quanm': 0,
    'subapp': 0,
}

PREFIJOS_GRANDES = ['CCUGH', 'CCBTQ', 'CCBGH', 'CCBGU', 'CCTSU', 'CCMOL', 'CCPAN', 'CCZXH', 'CCBNT', 'CCDNG', 'CMS01']
PREFIJOS_PEQUENOS = ['CBTQ', 'CCOG']

AMBIENTES = ["dev", "int", "qa", "au", "pro"]

PATRON_PREFIJOS_GRANDES = '|'.join(PREFIJOS_GRANDES)
PATRON_PREFIJOS_PEQUENOS = '|'.join(PREFIJOS_PEQUENOS)
