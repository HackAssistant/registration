from django.contrib import admin
# Register your models here.
from django.contrib.admin.forms import AdminPasswordChangeForm
from django.contrib.auth.models import Group

from user import models
from user.forms import UserChangeForm


class UserAdmin(admin.ModelAdmin):
    form = UserChangeForm
    change_password_form = AdminPasswordChangeForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'is_organizer', 'is_volunteer', 'is_director')
    list_filter = ('is_volunteer', 'is_director', 'is_organizer', 'is_admin', 'email_verified')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'qr_identifier')}),
        ('Permissions', {'fields': ('is_volunteer', 'is_director', 'is_organizer', 'is_admin', 'email_verified')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2',)}
         ),
    )
    search_fields = ('email',)
    ordering = ('created_time',)
    date_hierarchy = 'created_time'
    filter_horizontal = ()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(UserAdmin, self).get_fieldsets(request, obj)


admin.site.register(models.User, admin_class=UserAdmin)
admin.site.unregister(Group)
