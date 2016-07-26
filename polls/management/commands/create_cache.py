from django.core.management.base import BaseCommand
from polls.models import User, get_feeds
from polls.tasks import save_feedbacks
from hahu.settings import CACHE_FEEDS_NUM


class Command(BaseCommand):
    def handle(self, *args, **options):
        for u in User.objects.all():
            feeds = get_feeds(u, 0, CACHE_FEEDS_NUM)
            save_feedbacks([u.username], feeds)
