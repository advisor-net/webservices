"""
Derived from here:
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""

import logging
import os
from smtplib import SMTPDataError

from django.conf import settings
from django.core.mail import EmailMessage

from celery import Celery

logger = logging.getLogger(__name__)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webservices.settings')

app = Celery('webservices')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


@app.task(bind=True)
def send_email_task(
    self,
    subject,
    body,
    to,
    cc=None,
    bcc=None,
    sender=None,
    html=False,
    reply_to=None,
    attachments=None,
):
    if isinstance(to, str):
        to = [to]
    assert isinstance(to, list), 'Required a list of recipients'

    if bcc is None:
        bcc = list()
    if cc is None:
        cc = list()

    # todo figure out why we have `None`s in our recipient lists
    # https://sentry.io/paperless-parts/paperless-parts-backend/issues/534858714
    # clean list for `None`s
    to = [email for email in to if email is not None]
    cc = [email for email in cc if email is not None]
    bcc = [email for email in bcc if email is not None]

    # only send emails to the first 50 people
    # email priority order: default paperless bcc email, to, cc, bcc
    recipientsLeft = 49
    to = to[:recipientsLeft]
    recipientsLeft = max(0, recipientsLeft - len(to))
    cc = cc[:recipientsLeft]
    recipientsLeft = max(0, recipientsLeft - len(cc))
    bcc = bcc[:recipientsLeft]
    bcc.append(settings.ADMIN_EMAIL)

    if isinstance(subject, str):
        subject = subject.replace('\n', ' ').replace('\r', ' ')
    elif isinstance(subject, bytes):
        subject = subject.replace(b'\n', b' ').replace(b'\r', b' ')

    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=sender or settings.ADMIN_EMAIL,
            to=to,
            bcc=bcc,
            reply_to=reply_to,
            cc=cc,
        )
        if html:
            email.content_subtype = 'html'

        if attachments is not None:
            for attachment in attachments:
                email.attach(
                    filename=attachment['filename'],
                    content=attachment['content'],
                    mimetype=attachment['mimetype'],
                )

        email.send(fail_silently=False)
    except SMTPDataError as exc:
        if (
            sender
            and sender in (settings.ADMIN_EMAIL,)
            and exc.smtp_code == 554
            and b'Email address is not verified' in exc.smtp_error
        ):
            # https://docs.aws.amazon.com/ses/latest/DeveloperGuide/smtp-response-codes.html
            # send from default sender and setup 'reply_to' header
            #   if current sender not verified in aws ses
            self.retry(
                countdown=1,
                exc=exc,
                max_retries=1,
                kwargs={
                    'sender': None,
                    "reply_to": [sender],
                    'cc': cc,
                    'bcc': bcc,
                    'html': html,
                },
            )
        else:
            self.retry(countdown=1, exc=exc, max_retries=3)
    except Exception as exc:
        # default retry
        self.retry(countdown=1, exc=exc, max_retries=3)


def send_email(
    subject,
    body,
    to,
    cc=None,
    bcc=None,
    sender=None,
    html=False,
    reply_to=None,
    attachments=None,
):
    if settings.SEND_EMAILS:
        send_email_task.delay(
            subject,
            body,
            to,
            cc=cc,
            bcc=bcc,
            sender=sender,
            html=html,
            reply_to=reply_to,
            attachments=attachments,
        )
