from django.contrib import admin
from churchs.models import WeeklyReport, Sermon, Media,SermonSeries,Speaker
from churchs import models as churchs_models
from django.db import models as sysmodels
from ckeditor.widgets import CKEditorWidget
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from churchs.widget import AliVideoWidgetExt
from django.forms import ModelForm,Form
from churchs.widget import S3DirectField,AliOssDirectField,AliOssDirectWidgetExt,AliMediaWidgetExt,MediaBaseWidget
from churchs.forms import MeidaForm2
from users.models import CustomUser
from church.models import Church
from django.utils.html import format_html
from django import forms
from django.db.models import Q
from django.forms import widgets as Fwidgets
from django.forms import fields
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from churchs.models import ContentColumn,Sermon2Medias
from church.confs.prod import get_ALIOSS_DESTINATIONS
from django.forms.widgets import HiddenInput

import logging
loger = logging.getLogger('church.all')
theLogger = logging.getLogger('church.all')


class MediaVideoForm(forms.ModelForm):
  
    alioss_video = forms.CharField(label="",widget=MediaBaseWidget(label='视频',typ='videos'),required=False)
    alioss_audio = forms.CharField(label="",widget=MediaBaseWidget(label='音频',typ='audios'),required=False)
    alioss_image = forms.CharField(label="",widget=MediaBaseWidget(label='封面',typ='images'),required=False)

    class Meta:
        model = churchs_models.Media
        fields = ('title','alioss_video','alioss_audio','alioss_image','alioss_video_status','content',)
        formfield_overrides = {
            Media.content: {'widget': CKEditorWidget()},
        }

    def __init__(self, *args, **kwargs):
        super(MediaVideoForm,self).__init__(*args, **kwargs)


class MediaKindListFilter(admin.SimpleListFilter):

    title = _('内容类型')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'kind'

    def lookups(self, request, model_admin):
        return (
            (6, _('视频')),
            (7, _('音频')),
            (8, _('图文')),
        )

    def queryset(self, request, queryset):
        if self.value() == None:
            return queryset
        else:
            return queryset.filter(Q(kind=self.value()))

class MediaColumnListFilter(admin.SimpleListFilter):

    title = _('所属专栏')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'column'

    def lookups(self, request, model_admin):

        ccls = ContentColumn.objects.filter(church=request.user.church)
        t = ()
        for cl in ccls:
            t = t + ((cl.id,cl.title),)
        return t

    def queryset(self, request, queryset):
        if self.value() == None:
            return queryset
        else:
            return queryset.filter(Q(column=self.value()))


class MediaVideoAdmin(admin.ModelAdmin):
    # form=MediaVideoForm
    class Media:
        js = ("admin/js/jquery.init.js",)
    list_display = ('title_with_link','kind', 'alioss_video_status','promote')  
    list_filter = (MediaKindListFilter, 'alioss_video_status',MediaColumnListFilter)
    # readonly_fields = ('kind',)
    # fieldsets = (
    #     (None, {
    #         'fields': ('title','kind','alioss_video_status','alioss_video','alioss_image')
    #     },),
    #     ('Advanced options', {
    #         'classes': ('collapse',),
    #         'fields': ('content',),
    #     },),
    # ) 
    
    def title_with_link(self,obj):
        return format_html(
            '<a target="_blank" href="/blog/media/{}">{}</a>',
            obj.id,
            obj.title,
        )
    title_with_link.short_description = '标题'

    def get_fieldsets(self,request, obj=None):
        '''
        MEDIA_VIDEOS = 6
        MEDIA_AUDIOS = 7
        MEDIA_TUWEN = 8
        '''
        try:
            # theLogger.info(obj.__dict__)
            data = request.GET
            kind = data.get('kind','')
            if kind == '':
                kind = obj.kind
            # theLogger.info(type(kind))
            # theLogger.info(type(churchs_models.Media.MEDIA_VIDEOS))
            # theLogger.info('kind:%s' % kind)
            fs = None
            if int(kind) == churchs_models.Media.MEDIA_VIDEOS:
                fs = (
                        (None, {
                            'fields': ('title','kind','alioss_video_status','alioss_video','alioss_image','pub_time')
                        },),
                        ('Advanced options', {
                            'classes': ('collapse',),
                            'fields': ('content',),
                        },),
                    )

                # MEDIA_VIDEOS = 6
                # MEDIA_AUDIOS = 7
                # MEDIA_TUWEN = 8
            elif int(kind) == churchs_models.Media.MEDIA_AUDIOS:
                fs = (
                        (None, {
                            'fields': ('title','kind','alioss_audio','alioss_image','pub_time')
                        },),
                        ('Advanced options', {
                            'classes': ('collapse',),
                            'fields': ('content',),
                        },),
                    )
            elif int(kind) == churchs_models.Media.MEDIA_TUWEN:
                fs = (
                        (None, {
                            'fields': ('title','kind','alioss_image','content','pub_time')
                        },),
                    
                    )
            else:
                raise Exception('not support %s' % kind)
            return fs 
        except Exception as e:
            import traceback
            loger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e


    # search_fields = ('pub_time', 'title','status')
    #fields = ('title','creator','church','image', 'status','content','pub_time')
    # readonly_fields = ['pub_time']
    formfield_overrides = {
        churchs_models.Media.content: {'widget': CKEditorWidget()},
    }

    def promote(self, obj):
        button_html = """<a class="changelink" href="#" onclick='fontConfig.premote(%s,"%s")'>推广链接</a>
        <a class="changelink" href="/admin/churchs/media/%d/change/?kind=%s">编辑</a>""" % (obj.id,'touvideo',obj.id,obj.kind)
        return format_html(button_html)
    promote.short_description = "操作"
    
    def get_changeform_initial_data(self, request):
        data = request.GET
        kind = data.get('kind','6')
        
        # churchs_models.Media.  
        validKind(kind)

        theLogger.info('kind: %d' % kind)

        # MEDIA_VIDEOS = 6
        # MEDIA_AUDIOS = 7
        # MEDIA_TUWEN = 8
        # STATUS_NONE = 1
        # STATUS_UPLOADED = 2
        # STATUS_DISTRIBUTED = 3

        return {'alioss_video_status': churchs_models.Media.STATUS_DISTRIBUTED,'kind':int(kind)}

    def validKind(self,kind):
        if int(kind) == churchs_models.Media.MEDIA_VIDEOS or int(kind) == churchs_models.Media.MEDIA_AUDIOS or int(kind) == churchs_models.Media.MEDIA_TUWEN:
            pass
        else:
            raise Exception('not support %s' % kind)


    def save_form(self, request, form,change):
        """
        Given a ModelForm return an unsaved instance. ``change`` is True if
        the object is being changed, and False if it's being added.
        """
        loger.info('---------save_form-------')
        instance = form.save(commit=False)
        loger.info(instance)
        instance.user = request.user
        instance.church = request.user.church

        data = request.GET
        kind = data.get('kind','6')
        validKind(kind)

        instance.kind = int(kind)
        return instance
    

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = MediaVideoForm
        return super().get_form(request, obj, **kwargs)

    def get_queryset(self, request):
        try:
            qs = super().get_queryset(request)
            request.GET = request.GET.copy()
            fp = request.GET.pop('frompage', [])
            columnid = request.GET.pop('columnid', [])
            sermonid = request.GET.pop('sermonid', [])
            # 在个queryset里面，为什么要取出参数保存为成员变量呢？ 因为，只有在这里pop后台的处理代码，才不会把参数处理成 e=1这样的错误信息。

            if (len(fp) == 1):
                self.frompage = fp[0]
            if (len(columnid) == 1):
                self.columnid = columnid[0]
            if (len(sermonid) == 1):
                self.sermonid = sermonid[0]

            if not request.user.is_superuser:
                qs = qs.filter(Q(church=request.user.church) |  Q(kind__in=[churchs_models.Media.MEDIA_VIDEOS,churchs_models.Media.MEDIA_AUDIOS,churchs_models.Media.MEDIA_TUWEN]))
            return qs
        except Exception as e:
            import traceback
            loger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e
    frompage = ''
    columnid = 0
    sermonid = 0
    
    actions = ['add_to_column','add_to_sermon','add_content']
    def add_to_column(self, request, queryset):
        from django.http import HttpResponse
        data = request.GET
        kind = data.get('kind','video')
        col = ContentColumn.objects.get(id=self.columnid)
        for m in queryset.all():
            col.medias.add(m)
        col.save()
        response = HttpResponse(content_type="text/html")
        response.write('''<script>
            window.opener.window.formVue.loadForm();
            window.close();
        </script>''')
        return response
    # add_to_column.allowed_permissions = ('加入专栏',)
    add_to_column.short_description = "加入专栏"

    def add_to_sermon(self, request, queryset):
        from django.http import HttpResponse
        sermon = Sermon.objects.get(id=self.sermonid)
        for m in queryset.all():
            sermon.medias.add(m)
        sermon.save()

        # kind = request.GET('kind',-1)
        # alioss_video_status__exact = request.GET('alioss_video_status__exact',-1)
        column = request.GET.get('column',-1)
        if int(column) > 0 :
            Sermon2Medias.objects.filter(Sermon=sermon, Media__in=queryset.all()).update(fromColumn=column)

        response = HttpResponse(content_type="text/html")
        response.write('''<script>
            window.opener.window.formVue.loadForm();
            window.close();
        </script>''')
        return response
    # add_to_column.allowed_permissions = ('加入专栏',)
    add_to_column.short_description = "加入主日信息"

    def add_content(self, request, queryset):
        # from django.http import HttpResponse
        response = HttpResponse(content_type="text/html")
        response.write('''<script>
        </script>''')
        return response


    def get_actions(self, request):
        actions = super().get_actions(request)
        if self.frompage != 'content_column' and 'add_to_column' in actions:
            del actions['add_to_column']
        
        if self.frompage != 'sermon' and 'add_to_sermon' in actions:
            del actions['add_to_sermon']

        return actions

    

    list_display_links = None

    def view_on_site(self, obj):
        return '/admin/churchs/media/%d/change/?kind=%d' % (obj.id,obj.kind)
