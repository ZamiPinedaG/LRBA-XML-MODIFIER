# logger_setup.py
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(log_dir="log", log_file="script.log", incidencias_file="incidencias.log"):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(stream=sys.stdout, encoding='utf-8')
    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)

    # Handler para el log principal
    main_handler = RotatingFileHandler(os.path.join(log_dir, log_file), maxBytes=100 * 1024 * 1024, backupCount=5)
    main_handler.setLevel(logging.DEBUG)
    main_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main_handler.setFormatter(main_formatter)
    logger.addHandler(main_handler)

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(main_formatter)
    logger.addHandler(console_handler)

    # Logger específico para incidencias
    incidencias_logger = logging.getLogger("incidencias_logger")
    incidencias_logger.setLevel(logging.WARNING)  # Solo registrar advertencias y errores críticos

    # Handler para el log de incidencias
    incidencias_handler = RotatingFileHandler(os.path.join(log_dir, incidencias_file), maxBytes=50 * 1024 * 1024, backupCount=3)
    incidencias_formatter = logging.Formatter('%(asctime)s - %(message)s')
    incidencias_handler.setFormatter(incidencias_formatter)
    incidencias_logger.addHandler(incidencias_handler)

    return logger, incidencias_logger
