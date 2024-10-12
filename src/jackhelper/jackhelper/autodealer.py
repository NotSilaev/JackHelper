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

def connect(city: str) -> fdb.fbcore.Cursor:
    if settings.DEBUG: dev_status = 'test'
    else: dev_status = 'prod'

    AUTODEALER_DB_DSN = dsn_list[city][dev_status]

    connect = fdb.connect(
        dsn=AUTODEALER_DB_DSN, 
        user=AUTODEALER_DB_USER, 
        password=AUTODEALER_DB_PASS,
        charset='WIN1251'
    )

    return connect.cursor()