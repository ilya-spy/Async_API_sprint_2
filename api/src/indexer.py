import asyncio
import logging
import signal
from dataclasses import dataclass

import aioredis
from elasticsearch import AsyncElasticsearch

from core import config
from db import elastic, postgres, redis
from etl import enrichers, loaders, pipeline, producers, state, transformers


@dataclass
class App:
    """Запускает обреботку пайплайнов.
    Обеспечивает корректное завершение при получении сигналов SIGINT и SIGTERM."""
    pipelines_builders: list[callable]
    _stopped: bool = False

    @staticmethod
    def startup():
        redis.redis = aioredis.from_url(f'redis://{config.REDIS_HOST}:{config.REDIS_PORT}')
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

        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for s in signals:
            loop.add_signal_handler(s, lambda s=s: asyncio.create_task(self.shutdown(s, loop)))

        storage = state.RedisStorage(redis=await redis.get_redis(), name=config.ETL_STORAGE_STATE_KEY)
        state_obj = state.State(storage)

        tasks = []
        for build_pipeline in self.pipelines_builders:
            pipe = await build_pipeline(state_obj)
            task = loop.create_task(pipe.execute())
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=False)


async def build_genre_index_pipeline(state_obj: state.State) -> pipeline.Pipeline:
    logger = logging.getLogger().getChild('GenreIndexPipeline')

    enricher = enrichers.GenreEnricher(
        db=await postgres.get_postgres(),
        logger=logger.getChild('Enricher'),
        max_batch_size=config.ETL_ENRICHER_MAX_BATCH_SIZE,
        chunk_size=config.ETL_ENRICHER_CHUNK_SIZE,
    )
    loader = loaders.ElasticIndex(
        elastic=await elastic.get_elastic(),
        transformer=transformers.PgGenreToElasticSearch(),
        index_name='genres',
        state=state_obj,
        logger=logger.getChild('Loader'),
        chunk_size=config.ETL_LOADER_CHUNK_SIZE,
    )
    return pipeline.Pipeline(
        producer_queue_size=config.ETL_PRODUCER_QUEUE_SIZE,
        producers=[
            producers.GenreModified(
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


async def build_person_index_pipeline(state_obj: state.State) -> pipeline.Pipeline:
    logger = logging.getLogger().getChild('PersonIndexPipeline')

    enricher = enrichers.PersonEnricher(
        db=await postgres.get_postgres(),
        logger=logger.getChild('Enricher'),
        max_batch_size=config.ETL_ENRICHER_MAX_BATCH_SIZE,
        chunk_size=config.ETL_ENRICHER_CHUNK_SIZE,
    )
    loader = loaders.ElasticIndex(
        elastic=await elastic.get_elastic(),
        transformer=transformers.PgPersonToElasticSearch(),
        index_name='persons',
        state=state_obj,
        logger=logger.getChild('Loader'),
        chunk_size=config.ETL_LOADER_CHUNK_SIZE,
    )
    return pipeline.Pipeline(
        producer_queue_size=config.ETL_PRODUCER_QUEUE_SIZE,
        producers=[
            producers.PersonModified(
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


async def build_film_index_pipeline(state_obj: state.State) -> pipeline.Pipeline:
    logger = logging.getLogger().getChild('FilmIndexPipeline')

    enricher = enrichers.FilmEnricher(
        db=await postgres.get_postgres(),
        logger=logger.getChild('Enricher'),
        max_batch_size=config.ETL_ENRICHER_MAX_BATCH_SIZE,
        chunk_size=config.ETL_ENRICHER_CHUNK_SIZE,
    )
    loader = loaders.ElasticIndex(
        elastic=await elastic.get_elastic(),
        transformer=transformers.PgFilmToElasticSearch(),
        index_name='films',
        state=state_obj,
        logger=logger.getChild('Loader'),
        chunk_size=config.ETL_LOADER_CHUNK_SIZE,
    )
    return pipeline.Pipeline(
        producer_queue_size=config.ETL_PRODUCER_QUEUE_SIZE,
        producers=[
            producers.FilmworkPersonModified(
                db=await postgres.get_postgres(),
                state=state_obj,
                logger=logger.getChild('FilmworkPersonModifiedProducer'),
                chunk_size=config.ETL_PRODUCER_CHUNK_SIZE,
                check_interval=config.ETL_PRODUCER_CHECK_INTERVAL,
            ),
            producers.FilmworkGenreModified(
                db=await postgres.get_postgres(),
                state=state_obj,
                logger=logger.getChild('FilmworkGenreModifiedProducer'),
                chunk_size=config.ETL_PRODUCER_CHUNK_SIZE,
                check_interval=config.ETL_PRODUCER_CHECK_INTERVAL,
            ),
            producers.FilmworkModified(
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
