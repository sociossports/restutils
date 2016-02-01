from django.http import HttpResponse
from django.conf import settings
from django.core.signals import got_request_exception
from django.core.exceptions import ObjectDoesNotExist

from restutils.hal import Representation
from restutils.exceptions import ApiError, NotFound
from restutils.lib.json_as_html import create_html
from restutils.lib.content_negotiation import best_content_type
from restutils.magicreverse import MagicReverser
from restutils.utils import decode_json_data


def data(self):
    if not hasattr(self, '_data_dict'):
        self._data_dict = decode_json_data(self)
    return self._data_dict


class RequestDataMiddleware(object):

    def process_request(self, request):
        if request.method in ('PUT', 'POST'):
            request.__class__.data = property(data)
        return None


class MagicReverseMiddleware(object):

    def process_request(self, request):
        reverser = MagicReverser(request)
        request.__class__.rev = reverser.rev
        return None


class VndErrorMiddleware(object):

    def process_exception(self, request, exception):

        if issubclass(type(exception), ObjectDoesNotExist):
            exception = NotFound(str(exception))
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

        # Make sure the exception signal is fired for Sentry, but don't
        # bother it with anything that's not a server error
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
