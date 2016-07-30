import redis
from hahu.settings import REDIS_HOST

socket_redis = redis.Redis(host=REDIS_HOST, port=6379, db=2)
