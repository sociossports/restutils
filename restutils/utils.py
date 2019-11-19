import json
from urllib.parse import urlparse
from isodate import datetime_isoformat
from django.conf import settings
from django.urls import resolve
from django.http import Http404
from django.utils.timezone import is_naive, make_aware, get_current_timezone

from restutils.exceptions import BadRequest


def iso_date(date):
    if date is not None:
        if is_naive(date):
            date = make_aware(date, get_current_timezone())
        # NOTE naive formatting generates bad non-iso strings
        # return date.strftime('%Y-%m-%dT%H:%M:%S%z')
        # replaced with real isodate
        return datetime_isoformat(date)


def extract_from_uri(uri, fields):
    if type(uri) != str:
        raise ValueError('URI is not of string type')
    uri_parts = urlparse(uri)
    try:
        parsed_path = resolve(uri_parts.path)
    except Http404:
        raise BadRequest('Invalid URI: '+ uri)

    if type(fields) is list:
        return {field: parsed_path.kwargs[field] for field in fields}
    else:
        return parsed_path.kwargs[fields]


def decode_json_data(request):
    try:
        parsed_body = json.loads(request.body.decode())
    except ValueError:
        raise BadRequest('Error trying to parse body as JSON')
    return parsed_body
