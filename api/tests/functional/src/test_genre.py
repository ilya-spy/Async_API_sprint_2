from logging import Logger

from functional.logger import logger


def test_hello():
    hello_logger: Logger = logger.getChild("HelloTest")
    hello_logger.info("World!")
