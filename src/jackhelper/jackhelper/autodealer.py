from django.conf import settings

from .config import (
    AUTODEALER_DB_DSN_VLG,
    AUTODEALER_DB_DSN_VLZ,
    TEST_AUTODEALER_DB_DSN_VLG,
    TEST_AUTODEALER_DB_DSN_VLZ,
    AUTODEALER_DB_USER,
    AUTODEALER_DB_PASS
)

import fdb
import datetime


dsn_list = {
    'VLG': {
        'prod': AUTODEALER_DB_DSN_VLG, 
        'test': TEST_AUTODEALER_DB_DSN_VLG,
    },
    'VLZ': {
        'prod': AUTODEALER_DB_DSN_VLZ, 
        'test': TEST_AUTODEALER_DB_DSN_VLZ,
    },
}

def getConnect(city: str) -> fdb.connect:
    '''Makes a connection with AutoDealer database.'''

    if settings.DEBUG: dev_status = 'test'
    else: dev_status = 'prod'

    AUTODEALER_DB_DSN = dsn_list[city][dev_status]

    connect = fdb.connect(
        dsn=AUTODEALER_DB_DSN, 
        user=AUTODEALER_DB_USER, 
        password=AUTODEALER_DB_PASS,
        charset='WIN1251'
    )

    return connect


def fetch(
    cursor: fdb.fbcore.Cursor, 
    query: str,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    fetch_type: str, 
    indexes: list = None, 
    zero_if_none=False
):
    '''Executes an SQL fetch query.
    
    :param query: SQL fetch query.
    :param fetch_type: if `one`, the fetchone() function will be executed, if `all` - the fetchall().
    :param indexes: list of indexes to data select from the database response.
    :param zero_if_zone: if `True` and query response is `None`, the function returns `0` instead of `None`.
    '''

    response = cursor.execute(
        query % {
            'start_date': start_date, 
            'end_date': end_date
        }
    )
    match fetch_type:
        case 'one': response = response.fetchone()
        case 'all': response = response.fetchall()
    if indexes:
        for i in indexes:
            response = response[0]
    if zero_if_none and response is None:
        return 0
    return response