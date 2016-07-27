from django.core.management.base import BaseCommand
from polls.models import User, get_self_feeds
from polls.tasks import new_feed
from hahu.settings import CACHE_FEEDS_NUM


class Command(BaseCommand):
    def handle(self, *args, **options):
        for u in User.objects.all():
            feeds = get_self_feeds(u, 0, 100)
            for f in feeds:
                new_feed(user_id=u.username, follower_names=u.profile.follower_names, feed=f, feed_id=str(f['feed_id']))
