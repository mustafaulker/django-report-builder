
import copy
import logging
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, View
from .models import Report
from .tasks import generate_report_task
from .utils import duplicate
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required

logger = logging.getLogger(__name__)
User = get_user_model()

class ReportSPAView(TemplateView):
    template_name = "report_builder/spa.html"

    def get_context_data(self, **kwargs):
        context = super(ReportSPAView, self).get_context_data(**kwargs)
        context['ASYNC_REPORT'] = getattr(settings, 'REPORT_BUILDER_ASYNC_REPORT', False)
        return context

class DownloadFileView(View):

    def get_report(self, report_id):
        return get_object_or_404(Report, pk=report_id)

    def process_report(self, report_id, user_id, file_type, to_response=True, queryset=None):
        user = get_object_or_404(User, pk=user_id)
        report = self.get_report(report_id)
        cache_key = f'report_{report_id}_{file_type}'

        # Cache kontrolü
        cached_report = cache.get(cache_key)
        if cached_report:
            logger.info(f"Report {report_id} for file type {file_type} is being served from cache.")
            response = HttpResponse(cached_report, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{report_id}_{file_type}.zip"'
            return response

        if to_response:
            # Raporu hemen oluştur
            report_content = report.run_report(file_type, user, queryset, asynchronous=False)
            
            # Raporu cache'e kaydet, 24 saat süre ile saklanacak
            cache.set(cache_key, report_content, timeout=86400)
            logger.info(f"Report {report_id} for file type {file_type} is generated and saved to cache.")
            
            # Raporun indirilmesi
            response = HttpResponse(report_content, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{report_id}_{file_type}"'

            # Asenkron olarak tekrar cache'e kaydedilmesi için Celery görevi başlatılır
            generate_report_task.delay(report_id, user_id, file_type, queryset)

            return response

    def get(self, request, *args, **kwargs):
        report_id = kwargs['pk']
        file_type = kwargs.get('filetype')

        logger.debug(f'Rapor {report_id} oluşturuluyor...')
        return self.process_report(
            report_id, request.user.pk, file_type, to_response=True
        )
    
    
@staff_member_required
def ajax_add_star(request, pk):
    report = get_object_or_404(Report, pk=pk)
    user = request.user
    if user in report.starred.all():
        added = False
        report.starred.remove(request.user)
    else:
        added = True
        report.starred.add(request.user)
    return HttpResponse(added)

@staff_member_required
def create_copy(request, pk):
    report = get_object_or_404(Report, pk=pk)
    new_report = duplicate(report, changes=(
        ('name', '{0} (copy)'.format(report.name)),
        ('user_created', request.user),
        ('user_modified', request.user),
    ))
    for display in report.displayfield_set.all():
        new_display = copy.copy(display)
        new_display.pk = None
        new_display.report = new_report
        new_display.save()
    for report_filter in report.filterfield_set.all():
        new_filter = copy.copy(report_filter)
        new_filter.pk = None
        new_filter.report = new_report
        new_filter.save()
    return redirect(new_report)

class ExportToReport(DownloadFileView, TemplateView):
    template_name = "report_builder/export_to_report.html"

    def get_context_data(self, **kwargs):
        ctx = super(ExportToReport, self).get_context_data(**kwargs)
        ctx['admin_url'] = self.request.GET.get('admin_url', '/')
        ct = ContentType.objects.get_for_id(self.request.GET['ct'])
        ids = self.request.GET['ids'].split(',')
        ctx['ids'] = ",".join(map(str, ids))
        ctx['ct'] = ct.id
        ctx['number_objects'] = len(ids)
        ctx['object_list'] = Report.objects.filter(
            root_model=ct).order_by('-modified')
        ctx['mode'] = ct.model_class()._meta.verbose_name
        return ctx

    def get(self, request, *args, **kwargs):
        if 'download' in request.GET:
            ct = ContentType.objects.get_for_id(request.GET['ct'])
            ids = self.request.GET['ids'].split(',')
            report = get_object_or_404(Report, pk=request.GET['download'])
            queryset = ct.model_class().objects.filter(pk__in=ids)
            return self.process_report(
                report.id, request.user.pk,
                to_response=True,
                queryset=queryset,
                file_type="xlsx",
            )
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

@staff_member_required
def check_status(request, pk, task_id):
    from celery.result import AsyncResult
    res = AsyncResult(task_id)
    if res.state == 'SUCCESS':
        cache_key = f'report_{pk}_{task_id}'
        cached_report = cache.get(cache_key)
        if cached_report:
            response = HttpResponse(cached_report, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{pk}.csv"'  # or file_type
            return response
    return JsonResponse({'state': res.state})