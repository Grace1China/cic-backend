from django.contrib import admin

from . import models
from churchs import models as churchs_md
from church import models as church_md
from users import models as users_md

from api import models as api_md
from ckeditor.widgets import CKEditorWidget
from churchs.models import Media
from parsley.mixins import ParsleyAdminMixin

from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from church.models import Church
from django.db.models import Q 
from django import forms
from churchs.widget import MediaBaseWidget
from users.models import CustomUser
class ChurchForm(forms.ModelForm):
    promot_cover = forms.CharField(label="",widget=MediaBaseWidget(label='海报',typ='images'),required=False)
    giving_qrcode = forms.CharField(label="",widget=MediaBaseWidget(label='奉献二维码',typ='images'),required=False)
    promot_video = forms.CharField(label="",widget=MediaBaseWidget(label='封面',typ='videos'),required=False)
    creator = forms.ChoiceField (
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly','disabled':'disabled'})
    )
    class Meta:
        model = Church
        fields = ('name', 'code','description', 'address', 'promot_cover', 'giving_qrcode', 'promot_video','status','venue','creator','manager')

    def __init__(self, *args, **kwargs):
        super(ChurchForm, self).__init__(*args, **kwargs)
        # if self.initial:
            # when load init from model, when in add page from the admin
            # self.fields['creator'].choices=CustomUser.objects.filter(id=self.initial['creator']).values_list('id','email')
            # self.fields['manager'].choices=Church.objects.filter(id=self.initial['manager']).values_list('id','email')
           


    # def save(self, *args, **kwargs):
    #     return super().save(*args, **kwargs)
class ChurchAdmin(admin.ModelAdmin):
    form = ChurchForm
    list_display = ('name','code','manager','promot_cover','status') 
    search_fields = ('name','status')
    
    def get_changeform_initial_data(self, request):
        return {'creator': request.user,'manager': request.user}
    
    def get_queryset(self, request):
        try:
            qs = super().get_queryset(request)
            if not request.user.is_superuser:
                qs = qs.filter(Q(manager=request.user) or Q(creator=request.user))
                # loger.info(qs)
            return qs
        except Exception as e:
            import traceback
            loger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e
    




from churchs.admin import MediaInline1
class CourseAdmin(ParsleyAdminMixin,admin.ModelAdmin):
    inlines = [
        MediaInline1,
    ]

    list_display = ('title', 'teacher') 
    search_fields = ('teacher', 'title')
    fields = ('church','title', 'teacher','description','content','iap_charge','price','price_usd')

    change_form_template ="admin/churchs/sermon_change_form.html"

    
    
    def get_changeform_initial_data(self, request):
        from churchs.models import Speaker
        spk = Speaker.objects.filter(churchs__in=[request.user.church])[0]
        ret = {'church': request.user.church,'teacher':spk}
        print(ret)
        return ret

admin.site.register(church_md.Church, ChurchAdmin)
admin.site.register(models.Course, CourseAdmin)

admin.AdminSite.site_header = '教会平台'
admin.AdminSite.site_title = '教会平台'


