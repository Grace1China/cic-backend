from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.utils.translation import gettext_lazy as _
from django.db.models import Q 


import logging
loger = logging.getLogger('church.all')

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'username','groups_list', 'creator','is_active',)
    list_filter = ('email', 'username','is_active')
    fieldsets = (
        (None, {'fields': ('email', 'username','password','creator')}),
        ('Permissions', {'fields': ('is_active','is_superuser','is_staff','groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username','password1', 'password2','creator', 'is_active','is_staff','groups')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    # list_filter = (
    #     ('creator', admin.RelatedOnlyFieldListFilter),
    # )
    # groups_list.admin_order_field = 'first_groups__name'
    def change_view(self, request,object_id, form_url='', extra_context=None):
        user = request.user
        if user.is_superuser:
            self.fieldsets = (
                (None, {'fields': ('email', 'username','password','creator','church')}),
                ('Permissions', {'fields': ('is_active','is_superuser','is_staff','groups')}),)
            self.add_fieldsets = (
                (None, {
                    'classes': ('wide',),
                    'fields': ('email', 'username','password1', 'password2','creator','church','is_superuser','is_active','is_staff','groups')}
                ),)
        else:
            self.fieldsets = (
                (None, {'fields': ('email', 'username','password','creator')}),
                ('Permissions', {'fields': ('is_active','is_staff','groups')}),)
            self.add_fieldsets = (
                (None, {
                    'classes': ('wide',),
                    'fields': ('email', 'username','password1', 'password2','creator','is_active','is_staff','groups')}
                ),)
        return super(CustomUserAdmin, self).change_view(request,object_id, form_url='', extra_context=None)
    
    def get_list_filter(self, request):
        user = request.user
        if user.is_superuser:
            return ('email', 'username','is_active','church','creator')
        else:
            return ('email', 'username','is_active','creator')

    def get_queryset(self, request):
        try:
            qs = super().get_queryset(request)
            if not request.user.is_superuser:
                loger.info('-----------CustomUserAdmin-----------')
                loger.info(request.user.email)
                qs = qs.filter(Q(creator=request.user) | Q(id=request.user.id))
                loger.info(qs)
                # loger.info(qs)
            return qs
        except Exception as e:
            import traceback
            loger.exception('There is and exceptin',exc_info=True,stack_info=True)
            raise e


admin.site.register(CustomUser, CustomUserAdmin)
