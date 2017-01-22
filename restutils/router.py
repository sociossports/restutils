from collections import defaultdict

from django.views.decorators.csrf import csrf_exempt
from django.conf.urls import url
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed

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


class Route:
    def __init__(self):
        self.handlers = {
            'OPTIONS': self.show_options,
        }

    def add_handler(self, method, handler):
        self.handlers[method] = handler
        if method == 'GET':
            self.add_handler('HEAD', handler)

    def show_options(self, request, *args, **kwargs):
        response = HttpResponse('')
        response['Allow'] = ', '.join(self.handlers.keys())
        return response

    # NOTE removed global @csrf_exempt.. why even?
    # @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        handler = self.handlers.get(request.method)
        if handler is None:
            return HttpResponseNotAllowed(self.handlers.keys())
        return handler(request, *args, **kwargs)


class RouteSet:
    def __init__(self, name_prefix):
        self.routes = defaultdict(Route)
        self.name_prefix = name_prefix

    def add_route(self, name, method, handler):
        self.routes[name].add_handler(method, handler)

    @property
    def urls(self):
        url_patterns = []
        for name, route in self.routes.items():
            url_patterns.append(
                url(
                    named_routes[name],
                    route.dispatch,
                    name=full_name(self.name_prefix, name),
                ))
        return url_patterns


class RoutableResourceMixin:
    def _set_request(self, request):
        self.request = request

    def _create_routeset(self, handlers, default_name, name_prefix):
        """We decorate each handler and add the _set_request function, so that before
        the handler is actually called, it stores the request in a class property on
        the class that extends the RoutableResourceMixin. The webargs module checks
        for the existence of this property to determine whether the use_args decorator
        is used on a function or a method. If we don't set it, it will think our
        methods are ordinary functions and mix up the self and request parameters."""

        def add_request_registration(handler_function):
            def set_request_and_handle(request, *args, **kwargs):
                self._set_request(request)
                return handler_function(request, *args, **kwargs)

            return set_request_and_handle

        routeset = RouteSet(name_prefix)
        for handler, data in handlers.items():
            if hasattr(self, handler):
                handle_func = getattr(self, handler)
                routeset.add_route(
                    data.get('name', default_name),
                    data['method'],
                    add_request_registration(handle_func),
                )
        return routeset

    def get_list_handlers(self):
        return {
            'create': {'method': 'POST'},
            'index': {'method': 'GET'},
            'new': {'method': 'GET', 'name': 'create-form'},
        }

    def get_item_handlers(self):
        return {
            'edit': {'method': 'GET', 'name': 'edit-form'},
            'show': {'method': 'GET'},
            'delete': {'method': 'DELETE'},
            'update': {'method': 'PUT'},
        }

    def list_urls(self, prefix=None):
        handlers = self.get_list_handlers()
        return self._create_routeset(handlers, 'list', prefix).urls

    def item_urls(self, prefix=None):
        handlers = self.get_item_handlers()
        return self._create_routeset(handlers, 'item', prefix).urls
