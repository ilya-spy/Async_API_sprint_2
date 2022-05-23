import asyncio
import logging
from dataclasses import dataclass

from etl.enrichers import BaseEnricher
from etl.loaders import BaseLoader
from etl.producers import BaseProducer
from etl.utils import backoff


@dataclass
class Pipeline:
    """Связывает все компоненты etl в единый пайплайн загрузки."""

    producers: list[BaseProducer]
    enricher: BaseEnricher
    loader: BaseLoader
    logger: logging.Logger
    producer_queue_size: int

    @backoff()
    async def execute(self):
        producer_queue = asyncio.Queue(maxsize=self.producer_queue_size)
        loader_queue = asyncio.Queue()

        self.logger.debug('Pipeline Execution started')

        tasks = []
        for producer in self.producers:
            tasks.append(asyncio.create_task(
                producer.produce(producer_queue)
            ))

        tasks.append(asyncio.create_task(
            self.enricher.enrich(producer_queue, loader_queue),
        ))
        tasks.append(asyncio.create_task(
            self.loader.load(loader_queue),
        ))

        await asyncio.gather(*tasks)
        self.logger.debug('Pipeline Execution ended')
