def full_uri(request, path):
    if path is not None:
        return request.build_absolute_uri(path).replace(
            '%7B','{').replace('%7D','}')