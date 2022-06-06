import logging

from functional.settings import settings


class TestLogger:
    def __init__(self) -> None:
        logging.basicConfig(
            format="%(asctime)s[%(name)s]: %(message)s",
            level=settings.LOGGING_LEVEL
        )
        self.logger = logging.getLogger("TestLogger")

    def get(self):
        return self.logger


logger: logging.Logger = TestLogger().get()
