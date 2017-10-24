from django.conf.urls import url
from django.contrib import admin, messages
# Register your models here.
from django.contrib.admin.forms import AdminPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse

from app.utils import reverse
from user import models
from user.forms import UserChangeForm, UserCreationForm


class UserAdmin(admin.ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'nickname', 'is_organizer', 'is_volunteer', 'is_director')
    list_filter = ('is_volunteer', 'is_director', 'is_organizer', 'email_verified')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('nickname',)}),
        ('Permissions', {'fields': ('is_volunteer', 'is_director', 'is_organizer', 'email_verified')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nickname', 'password1', 'password2',)}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(UserAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super(UserAdmin, self).get_form(request, obj, **defaults)

    def get_urls(self):
        return [url(
            r'^(.+)/password/$',
            self.admin_site.admin_view(self.user_change_password),
            name='auth_user_password_change', ), ] + super(UserAdmin, self).get_urls()

    def user_change_password(self, request, id):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = self.get_object(request, id.split('/')[0])
        if user is None:
            raise Http404()
        if request.method == 'POST':
            form = AdminPasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Password changed successfully.')
                update_session_auth_hash(request, form.user)
                return HttpResponseRedirect(
                    reverse(
                        '%s:%s_%s_change' % (
                            self.admin_site.name,
                            user._meta.app_label,
                            user._meta.model_name,
                        ),
                        args=(user.pk,),
                    )
                )
        else:
            form = AdminPasswordChangeForm(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': 'Change password: %s' % user.get_username(),
            # 'form_url': form_url,
            'form': adminForm,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        context.update(self.admin_site.each_context(request))
        #
        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            'admin/auth/user/change_password.html',
            context,
        )


admin.site.register(models.User, admin_class=UserAdmin)
admin.site.unregister(Group)
