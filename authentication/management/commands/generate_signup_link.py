import logging

from authentication.models import SignUpLink, User
from django.conf import settings
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate a sign up link for an email"

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            dest='email',
            help='Email',
        )

    def handle(self, *args, **options):
        email = options['email']
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'User with {email} already exists!'))
            return

        signup_link, _ = SignUpLink.objects.get_or_create(email=email)
        self.stdout.write(
            self.style.SUCCESS(
                f'Generated signup link for {email}: {settings.SITE_URL}/signup/{str(signup_link.uuid)}'
            )
        )
