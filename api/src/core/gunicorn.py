import multiprocessing

from core.config import settings

bind = f'{settings.APP_HOST}:{settings.APP_PORT}'
workers = settings.APP_WORKERS
reload = settings.DEBUG
worker_class = settings.APP_WORKERS_CLASS
