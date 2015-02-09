# -*- coding: utf-8 -*-

__author__ = 'Sergey Sobko'

from txmongo.connection import ConnectionPool


def acquire_new_connection_pool():
    return ConnectionPool()


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
