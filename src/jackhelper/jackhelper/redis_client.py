from .config import REDIS_DB, REDIS_HOST, REDIS_PORT

import redis
import json


redis_connection = None
def getRedisConnection() -> redis.Redis:
    global redis_connection
    if redis_connection is None:
        redis_connection = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    return redis_connection

def setValue(key, value, expiration: int) -> None:
    redis = getRedisConnection()
    value = json.dumps(value)
    redis.set(key, value, ex=expiration)

def getValue(key) -> str | None:
    redis = getRedisConnection()
    value = redis.get(key)
    if value:
        return json.loads(value)

def delKey(key) -> None:
    redis = getRedisConnection()
    redis.delete(key)