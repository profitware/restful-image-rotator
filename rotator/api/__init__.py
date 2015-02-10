# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

__author__ = 'Sergey Sobko'

from pprint import pformat

from twisted.python import log
from txmongo.connection import ConnectionPool

from rotator.settings import MONGO_URI, USE_SIMPLE_PRINT


def acquire_new_connection_pool():
    return ConnectionPool(uri=MONGO_URI)


def get_rotator_database(connection, is_test=False):
    return connection.rotator_test if is_test else connection.rotator


mongo_connection = {
    'connection': acquire_new_connection_pool(),
    'connected': True,
    'rotator_database': None
}


mongo_connection['rotator_database'] = get_rotator_database(
    mongo_connection.get('connection'),
    is_test=False
)


log.startLogging(log.StdioOnnaStick())


def log_me(*args, **kwargs):
    # pylint: disable=unused-argument

    fmt_msg = pformat([arg for arg in args], width=80, indent=2)

    if USE_SIMPLE_PRINT:
        # pylint: disable=print-statement

        print fmt_msg
    else:
        log.msg(fmt_msg)
