import logging


def test_hello():
    logger = logging.getLogger("Hello")
    logger.info("World!")
