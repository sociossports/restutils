from urllib.parse import urlparse

from django.conf import settings
from django.core.urlresolvers import resolve
from django.http import Http404

from restutils.exceptions import BadRequest


def iso_date(date):
    if not date:
        return None
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


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
    except:
        raise BadRequest("Error trying to parse body as JSON")
    return parsed_body