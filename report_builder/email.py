from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import get_template


def email_report(report_url, user=None, email=None):
    if (getattr(settings, 'EMAIL_BACKEND', False) or getattr(settings, 'EMAIL_HOST', False)) and getattr(
        settings,
        'DEFAULT_FROM_EMAIL',
        False,
    ):
        name = None
        if user:
            email = user.email
            name = user.username

        if get_template('email/email_report.html'):
            email_template = get_template('email/email_report.html')
            msg = EmailMultiAlternatives(
                getattr(settings, 'REPORT_BUILDER_EMAIL_SUBJECT', False) or 'Report is ready',
                report_url,
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            html_parameters = {
                'name': name,
                'report': report_url,
            }
            msg.attach_alternative(
                email_template.render(html_parameters),
                "text/html",
            )
            msg.send()
        else:
            send_mail(
                getattr(settings, 'REPORT_BUILDER_EMAIL_SUBJECT', False) or 'Report is ready',
                str(report_url),
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,
            )
