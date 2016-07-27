from __future__ import absolute_import

from celery import shared_task
from . import cache


@shared_task
def new_feed(user_id, follower_names, feed, feed_id):
    cache.new_feed(user_id=user_id, feed_id=feed_id, feed=feed)
    cache.update_feeds_set(user_ids=follower_names, feed_ids=[feed_id])


@shared_task
def new_follow(from_user_id, to_user_id):
    feed_ids = list(map(lambda k: k.decode('utf-8'), cache.redis_server.lrange('feeds_list_' + to_user_id, 0, -1)))
    cache.update_feeds_set(user_ids=[from_user_id], feed_ids=feed_ids)


@shared_task
def delete_follow(from_user_id, to_user_id):
    feed_ids = list(map(lambda k: k.decode('utf-8'), cache.redis_server.lrange('feeds_list_' + to_user_id, 0, -1)))
    cache.redis_server.zrem('feeds_set_' + from_user_id, *feed_ids)
