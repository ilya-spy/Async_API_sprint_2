import asyncio
import logging
from dataclasses import dataclass

from enrichers import BaseEnricher
from loaders import BaseLoader
from producers import BaseProducer
from utils import backoff


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

        self.logger.info('Pipeline Execution started')

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
        try:
            await asyncio.gather(*tasks, return_exceptions=False)
        except Exception as e:
            self.logger.info('Pipeline Execution exception: ' + str(e))

            # release claimed resources (avoid connections storm)
            await self.enricher.release()
            for producer in self.producers:
                await producer.release()
            raise e

        self.logger.info('Pipeline Execution finished')
