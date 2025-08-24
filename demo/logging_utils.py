import logging
import os

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logger = logging.getLogger("herag")
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(getattr(logging, log_level, logging.INFO))
logger.propagate = False
