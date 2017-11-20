import logging
from copy import copy

from django.core.mail import EmailMultiAlternatives
from django.views.debug import ExceptionReporter

from app import settings


class HackathonDevEmailHandler(logging.Handler):
    """An exception log handler that emails log entries to site hackathon devs.

    If the request is passed as the first argument to the log record,
    request data will be provided in the email report.
    
    This is replicated from Django log to use the default backend properly.
    
    See: https://docs.djangoproject.com/en/1.11/howto/error-reporting/
    """

    def emit(self, record):

        try:
            request = record.request
        except Exception:
            request = None

        subject = '%s: %s' % (
            record.levelname,
            record.getMessage()
        )
        subject = subject.replace('\n', '\\n').replace('\r', '\\r')

        # Since we add a nicely formatted traceback on our own, create a copy
        # of the log record without the exception data.
        no_exc_record = copy(record)
        no_exc_record.exc_info = None
        no_exc_record.exc_text = None

        if record.exc_info:
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)
        if settings.HACKATHON_DEV_EMAILS:
            reporter = ExceptionReporter(request, is_email=True, *exc_info)
            message = "%s\n\n%s" % (self.format(no_exc_record), reporter.get_traceback_text())
            html_message = reporter.get_traceback_html()
            msg = EmailMultiAlternatives(subject,
                                         message,
                                         'server@' + settings.HACKATHON_DOMAIN,
                                         settings.HACKATHON_DEV_EMAILS)
            msg.attach_alternative(html_message, 'text/html')
            msg.send(fail_silently=True)
