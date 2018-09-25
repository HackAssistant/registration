from django import template

register = template.Library()


@register.filter
def itoa(value):
    return chr(value + 65)
