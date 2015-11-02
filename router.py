import json
import collections

from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import patterns, url
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.conf import settings


named_routes = {
    'list': r'^$',
    'item': r'^$',
    'create-form': r'^new/$',
    'edit-form': r'^edit/$',
}


def full_name(prefix, name):
    if not prefix:
        return name
    return prefix + '-' + name


class Route(object):

    def __init__(self):
        self.handlers = {'OPTIONS': self.show_options}

    def add_handler(self, method, handler):
        self.handlers[method] = handler
        if method == 'GET':
            self.add_handler('HEAD', handler)

    def show_options(self, request, *args, **kwargs):
        response = HttpResponse('')
        response['Allow'] = ', '.join(self.handlers.keys())
        return response

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        handler = self.handlers.get(request.method)
        if handler is None:
            return HttpResponseNotAllowed(self.handlers.keys())
        return handler(request, *args, **kwargs)


class RouteSet(object):

    def __init__(self, name_prefix):
        self.routes = collections.defaultdict(Route)
        self.name_prefix = name_prefix

    def add_route(self, name, method, handler):
        self.routes[name].add_handler(method, handler)

    @property
    def urls(self):
        url_patterns = []
        for name, route in self.routes.items():
            url_patterns.append(url(named_routes[name],
                                    route.dispatch,
                                    name=full_name(self.name_prefix, name)))
        return patterns('', *url_patterns)


class RoutableResourceMixin(object):

    def _create_routeset(self, handlers, name_prefix):
        routeset = RouteSet(name_prefix)
        for handler, data in handlers.items():
            if hasattr(self, handler):
                routeset.add_route(data['name'], data['method'],
                                   getattr(self, handler))
        return routeset

    def get_list_handlers(self):
        return {
            'create': {'method': 'POST', 'name': 'list'},
            'index': {'method': 'GET', 'name': 'list'},
            'new': {'method': 'GET', 'name': 'create-form'},
        }

    def get_item_handlers(self):
        return {
            'edit': {'method': 'GET', 'name': 'edit-form'},
            'show': {'method': 'GET', 'name': 'item'},
            'delete': {'method': 'DELETE', 'name': 'item'},
            'update': {'method': 'PUT', 'name': 'item'},
        }

    def list_urls(self, prefix=None):
        handlers = self.get_list_handlers()
        return self._create_routeset(handlers, prefix).urls

    def item_urls(self, prefix=None):
        handlers = self.get_item_handlers()
        return self._create_routeset(handlers, prefix).urls