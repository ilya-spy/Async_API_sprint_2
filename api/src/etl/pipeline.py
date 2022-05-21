import asyncio
from asyncio import AbstractEventLoop
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

from etl.enrichers import BaseEnricher
from etl.loaders import BaseLoader
from etl.producers import BaseProducer


@dataclass
class Pipeline:
    """Связывает все компоненты etl в единый пайплайн загрузки."""

    producers: list[BaseProducer]
    enricher: BaseEnricher
    loader: BaseLoader
    chunk_size: int

    async def execute(self, loop: AbstractEventLoop, pool: ProcessPoolExecutor):
        producer_queue = asyncio.Queue(maxsize=self.chunk_size)
        loader_queue = asyncio.Queue()

        tasks = []
        for producer in self.producers:
            tasks.append(asyncio.create_task(
                producer.produce(producer_queue)
            ))

        tasks.append(asyncio.create_task(
            self.enricher.enrich(producer_queue, loader_queue),
        ))
        tasks.append(asyncio.create_task(
            self.loader.load(loop, pool, loader_queue),
        ))

        await asyncio.gather(*tasks)
