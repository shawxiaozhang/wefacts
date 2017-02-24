"""
Utils.
"""

import logging

logging.basicConfig(format='%(pathname)s:%(lineno)d %(message)s',)
logger = logging.getLogger('wefacts')  # pylint: disable=C0103
logger.setLevel(logging.DEBUG)


__version__ = "0.0.1"
