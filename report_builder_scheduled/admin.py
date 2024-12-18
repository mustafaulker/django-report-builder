from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import ScheduledReport


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ('report', 'is_active', 'last_run_at', 'run_report_url')
    list_filter = ('is_active', 'last_run_at')
    readonly_fields = ('last_run_at',)

    @admin.display(
        description='',
    )
    def run_report_url(self, obj):
        url = reverse('run_scheduled_report', kwargs={'pk': obj.id})
        return format_html('<a href="{}">Run Report</a>', url)
