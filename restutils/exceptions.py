"""This file defines several exceptions that can be raised in an http api. The
ApiError class is designed to be serializable in the vnd.error format
(https://github.com/blongden/vnd.error). The
restutils.middleware.VndErrorMiddleware middleware will catch these exceptions,
serialize them to vnd.error and return the proper status code."""


class ApiError(Exception):
    """
    message (REQUIRED)
    For expressing a human readable message related to the current error which
    may be displayed to the user of the api.

    logref (OPTIONAL)
    For expressing a (numeric/alpha/alphanumeric) identifier to refer to the
    specific error on the server side for logging purposes (i.e. a request
    number).

    path (OPTIONAL)
    For expressing a JSON Pointer (RFC6901) to a field in related resource
    (contained in the 'about' link relation) that this error is relevant for.

    help (The 'help' link relation is OPTIONAL.)
    Links to a document describing the error. This has the same definition as
    the help link relation in the HTML5 specification

    describes (The 'describes' link relation is OPTIONAL.)
    Present if this error representation describes another representation of
    the error on the server side. See RFC6892 for further details.

    about (The 'about' link relation is OPTIONAL.)
    Links to a resource that this error is related to. See RFC6903 for further
    details.
    """

    status = 500
    message = 'Internal server error'

    def __init__(self, message=None, status=None, logref=None, path=None,
                 about=None, describes=None, help=None):

        super(ApiError, self).__init__()

        # When the status and message fields are set in the subclasses, then we
        # should avoid to overwrite them with None:
        if status is not None:
            self.status = status
        if message is not None:
            self.message = message

        # The others can be overwritten
        self.logref = logref
        self.path = path
        self.about = about
        self.describes = describes
        self.help = help


class BadRequest(ApiError):
    status = 400
    message = 'Bad Request'


class NotFound(ApiError):
    status = 404
    message = 'Resource not found'


class Forbidden(ApiError):
    status = 403
    message = 'Access denied'
