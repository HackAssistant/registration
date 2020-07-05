from django.conf import settings
from django.contrib import admin
# Register your models here.
from django.contrib.admin.forms import AdminPasswordChangeForm
from django.contrib.auth.models import Group

from user import models
from user.forms import UserChangeForm


class UserAdmin(admin.ModelAdmin):
    form = UserChangeForm
    change_password_form = AdminPasswordChangeForm

    display_fields = ['email', 'name', 'type', 'admin_is_organizer', 'admin_is_volunteer_accepted',
                      'is_director', 'have_application']
    filter_fields = ['is_director', 'is_admin', 'email_verified', 'type']
    permission_fields = ['is_director', 'is_admin', 'email_verified', 'can_review_dubious', 'can_review_blacklist',
                         'can_review_volunteers', 'can_review_mentors', 'can_review_sponsors']

    if settings.HARDWARE_ENABLED:
        display_fields.append('is_hardware_admin')
        filter_fields.append('is_hardware_admin')
        permission_fields.insert(4, 'is_hardware_admin')

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = tuple(display_fields)
    list_filter = tuple(filter_fields)
    permission_fields = tuple(permission_fields)

    fieldsets = (
        (None, {'fields': ('email', 'type', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': permission_fields}),
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


class BlacklistUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'date_of_ban')
    list_per_page = 20
    list_filter = ('email', 'name')
    search_fields = ('email', 'name')
    actions = ['delete_selected', ]


admin.site.register(models.User, admin_class=UserAdmin)
admin.site.register(models.BlacklistUser, admin_class=BlacklistUserAdmin)
admin.site.unregister(Group)
