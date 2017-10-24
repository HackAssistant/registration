from django.contrib import admin

# Register your models here.
from organizers import models


class CommentAdmin(admin.ModelAdmin):
    list_display = ('application', 'author', 'text')
    list_per_page = 200
    actions = ['delete_selected', ]

admin.site.register(models.ApplicationComment, admin_class=CommentAdmin)
