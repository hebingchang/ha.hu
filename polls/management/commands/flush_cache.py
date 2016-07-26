from django.core.management.base import BaseCommand
from polls.cache import redis_server


class Command(BaseCommand):
    help = 'Flush the redis database'

    def handle(self, *args, **options):
        redis_server.flushdb()
