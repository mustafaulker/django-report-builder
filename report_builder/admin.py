from django.conf import settings
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.templatetags.static import static
from django.urls import reverse
from django.utils.safestring import mark_safe

from report_builder.models import Format, Report


class StarredFilter(SimpleListFilter):
    title = 'Your starred reports'
    parameter_name = 'starred'

    def lookups(self, request, model_admin):
        return (('Starred', 'Starred Reports'),)

    def queryset(self, request, queryset):
        if self.value() == 'Starred':
            return queryset.filter(starred=request.user)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'ajax_starred',
        'edit',
        'name',
        'description',
        'root_model',
        'created',
        'modified',
        'user_created',
        'download_xlsx',
        'copy_report',
    )
    readonly_fields = [
        'slug',
    ]
    fields = ['name', 'description', 'root_model', 'slug']
    search_fields = ('name', 'description')
    list_filter = (StarredFilter, 'root_model', 'created', 'modified', 'root_model__app_label')
    list_display_links = []
    show_save = False

    class Media:
        js = [
            'admin/js/jquery.init.js',
            'report_builder/js/report_list.js',
            'report_builder/js/report_form.js',
        ]

    def response_add(self, request, obj, post_url_continue=None):
        if '_easy' in request.POST:
            return HttpResponseRedirect(obj.get_absolute_url())
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        if '_easy' in request.POST:
            return HttpResponseRedirect(obj.get_absolute_url())
        return super().response_change(request, obj)

    def change_view(self, request, object_id, extra_context=None):
        if getattr(settings, 'REPORT_BUILDER_ASYNC_REPORT', False) and 'report_file' not in self.fields:
            self.fields += ['report_file', 'report_file_creation']
        return super().change_view(request, object_id, extra_context=None)

    def changelist_view(self, request, extra_context=None):
        self.user = request.user
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(
        description="Starred",
    )
    def ajax_starred(self, obj):
        if obj.starred.filter(id=self.user.id):
            img = static('report_builder/img/star.png')
        else:
            img = static('report_builder/img/unstar.png')
        return mark_safe(
            '<a href="javascript:void(0)" onclick="ajax_add_star(this, \'{}\')"><img style="width: 26px; margin: -6px;" src="{}"/></a>'.format(
                reverse('ajax_add_star', args=[obj.id]),
                img,
            ),
        )

    def save_model(self, request, obj, form, change):
        star_user = False
        if not obj.id:
            obj.user_created = request.user
            star_user = True
        obj.user_modified = request.user
        if obj.distinct is None:
            obj.distinct = False
        obj.save()
        if star_user:  # Star created reports automatically
            obj.starred.add(request.user)


@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    pass


def export_to_report(modeladmin, request, queryset):
    admin_url = request.get_full_path()
    selected_int = queryset.values_list('id', flat=True)
    selected = []
    for s in selected_int:
        selected.append(str(s))
    ct = ContentType.objects.get_for_model(queryset.model)
    return HttpResponseRedirect(
        reverse('export_to_report') + "?ct={}&admin_url={}&ids={}".format(ct.pk, admin_url, ",".join(selected)),
    )


if getattr(settings, 'REPORT_BUILDER_GLOBAL_EXPORT', False):
    admin.site.add_action(export_to_report, 'Export to Report')
