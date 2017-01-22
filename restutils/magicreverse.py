from django.core.urlresolvers import get_resolver
from django.core.urlresolvers import reverse as django_reverse
from django.core.urlresolvers import resolve

from restutils.lib.uri_tools import full_uri


class MagicReverser:

    def __init__(self, request):
        self.request = request
        _, self.args, self.kwargs = resolve(request.path)

    def rev(self, route_name, **kwargs):
        self.kwargs.update(kwargs)
        filter_keys = get_resolver(None).reverse_dict[route_name][0][0][1]
        filtered_kwargs = {
            filter_key: self.kwargs.get(filter_key) for filter_key in filter_keys
        }
        return full_uri(
            self.request,
            django_reverse(route_name, kwargs=filtered_kwargs))
