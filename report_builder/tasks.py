import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.cache import cache

from .mixins import DataExportMixin
from .models import Report

logger = logging.getLogger(__name__)

@shared_task
def generate_report_task(report_id, user_id, file_type, queryset=None):
    logger.info(f"Starting report generation task for report_id: {report_id}, user_id: {user_id}, file_type: {file_type}")

    User = get_user_model()
    user = User.objects.get(pk=user_id)
    report = Report.objects.get(pk=report_id)
    logger.debug(f"{report}")

    cache_key = f'report_{report_id}_{file_type}'

    try:
        logger.debug(f"Running report with file_type: {file_type}")
        report_content = report.run_report(file_type, user, queryset, asynchronous=True)

        logger.debug(f"Report generated. Checking if it needs to be zipped...")

        if file_type in ['csv', 'xlsx'] and not cache_key.endswith('.zip'):
            export_mixin = DataExportMixin()
            logger.debug(f"File type is {file_type}. Preparing to zip the report content.")
            
            if file_type == 'csv':
                logger.debug("Zipping CSV content...")
                report_content = export_mixin.build_zip_response({'report.csv': report_content}, title="report")
            elif file_type == 'xlsx':
                logger.debug("Zipping XLSX content...")
                report_content = export_mixin.build_zip_response({'report.xlsx': report_content}, title="report")

            cache_key = f'report_{report_id}_{file_type}.zip'

            logger.debug("Zipping process completed.")

        logger.debug(f"Saving the report to cache with key: {cache_key}")
        cache.set(cache_key, report_content, timeout=86400)  # 86400 saniye = 24 saat
        logger.info(f"Report {report_id} for file type {file_type} is generated and saved to cache successfully.")

        return cache_key

    except Report.DoesNotExist as e:
        logger.error(f"Report {report_id} does not exist: {e}")
        raise ValueError("Requested report does not exist.")

    except Exception as e:
        logger.error(f"Error occurred while processing report {report_id} for user {user_id}: {e}")
        raise ValueError("An unexpected error occurred while generating the report. Please try again later.")