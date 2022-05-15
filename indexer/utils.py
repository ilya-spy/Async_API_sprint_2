import logging
import time

import log


def backoff(start_sleep_time: float = 0.1,
            factor: int = 2,
            border_sleep_time: float = 10,
            logger: logging.Logger = None):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :param logger: логгер для ошибок, если не передан, используется по умолчанию из пакета log
    :return: результат выполнения функции
    """

    if logger is None:
        logger = log.logger

    def func_wrapper(func):
        def inner(*args, **kwargs):
            n = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except BaseException as e:
                    logger.info(e)

                    t = start_sleep_time * (2 ^ n)
                    if t < border_sleep_time:
                        t = border_sleep_time
                    time.sleep(t)
                    n += factor

        return inner

    return func_wrapper
