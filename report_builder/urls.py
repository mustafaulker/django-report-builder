from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import include, path
from rest_framework import routers

from . import views
from .api import views as api_views


router = routers.DefaultRouter()
router.register(r'reports', api_views.ReportViewSet)
router.register(r'report', api_views.ReportNestedViewSet, basename="report-nested")
router.register(r'formats', api_views.FormatViewSet)
router.register(r'filterfields', api_views.FilterFieldViewSet)
router.register(r'contenttypes', api_views.ContentTypeViewSet)

urlpatterns = [
    path('report/<int:pk>/download_file/', views.DownloadFileView.as_view(), name="report_download_file"),
    path(
        'report/<int:pk>/download_file/<path:filetype>/',
        views.DownloadFileView.as_view(),
        name="report_download_file",
    ),
    path('report/<int:pk>/check_status/<path:task_id>/', views.check_status, name="report_check_status"),
    path('report/<int:pk>/add_star/', views.ajax_add_star, name="ajax_add_star"),
    path('report/<int:pk>/create_copy/', views.create_copy, name="report_builder_create_copy"),
    path('export_to_report/', views.ExportToReport.as_view(), name="export_to_report"),
    path('api/', include(router.urls)),
    path(
        'api/config/',
        api_views.ConfigView.as_view(),
        name="config",
    ),
    path('api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(
        'api/related_fields/',
        staff_member_required(api_views.RelatedFieldsView.as_view()),
        name="related_fields",
    ),
    path(
        'api/fields/',
        staff_member_required(api_views.FieldsView.as_view()),
        name="fields",
    ),
    path(
        'api/report/<int:report_id>/generate/',
        staff_member_required(api_views.GenerateReport.as_view()),
        name="generate_report",
    ),
    path(
        'api/report/<int:pk>/download_file/<path:filetype>/',
        views.DownloadFileView.as_view(),
        name="report_download_file",
    ),
    path('api/report/<int:pk>/check_status/<path:task_id>/', views.check_status, name="report_check_status"),
    path('report/<int:pk>/', views.ReportSPAView.as_view(), name="report_update_view"),
]

if not hasattr(settings, 'REPORT_BUILDER_FRONTEND') or settings.REPORT_BUILDER_FRONTEND:
    urlpatterns += [
        path(
            '',
            staff_member_required(views.ReportSPAView.as_view()),
            name="report_builder",
        ),
    ]
