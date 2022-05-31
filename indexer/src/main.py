import asyncio
import logging
import os
import signal
from dataclasses import dataclass

import aioredis
from elasticsearch import AsyncElasticsearch

import state
from core import config
from db import elastic, postgres, redis
from enrichers import FilmEnricher, GenreEnricher, PersonEnricher
from loaders import ElasticIndexLoader
from pipeline import Pipeline
from producers import (FilmworkGenreModifiedProducer, FilmworkModifiedProducer,
                       FilmworkPersonModifiedProducer, GenreModifiedProducer,
                       PersonModifiedProducer)
from transformers import FilmTransformer, GenreTransformer, PersonTransformer


@dataclass
class App:
    """Запускает обреботку пайплайнов.
    Обеспечивает корректное завершение при получении сигналов SIGINT и SIGTERM."""
    pipelines_builders: list[callable]
    _stopped: bool = False

    @staticmethod
    def startup():
        redis.redis = aioredis.from_url(
            f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}')
        elastic.es = AsyncElasticsearch(
            hosts=[f'{config.ELASTIC_SCHEME}://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'])
        postgres.postgres = postgres.DB(dsn=config.PG_DSN)

    @staticmethod
    async def shutdown(sig, loop: asyncio.AbstractEventLoop):
        """Cleanup tasks tied to the service's shutdown."""
        logging.info(f'Received exit signal {sig.name}...')
        logging.info('Closing database connections')
        logging.info('Nacking outstanding messages')
        tasks = [t for t in asyncio.all_tasks()
                 if t is not asyncio.current_task()]

        for task in tasks:
            task.cancel()

        logging.info(f'Cancelling {len(tasks)} outstanding tasks')
        await asyncio.gather(*tasks)
        logging.info('Flushing metrics')
        loop.stop()

    async def run(self):
        """Запускает пайплайны."""
        self.startup()

        loop = asyncio.get_running_loop()

        if os.name != 'nt':
            signals = (signal.SIGTERM, signal.SIGINT)
            for s in signals:
                loop.add_signal_handler(
                    s, lambda s=s: asyncio.create_task(self.shutdown(s, loop)))

        tasks = []
        for build_pipeline in self.pipelines_builders:
            pipe = await build_pipeline()
            task = loop.create_task(pipe.execute())
            tasks.append(task)

        try:
            await asyncio.gather(*tasks, return_exceptions=False)
        finally:
            await self.shutdown(signal.SIGINT, loop)


async def build_genre_index_pipeline() -> Pipeline:
    logger = logging.getLogger().getChild('GenreIndexPipeline')

    storage = state.RedisStorage(redis=await redis.get_redis(), name='genre_index_pipeline')
    state_obj = state.State(storage)

    enricher = GenreEnricher(
        db=await postgres.get_postgres(),
        logger=logger.getChild('GenreModifiedEnricher'),
        chunk_size=config.ETL_ENRICHER_CHUNK_SIZE,
    )
    loader = ElasticIndexLoader(
        elastic=await elastic.get_elastic(),
        transformer=GenreTransformer(),
        index_name='genres',
        state=state_obj,
        logger=logger.getChild('GenreModifiedLoader'),
        chunk_size=config.ETL_LOADER_CHUNK_SIZE,
    )
    return Pipeline(
        producer_queue_size=config.ETL_PRODUCER_QUEUE_SIZE,
        producers=[
            GenreModifiedProducer(
                db=await postgres.get_postgres(),
                state=state_obj,
                logger=logger.getChild('GenreModifiedProducer'),
                chunk_size=config.ETL_PRODUCER_CHUNK_SIZE,
                check_interval=config.ETL_PRODUCER_CHECK_INTERVAL,
            ),
        ],
        enricher=enricher,
        loader=loader,
        logger=logger,
    )


async def build_person_index_pipeline() -> Pipeline:
    logger = logging.getLogger().getChild('PersonIndexPipeline')

    storage = state.RedisStorage(redis=await redis.get_redis(), name='person_index_pipeline')
    state_obj = state.State(storage)

    enricher = PersonEnricher(
        db=await postgres.get_postgres(),
        logger=logger.getChild('PersonModifiedEnricher'),
        chunk_size=config.ETL_ENRICHER_CHUNK_SIZE,
    )
    loader = ElasticIndexLoader(
        elastic=await elastic.get_elastic(),
        transformer=PersonTransformer(),
        index_name='persons',
        state=state_obj,
        logger=logger.getChild('PersonModifiedLoader'),
        chunk_size=config.ETL_LOADER_CHUNK_SIZE,
    )
    return Pipeline(
        producer_queue_size=config.ETL_PRODUCER_QUEUE_SIZE,
        producers=[
            PersonModifiedProducer(
                db=await postgres.get_postgres(),
                state=state_obj,
                logger=logger.getChild('PersonModifiedProducer'),
                chunk_size=config.ETL_PRODUCER_CHUNK_SIZE,
                check_interval=config.ETL_PRODUCER_CHECK_INTERVAL,
            ),
        ],
        enricher=enricher,
        loader=loader,
        logger=logger,
    )


async def build_film_index_pipeline() -> Pipeline:
    logger = logging.getLogger().getChild('FilmIndexPipeline')

    storage = state.RedisStorage(redis=await redis.get_redis(), name='film_index_pipeline')
    state_obj = state.State(storage)

    enricher = FilmEnricher(
        db=await postgres.get_postgres(),
        logger=logger.getChild('FilmworkEnricher'),
        chunk_size=config.ETL_ENRICHER_CHUNK_SIZE,
    )
    loader = ElasticIndexLoader(
        elastic=await elastic.get_elastic(),
        transformer=FilmTransformer(),
        index_name='films',
        state=state_obj,
        logger=logger.getChild('FilmworkLoader'),
        chunk_size=config.ETL_LOADER_CHUNK_SIZE,
    )
    return Pipeline(
        producer_queue_size=config.ETL_PRODUCER_QUEUE_SIZE,
        producers=[
            FilmworkPersonModifiedProducer(
                db=await postgres.get_postgres(),
                state=state_obj,
                logger=logger.getChild('FilmworkPersonModifiedProducer'),
                chunk_size=config.ETL_PRODUCER_CHUNK_SIZE,
                check_interval=config.ETL_PRODUCER_CHECK_INTERVAL,
            ),
            FilmworkGenreModifiedProducer(
                db=await postgres.get_postgres(),
                state=state_obj,
                logger=logger.getChild('FilmworkGenreModifiedProducer'),
                chunk_size=config.ETL_PRODUCER_CHUNK_SIZE,
                check_interval=config.ETL_PRODUCER_CHECK_INTERVAL,
            ),
            FilmworkModifiedProducer(
                db=await postgres.get_postgres(),
                state=state_obj,
                logger=logger.getChild('FilmworkModifiedProducer'),
                chunk_size=config.ETL_PRODUCER_CHUNK_SIZE,
                check_interval=config.ETL_PRODUCER_CHECK_INTERVAL,
            ),
        ],
        enricher=enricher,
        loader=loader,
        logger=logger,
    )


def indexer():
    pipelines_builders = [
        build_film_index_pipeline,
        build_genre_index_pipeline,
        build_person_index_pipeline,
    ]

    app = App(pipelines_builders=pipelines_builders)
    asyncio.run(app.run())


if __name__ == '__main__':
    indexer()
