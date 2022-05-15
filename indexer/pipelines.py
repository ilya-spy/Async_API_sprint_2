import logging
from dataclasses import dataclass
from datetime import datetime, timezone

import enrichers
import loaders
import producers
import states
import transformers
from utils import backoff


@dataclass
class Pipeline:
    """Связывает все компоненты etl в единый пайплайн загрузки."""

    name: str
    state: states.State
    producer: producers.Base
    enricher: enrichers.Base
    transformer: transformers.Base
    loader: loaders.Base
    logger: logging.Logger

    def __post_init__(self):
        self.logger = self.logger.getChild(self.name)

    @property
    def last_modified(self) -> datetime:
        """Возвращает дату последнего изменения из хранилища состояний.

        Если не найдена, то вернет 0001-01-01 00:00:00.

        :return:
        """
        modified = self.state.retrieve_state(self.name)
        return datetime.fromisoformat(modified) if modified else datetime.min.replace(tzinfo=timezone.utc)

    @last_modified.setter
    def last_modified(self, modified: datetime):
        """Запоминает дату последнего изменения, полученную из бд.

        :param modified:
        :return:
        """
        self.state.save_state(self.name, modified.isoformat())

    @backoff()
    def execute(self):
        """Выполняет загрузку данных из pg в elastic."""
        num = 1
        total_loaded = 0

        self.logger.debug('Execution started')
        self.logger.debug(f'Last modified from state: {self.last_modified}')
        chunks = self.producer.produce(self.last_modified)
        for chunk in chunks:
            self.logger.debug(f'#{num}: Chunk size: {len(chunk)}')

            items = self.enricher.enrich([item_id for item_id, _ in chunk])
            self.logger.debug(f'#{num}: Unique items enriched: {len(items)}')

            loaded = self.loader.load(self.transformer.transform(items))
            self.logger.debug(f'#{num}: Items loaded: {loaded}')

            new_last_modified = max([modified for _, modified in chunk])
            if new_last_modified > self.last_modified:
                self.last_modified = max(self.last_modified, new_last_modified)

            total_loaded += loaded
            num += 1

        self.logger.info(f'Total loaded: {total_loaded}')
        self.logger.debug('Execution ended')
