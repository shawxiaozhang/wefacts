"""
Utils.
"""

import logging

DIR_LOCAL = '../local/'
DIR_RAW = '../raw/'
DIR_RESULT = '../result/'

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(pathname)s %(lineno)d %(levelname)s %(message)s')
file_handler = logging.FileHandler('wefacts.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)

__version__ = "0.1.4"
