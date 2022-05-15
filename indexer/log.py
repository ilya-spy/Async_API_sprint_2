import logging

import settings

_formatter = logging.Formatter("%(asctime)s: %(levelname)s: %(name)s: %(message)s")

_log_handler = logging.StreamHandler()
_log_handler.setLevel(settings.LOGGING_LEVEL)
_log_handler.setFormatter(_formatter)

logger = logging.getLogger('ETL')
logger.addHandler(_log_handler)
logger.setLevel(settings.LOGGING_LEVEL)
