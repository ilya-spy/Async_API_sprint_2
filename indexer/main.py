import signal
import time
from dataclasses import dataclass

import redis
from elasticsearch import Elasticsearch

import enrichers
import loaders
import producers
import settings
import states
import transformers
from db import DB
from log import logger
from pipelines import Pipeline


@dataclass
class App:
    """Запускает обреботку пайплайнов.
    Обеспечивает корректное завершение при получении сигналов SIGINT и SIGTERM."""
    pipelines: list[Pipeline]
    check_interval_sec: int
    _stopped: bool = False

    def __post_init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self._stopped = True

    def run(self):
        """Запускает пайплайны с инетрвалом."""
        while not self._stopped:
            for pipeline in self.pipelines:
                pipeline.execute()
            time.sleep(self.check_interval_sec)


def init_app():
    db = DB(dsn=settings.PG_DSN)
    es_client = Elasticsearch(f'{settings.ES_SCHEMA}://{settings.ES_HOST}:{settings.ES_PORT}',
                              max_retries=settings.ES_MAX_RETRIES)
    redis_client = redis.Redis(**settings.REDIS_DSN)

    storage = states.RedisStorage(redis=redis_client, name=settings.STORAGE_STATE_KEY)
    state = states.State(storage)

    enricher = enrichers.Movie(db)
    transformer = transformers.ElasticSearchMovie()
    loader = loaders.ElasticSearchMovie(client=es_client, index=settings.ES_MOVIE_INDEX_NAME)

    pipelines = [
        Pipeline(
            name='PersonModified',
            state=state,
            producer=producers.PersonModified(db, settings.CHUNK_SIZE),
            enricher=enricher,
            transformer=transformer,
            loader=loader,
            logger=logger,
        ),
        Pipeline(
            name='GenreModified',
            state=state,
            producer=producers.GenreModified(db, settings.CHUNK_SIZE),
            enricher=enricher,
            transformer=transformer,
            loader=loader,
            logger=logger,
        ),
        Pipeline(
            name='FilmworkModified',
            state=state,
            producer=producers.FilmworkModified(db, settings.CHUNK_SIZE),
            enricher=enricher,
            transformer=transformer,
            loader=loader,
            logger=logger,
        ),
    ]

    App(pipelines=pipelines, check_interval_sec=settings.CHECK_INTERVAL_SEC).run()


if __name__ == '__main__':
    init_app()
