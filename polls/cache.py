from django_redis import get_redis_connection
import redis
import json

connection = get_redis_connection('default')
redis_server = redis.Redis(connection_pool=connection.connection_pool)

from hahu.settings import PER_PAGE_FEEDS_NUM


def new_feed(feed_id, feed, user_id):
    redis_server.set('feed_{}'.format(feed_id), json.dumps(feed))

    feeds_list_key = 'feeds_list_{}'.format(user_id)
    redis_server.lpush(feeds_list_key, feed_id)

    if redis_server.llen(feeds_list_key) > 100:
        redis_server.rpop(feeds_list_key)


def update_feeds_set(user_ids, feed_ids):
    if len(user_ids) == 0 or len(feed_ids) == 0:
        return

    feed_keys = list(map(lambda i: 'feed_' + i, feed_ids))
    create_times = list(map(lambda f: -json.loads(f.decode('utf-8'))['create_time'], redis_server.mget(feed_keys)))
    data = dict(zip(feed_keys, create_times))
    for user_id in user_ids:
        feeds_set_key = 'feeds_set_' + user_id
        redis_server.zadd(feeds_set_key, **data)


def get_feeds(user, page_num=0):
    from . import models
    feeds_set_key = 'feeds_set_' + str(user.id)
    start, end = page_num * PER_PAGE_FEEDS_NUM, (page_num + 1) * PER_PAGE_FEEDS_NUM
    feed_ids = list(map(lambda k: k.decode('utf-8'), redis_server.zrange(feeds_set_key, start, end)))
    if len(feed_ids) == 0:
        return []

    feeds_from_cache = list(map(lambda f: json.loads(f.decode('utf-8')), redis_server.mget(feed_ids)))
    hit_num = len(feeds_from_cache)
    feeds_from_disk = models.get_feeds(user, start + hit_num, end)

    return feeds_from_cache + feeds_from_disk
