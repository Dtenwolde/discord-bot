import logging
from functools import wraps
from time import time


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        logger = logging.getLogger("timing")
        logger.info(f"{f.__name__}: {te - ts}")
        return result

    return wrap
