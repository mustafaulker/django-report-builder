from django.urls import path

from .views import run_scheduled_report

urlpatterns = [
    path('report/<int:pk>/run_scheduled_report/', run_scheduled_report, name="run_scheduled_report"),
]
