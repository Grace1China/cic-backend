# from churchs.admins.admin_ContentColumn import ContentColumnAdmin
from django.forms import modelformset_factory
from churchs.form.column import ColChangeListForm, ContentColumnForm, ColumnMediasInline
from django.contrib.admin.views.main import ChangeList
from django.contrib import admin
from churchs import models as churchs_models
from churchs.models.columnContent import ContentColumn

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
from django.utils.html import format_html
import logging

loger = logging.getLogger('church.all')


class ColChangeList(ChangeList):
    def __init__(self,
                 request, model,
                 list_display, list_display_links, list_filter,
                 date_hierarchy, search_fields, list_select_related,
                 list_per_page, list_max_show_all, list_editable,
                 model_admin, sortable_by
                 ):
        # self.list_per_page = 20
        super(ColChangeList, self).__init__(request, model,
                                            list_display, list_display_links, list_filter,
                                            date_hierarchy, search_fields, list_select_related,
                                            list_per_page, list_max_show_all, list_editable,
                                            model_admin, sortable_by)

        # these need to be defined here, and not in MovieAdmin
        self.list_display = ['action_checkbox', 'title', 'cover', 'pub_time',
                             'status', 'parentCol', 'hierarchy','user']
        self.list_display_links = ['title']
        self.list_editable = ['cover', 'parentCol','user']
        self.sortable_by = ['title', 'cover', 'pub_time', 'status', 'parentCol', 'hierarchy']
        # self.list_per_page = 20
        self.search_fields = ['title', 'status', 'parentCol']
        self.list_select_related = True


class ColAdmin(admin.ModelAdmin):
    form = ContentColumnForm
    model = ContentColumn

    def get_changelist(self, request, **kwargs):
        return ColChangeList

    def get_changelist_form(self, request, **kwargs):
        return ColChangeListForm

    def get_changelist_formset(self, request, **kwargs):
        kwargs['formset'] = modelformset_factory(
            ContentColumn, form=ColChangeListForm, can_order=True)
        return super().get_changelist_formset(request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        loger.info('---------get_form--------')
        # return ContentColumnForm
        kwargs['form'] = ContentColumnForm
        # return ContentColumnForm(initial=self.get_changeform_initial_data(request=request))
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if form.cleaned_data['cover'] != obj.cover:
            obj.cover = form.cleaned_data['cover']
        if form.cleaned_data['parentCol'] != obj.parentCol:
            obj.parentCol_id = form.cleaned_data['parentCol']
        obj.church = request.user.church
        obj.user = request.user
        loger.info('-------save_model----------')
        loger.info(obj.__dict__)
        obj.save()

    def get_queryset(self, request):
        try:
            qs = super().get_queryset(request)
            qs = qs.filter(church=request.user.church)
            # loger.info(qs)
            return qs
        except Exception as e:
            import traceback
            loger.exception('There is and exceptin',
                            exc_info=True, stack_info=True)
            raise e

    ordering = ['title', 'cover', 'pub_time', 'status', 'parentCol', 'hierarchy']
    list_display = ['title', 'cover', 'pub_time', 'status', 'parentCol', 'hierarchy','user']
    fieldsets = (
        (None, {
            'fields': ('title', 'pub_time', 'status', 'cover', 'add_content')
        },),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('parentCol', 'content',),
        },),
    )
    list_per_page = 10

    def get_changeform_initial_data(self, request):
        loger.info('-------get_changeform_initial_data-----------')
        return {'user': request.user.id, 'church': request.user.church,
                'status': churchs_models.ContentColumn.STATUS_CLOSE}

    readonly_fields = ('add_content',)

    def add_content(self, instance):
        # assuming get_full_address() returns a list of strings
        # for each line of the address and you want to separate each
        # line by a linebreak
        if instance.id is None:
            return format_html(

                '''<el-button disabled @click="popupCenter('/admin/churchs/media/?kind=6&frompage=content_column&columnid={}','媒体库',900,600)">{}</el-button>''',
                0,
                '批量添加内容,先保存专栏'
            )
        else:
            return format_html(

                '''<el-button @click="popupCenter('/admin/churchs/media/?kind=6&frompage=content_column&columnid={}','媒体库',900,600)">{}</el-button>''',
                instance.id,
                '批量添加内容'
            )

    change_form_template = "admin/churchs/change_form_content.html"

    # short_description functions like a model field's verbose_name
    add_content.short_description = "批量添加内容"

    inlines = [
        ColumnMediasInline,
    ]


admin.site.register(churchs_models.ContentColumn, ColAdmin)

