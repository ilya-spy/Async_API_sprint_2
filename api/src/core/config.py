import logging
from dataclasses import dataclass
from logging import config as logging_config

from core.logger import LOGGING
from core.settings import Settings


@dataclass
class Config:
    """Класс содержит функции начального конфигурирования приложения по настройкам"""
    settings: Settings

    def configure_logging(self):
        logging_config.dictConfig(LOGGING)
        if self.settings.DEBUG:
            logging.info('Enabling debug logging...')
            root = logging.getLogger()
            root.setLevel(logging.DEBUG)

    def __post_init__(self):
        self.configure_logging()


# Инстанциируем настройки окружения
settings = Settings()

# Конфигурируем приложение на основе полученных настроек
config = Config(settings)
