from __future__ import absolute_import

from celery import shared_task
from . import cache


@shared_task
def new_feed(user_id, follower_names, feed, feed_id):
    cache.new_feed(user_id=user_id, feed_id=feed_id, feed=feed)
    cache.update_feeds_set(user_ids=follower_names, feed_ids=[feed_id])
