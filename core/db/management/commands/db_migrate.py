from django.core.management import call_command
from django.core.management.base import BaseCommand

from core.db.config import get_domain_backend
from core.db.migrations import run_mongo_migrations


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command("migrate")
        if get_domain_backend() == "mongodb":
            run_mongo_migrations()
