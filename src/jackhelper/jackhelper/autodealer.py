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
import decimal


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
    query: str,
    fetch_type: str,
    cursor: fdb.fbcore.Cursor = None,
    city: str = None,
    indexes: list = None,
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
    zero_if_none: bool = False,
    as_dict: bool = False,
    convert_decimal_to_float: bool = False
):
    '''Executes an SQL fetch query.
    
    :param query: SQL fetch query.
    :param fetch_type: if `one`, the fetchone() function will be executed, if `all` - the fetchall().
    :param cursor: database connection cursor.
    :param city: the city to connect to the database. Passed if the cursor was not passed.
    :param indexes: list of indexes to data select from the database response.
    :param start_date: sets the start date of the sampling period. If it is not `None`, then it must also be `end_date`.
    :param end_date: sets the end date of the sampling period. If it is not `None`, then it must also be `start_date`.
    :param zero_if_zone: if `True` and query response is `None`, the function returns `0` instead of `None`.
    :param convert_decimal_to_float: if `True`, all decimal fields will be converted to float.
    :param as_dict: if `True`, returns the response in the dictionary view (works only with `all` fetch_type).
    '''

    if cursor is None:
        if city:
            connection = getConnect(city)
            cursor = connection.cursor()
        else:
            raise ValueError('Сursor and Сity cannot be None at the same time')

    response = cursor.execute(
        query % {
            'start_date': start_date, 
            'end_date': end_date
        } if (start_date and end_date) else query
    )

    match fetch_type:
        case 'one': response = response.fetchone()
        case 'all': response = response.fetchall()
        case _:
            raise ValueError('Invalid fetch_type')

    if indexes:
        for i in indexes:
            response = response[0]

    if zero_if_none and response is None:
        return 0

    if convert_decimal_to_float:
        if fetch_type == 'one':
            response = float(response)
        elif fetch_type == 'all':
            response = [
                [float(column) if isinstance(column, decimal.Decimal) else column for column in row] 
                for row in response
            ]
    if as_dict:
        columns = [desk[0] for desk in cursor.description]
        if fetch_type == 'all':
            response = [dict(zip(columns, row)) for row in response]

    return response