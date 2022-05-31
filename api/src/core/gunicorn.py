import multiprocessing

from core import config as cfg

bind = f'{cfg.APP_HOST}:{cfg.APP_PORT}'
workers = multiprocessing.cpu_count() * 2 + 1
reload = cfg.DEBUG
worker_class = 'uvicorn.workers.UvicornWorker'
