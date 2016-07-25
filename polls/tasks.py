from __future__ import absolute_import

from celery import shared_task
from .cache import redis_server
import json
from hahu.settings import CACHE_FEEDS_NUM


@shared_task
def save_feedbacks(user_ids, feeds):
    data = dict(((json.dumps(feed), -feed['create_time']) for feed in feeds))

    for user_id in user_ids:
        feed_key = 'feeds_' + str(user_id)
        redis_server.zadd('feeds_' + str(user_id), **data)
        redis_server.zremrangebyrank(feed_key, CACHE_FEEDS_NUM, redis_server.zcard(feed_key))
