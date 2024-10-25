# logger_setup.py
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(log_dir="log", log_file="script.log"):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(stream=sys.stdout, encoding='utf-8')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    handler = RotatingFileHandler(os.path.join(log_dir, log_file), maxBytes=100 * 1024 * 1024, backupCount=5)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
