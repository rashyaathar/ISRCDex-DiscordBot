# -- Source - https://stackoverflow.com/a/55046826
# -- Posted by Nobilis, modified by community. See post 'Timeline' for change history
# -- Retrieved 2026-11-06, License - CC BY-SA 4.0

from django.core.management.base import BaseCommand
from django.core.cache import cache

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cache.clear()
        self.stdout.write('Cleared cache\n')