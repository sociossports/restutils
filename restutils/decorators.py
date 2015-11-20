import re
import json
from inspect import ismethod
from functools import wraps

from django.http import HttpRequest, HttpResponse

from restutils.hal import Representation
from restutils.lib.json_as_html import create_html
from restutils.lib.content_negotiation import best_content_type

def _get_request(args):
    try:
        if hasattr(args[0], 'META'):
            return args[0]
        elif hasattr(args[1], 'META'):
            return args[1]
    except IndexError:
        pass

    raise AssertionError("json_view decorator wraps something that doesn't "
                         "look like a view function (request parameter "
                         "missing)")


def json_view(http_handler):
    """Returns a HttpResponse with a json representattion of the function
    result. You can use this on Django views to return json without having to
    use json.dumps() all the time. It also arranges a proper Content-type
    header.

    Usage example:

    @json_view
    def my_view(request):
        return {"key": value}

    The default status code is 200. You can return a different http status code
    as follows:

    @json_view
    def my_view(request):
        return {"key": value}, 201

    For the json serialization, it first checks whether the returned object has
    a "to_json" method. When it does, this is called. Otherwise, it will use
    json.dumps(), which works fine for lists or dictionaries, but will fail for
    custom types.

    The system will inspect the clients HTTP_ACCEPT header to determine the
    proper Content-type header to return. If you return a
    restutils.hal.representation object from the view, it will try to return a
    Content-type header for "application/hal+json".
    When this is not accepted by the client or when another type of object is
    returned, it will use "application/json". When the client explicitely
    requests "text/html", the json will be color coded and embedded in an html
    page.
    """

    @wraps(http_handler)
    def wrapper(*args, **kwargs):
        request = _get_request(args)
        accept_headers = request.META.get('HTTP_ACCEPT', 'application/json')
        output = http_handler(*args, **kwargs)
        try:
            content, status = output
        except:
            content, status = output, 200

        if hasattr(content, 'to_json'):
            content = content.to_json()
        else:
            content = json.dumps(content, indent=4)

        if isinstance(content, Representation):
            content_type = best_content_type('hal+json', accept_headers)
        else:
            content_type = best_content_type('json', accept_headers)

        if 'html' in content_type:
            content=create_html(content)

        response = HttpResponse(content=content, status=status)
        response['Content-Type'] = content_type
        response['Vary'] = 'Accept'

        return response

    return wrapper
