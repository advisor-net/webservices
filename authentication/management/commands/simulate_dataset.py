import logging

from authentication.simulation import build_simulated_dataset
from django.conf import settings
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Build a simulated dataset for testing
    """

    def handle(self, *args, **options):
        assert settings.IS_LOCAL
        build_simulated_dataset()
