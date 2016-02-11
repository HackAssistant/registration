from django import template
from django.conf import settings

register = template.Library()


# settings value
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

# settings value
@register.filter(is_safe=True)
def url_blank(text):
    return text.replace('<a', '<a target="_blank"')
