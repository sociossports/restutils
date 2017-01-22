from collections import OrderedDict


fallback_list = OrderedDict([
    ('vnd.error', 'application/vnd.error+json; charset=utf-8'),
    ('hal+json', 'application/hal+json; charset=utf-8'),
    ('json', 'application/json; charset=utf-8'),
    # ('html', 'text/html; charset=utf-8'),
    ('default', 'application/json; charset=utf-8'),
])


def _parse_part(header_part):
    sub_parts = header_part.split(';')
    value = sub_parts.pop(0)
    params = {}
    for param_string in sub_parts:
        param_parts = param_string.split('=')
        # does not fit the 'name=value' pattern, so skip it
        if len(param_parts) != 2:
            continue
        param_parts = [part.strip() for part in param_parts]
        params[param_parts[0]] = param_parts[1]
    return {'value': value, 'params': params,}


def parse(header):
    return [_parse_part(part) for part in header.split(',')]


def best_content_type(optimal, accept_header):
    parsed_header = parse(accept_header)
    # in Python3, keys() and values() are iterable views that cannot be indexed
    ct_keys = list(fallback_list.keys())
    try:
        start_at = ct_keys.index(optimal)
    except ValueError:
        return fallback_list['default']
    for ix, key in enumerate(ct_keys):
        if ix < start_at:
            continue
        for accept in parsed_header:
            if key in accept['value']:
                return fallback_list[key]
    # Nothing found - default to json
    return fallback_list['default']
