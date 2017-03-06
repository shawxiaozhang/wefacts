"""
Utils.
"""

import logging

logger = logging.getLogger('wefacts')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(pathname)s %(lineno)d %(message)s')
file_handler = logging.FileHandler('../raw/wefacts.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)

__version__ = "0.0.1"
