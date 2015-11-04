import json
import pytz
from urllib.parse import urlparse

from django.conf import settings
from django.core.urlresolvers import resolve
from django.http import Http404

from restutils.exceptions import BadRequest


def iso_date(date):
    if date is not None:
        # http://stackoverflow.com/questions/5802108/how-to-check-if-a-datetime-object-is-localized-with-pytz
        is_naive = date.tzinfo is None or date.tzinfo.utcoffset(date) is None
        if is_naive:
            if hasattr(settings, 'TIME_ZONE'):
                date = pytz.timezone(settings.TIME_ZONE).localize(date)
            else:
                return date.strftime("%Y-%m-%dT%H:%M:%SZ")        
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