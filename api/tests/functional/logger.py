import logging

import settings

logging.basicConfig(
    format="%(asctime)s[%(name)s]: %(message)s",
    level=settings.LOGGING_LEVEL
)
