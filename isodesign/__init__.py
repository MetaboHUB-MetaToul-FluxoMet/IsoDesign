import logging 


logger = logging.getLogger("IsoDesign")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s: Method %(funcName)s: %(message)s"))

logger.addHandler(handler)
