import logging
from dataclasses import dataclass, field
from logging import config as logging_config

from core.logger import LOGGING
from core.settings import Settings


@dataclass
class Config:
    """Класс содержит функции начального конфигурирования приложения по настройкам"""
    settings: Settings
    postgres_dsn: dict = field(default=None)

    def configure_logging(self):
        logging_config.dictConfig(LOGGING)
        if self.settings.DEBUG:
            logging.info('Enabling debug logging...')
            root = logging.getLogger()
            root.setLevel(logging.DEBUG)

    def configure_postgres(self):
        self.postgres_dsn = dict(
            database=self.settings.DB_NAME,
            user=self.settings.DB_USER,
            password=self.settings.DB_PASSWORD,
            host=self.settings.DB_HOST,
            port=self.settings.DB_PORT,
            server_settings=dict(
                search_path=f'public,{self.settings.DB_SCHEMA}',
            ),
        )

    def __post_init__(self):
        self.configure_logging()
        self.configure_postgres()


# Инстанциируем настройки окружения
settings = Settings()

# Конфигурируем приложение на основе полученных настроек
config = Config(settings)
