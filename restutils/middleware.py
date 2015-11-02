import json

from django.http import HttpResponse
from django.conf import settings
from django.core.signals import got_request_exception
from django.core.exceptions import ObjectDoesNotExist

from .hal import Representation
from .exceptions import ApiError, BadRequest, NotFound
from .lib.json_as_html import create_html
from .lib.content_negotiation import best_content_type


def _decode_data(request):
    try:
        parsed_body = json.loads(request.body.decode())
    except:
        raise BadRequest("Error trying to parse body as JSON")
    return parsed_body


def data(self):
    if not hasattr(self, '_data_dict'):
        self._data_dict = _decode_data(self)
    return self._data_dict


class RequestDataMiddleware(object):

    def process_request(self, request):
        if request.method in ('PUT', 'POST'):
            request.__class__.data = property(data)
        return None


class VndErrorMiddleware(object):

    def process_exception(self, request, exception):

        if issubclass(type(exception), ObjectDoesNotExist):
            exception = NotFound()
        if not issubclass(type(exception), ApiError):
            return None

        accept_headers = request.META.get('HTTP_ACCEPT', 'application/json')

        doc = Representation(request)
        doc.add_property('message', exception.message)
        if exception.logref is not None:
            doc.add_property('logref', exception.logref)
        if exception.path is not None:
            doc.add_property('path', exception.path)
        if exception.about is not None:
            doc.add_link('about', exception.about)
        if exception.describes is not None:
            doc.add_link('describes', exception.describes)
        if exception.help is not None:
            doc.add_link('help', exception.help)

        # Make sure the exception signal is fired for Sentry
        if exception.status >= 500:
            got_request_exception.send(sender=self, request=request)

        content_type = best_content_type('vnd.error', accept_headers)

        content = doc.to_json()

        if 'html' in content_type:
            content=create_html(content)

        response = HttpResponse(content=content, status=exception.status)
        response['Content-Type'] = content_type
        response['Vary'] = 'Accept'

        return response