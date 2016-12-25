from django.urls import reverse as django_reverse


def reverse(viewname, args=None, kwargs=None, request=None, format=None, **extra):
    """
    Same as `django.urls.reverse`, but optionally takes a request
    and returns a fully qualified URL, using the request to get the base URL.
    """
    if format is not None:
        kwargs = kwargs or {}
        kwargs['format'] = format
    url = django_reverse(viewname, args=args, kwargs=kwargs, **extra)
    if request:
        return request.build_absolute_uri(url)
    return url