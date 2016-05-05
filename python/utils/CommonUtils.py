import os
import arrow
from logging import getLogger

__author__ = 'jayvee'


def timer(func):
    def wrapper(*args, **kwargs):
        t = arrow.utcnow()
        res = func(*args, **kwargs)
        print '[%s]cost time = %s' % (func.__name__, arrow.utcnow() - t)
        return res

    return wrapper


PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))

LOGGER = getLogger('')
