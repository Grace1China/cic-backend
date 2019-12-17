from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.utils.translation import gettext_lazy as _



class creatorListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('创建者')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'creator'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('creator', _('创建者')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        # if self.value() == 'creator':
        if request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(creator=request.user)
        

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'username','groups_list', 'creator','is_active',)
    list_filter = ('email', 'username','is_active',creatorListFilter)
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
                (None, {'fields': ('email', 'username','password','creator')}),
                ('Permissions', {'fields': ('is_active','is_superuser','is_staff','groups')}),)
            self.add_fieldsets = (
                (None, {
                    'classes': ('wide',),
                    'fields': ('email', 'username','password1', 'password2','creator','is_superuser','is_active','is_staff','groups')}
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


admin.site.register(CustomUser, CustomUserAdmin)
