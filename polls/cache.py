from django_redis import get_redis_connection
import redis
import json

connection = get_redis_connection('default')
redis_server = redis.Redis(connection_pool=connection.connection_pool)

from hahu.settings import PER_PAGE_FEEDS_NUM


def get_feeds(user, page_num=0):
    from . import models
    feed_key = 'feeds' + str(user.id)
    start, end = page_num * PER_PAGE_FEEDS_NUM, (page_num + 1) * PER_PAGE_FEEDS_NUM
    feeds_from_cache = list(map(json.loads, redis_server.zrange(feed_key, start, end)))
    hit_num = len(feeds_from_cache)
    feeds_from_disk = models.get_feeds(user, start + hit_num, end)

    return feeds_from_cache + feeds_from_disk

# TODO: load data from disk
