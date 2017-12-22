import logging

logger = logging.getLogger('bot_logger')
logger.setLevel(logging.DEBUG)
ch = logging.FileHandler("error.log")
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s](%(filename)s) - %(levelname)s - %(message)s',
                              '%m/%d/%Y %I:%M:%S %p')
ch.setFormatter(formatter)
logger.addHandler(ch)
