import json
from urllib.parse import urlparse

from django.conf import settings
from django.core.urlresolvers import resolve
from django.http import Http404
from django.utils.timezone import is_naive, make_aware

from restutils.exceptions import BadRequest


def iso_date(date):
    if date is not None:
        if is_naive(date):
            date = make_aware(date)
        return date.strftime("%Y-%m-%dT%H:%M:%S%z")


def extract_from_uri(uri, fields):
    if type(uri) != str:
        raise ValueError("URI is not of string type")
    uri_parts = urlparse(uri)
    try:
        parsed_path = resolve(uri_parts.path)
    except Http404:
        raise BadRequest("Invalid URI: "+ uri)

    if type(fields) is list:
        return {field: parsed_path.kwargs[field] for field in fields}
    else:
        return parsed_path.kwargs[fields]


def decode_json_data(request):
    try:
        parsed_body = json.loads(request.body.decode())
    except ValueError:
        raise BadRequest("Error trying to parse body as JSON")
    return parsed_body
