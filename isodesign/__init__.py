import logging 

logging.basicConfig(format=" %(levelname)s:%(name)s: Method %(funcName)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)