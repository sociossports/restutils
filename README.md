# README #

## REST utils provides the following features for Django based projects ##

* Resource-based routing
* [HAL](http://stateless.co/hal_specification.html) resource representations
* Middleware for easily processing JSON content in PUT or POST requests
* Middleware for returning [vnd.error](https://github.com/blongden/vnd.error) responses
* Lots of utilities functions to reduce "red tape" code

## Installation ##

Add this line to your requirements.txt file:

```
hg+https://bitbucket.org/plac/restutils/@1.0#egg=restutils
```


## Usage ##

### Routing ###

Provides Rails-like routing for REST resources. Create a view class that will serve your resource representations:

```
#!python

from restutils.router import RoutableResourceMixin

class PersonView(RoutableResourceMixin):

    def index(self, request):
        # return an HTTP response with a list of Persons
        pass

    def show(self, request, person_id):
        # return an HTTP response with a single Person
        pass


person_view = PersonView()
```

And add routes to your urls.py like this:

```
#!python
from xxx.xxx import person_view

urlpatterns = patterns('',
    url(r'^persons/(?P<person_id>\d+)/',
        include(person_view.item_urls(prefix='person')),
    url(r'^persons/',
        include(person_view.list_urls(prefix='person')),
)

```
This will automatically generate urls for the list-based methods of your resource (/persons/) and the item-based methods of your resource (/persons/1/) that correspond to the methods that you implemented in the view class. If you only implement item-based methods in your class, you don't need to add a route for the list_urls and vice-versa. A class that extends the RoutableResourceMixin can implement the following methods:

|Class method|Corresponds to HTTP method|on URL example|in URL patterns|URL name (for reversing)|Purpose|
|---|---|---|---|---|---|
|index|GET|/persons/|list_urls()|[prefix]-list|Show a list of all items|
|show|GET|/persons/1/|item_urls()|[prefix]-item|Show the details of a single item|
|create|POST|/persons/|list_urls()|[prefix]-list|Create a new item|
|update|PUT|/persons/1/|item_urls()|[prefix]-item|Update an existing item|
|edit|GET|/persons/1/edit/|item_urls()|[prefix]-edit-form|The edit form to update an item|
|new|GET|/persons/new/|list_urls()|[prefix]-create-form|The form to create a new item|
|delete|GET|/persons/1/|item_urls()|[prefix]-item|Delete an item|

To route an additional HTTP method to either the list_urls() or the item_urls(), you can override the corresponding method of the view class that implements RoutableResourceMixin: get_list_handlers or get_item_handlers as follows:

```
#!python
from restutils.router import RoutableResourceMixin

class PersonView(RoutableResourceMixin):

    def get_list_handlers(self):
        # Add a PUT operation to the list url to replace the whole list at once
        handlers = super().get_list_handlers()
        handlers['replace_all'] = {'method': 'PUT'}
        return handlers

    def replace_all(self, request):
        pass

```
If you do not want to route an additional HTTP method through the list or item urls, but want to route a new view method to a different url (for example to implement the "overloaded POST" anti-pattern), you can just use normal Django routing for that:

```
#!python
from restutils.router import RoutableResourceMixin

class PersonView(RoutableResourceMixin):

    def do_something(self, request, person_id):
        # do something weird to the person
        pass
```
urls.py:
```
#!python
from xxx.xxx import person_view

urlpatterns = patterns('',
    url(r'^persons/(?P<person_id>\d+)/do_something/',
        person_view.do_something),
)

```

### HAL representation ###
JSON serializable hypermedia resource representation in the [HAL](http://stateless.co/hal_specification.html) format.

```
#!python
from django.http import HttpResponse

from restutils.hal import Representation, Link

def view(request):
    r = new Representation(request)
    r.add_property('name', 'my name')
    r.add_link('self', Link(href='http://....', title='Self link'))
    # shortcut - when you pass a string instead of a Link object, the string is used as link href:
    r.add_link('parent', 'http://...')
    r.add_object('cr:item', other_representation)
    return HttpResponse(r.to_json(), content_type='application/hal+json')
```
You can define curies by hand using the add_curie method, but you can also define a subclass of the Representation that predefines them. A curies definition will then automatically be added when you use one in a link relation:
```
#!python
from restutils.hal import Representation

class MyRepresentation(Representation):
    curies = {'cr': '/static/docs/{rel}.html'}
```

### Returning json responses ###
Returning a json HttpResponse from a view is easier with the @json_view decorator:

```
#!python
from restutils.decorators import json_view

@json_view
def view(request):
   return {'property_1': 'some value', 'property_2': 42}
```
If the returned object has a to_json() method, this will be used for serialization. If it doesn't, then the decorator will feed the returned object to json.dumps(). By default, the http response code is 200. If you want something else, return the response code as the second element:

```
#!python
from restutils.decorators import json_view

@json_view
def view(request):
   return some_data, 201
```
To combine decorators, for example for caching, you can use django.utils.decorators.method_decorator:

```
#!python

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from restutils.decorators import json_view

@method_decorator(cache_page(60))
@json_view
def view(request):
   return some_data
```
### Processing POST/PUT data in json format ###

```
#!python

from restutils.utils import decode_json_data

def process_post(request):
    data = decode_json_data(request)
    person_id = data['person_id']
```
You can also use the restutils.middleware.RequestDataMiddleware to add a "data" property to the request. This property will contain the decoded json payload.
```
#!python
def process_post(request):
    person_id = request.data['person_id']
```
Both solutions (decode_json_data and the RequestDataMiddleware) will throw a restutils.exceptions.BadRequest exception when the json payload could not be decoded.

### Returning errors ###

The restutils.middleware.VndErrorMiddleware allows you to raise exceptions that are then translated to a [vnd.error](https://github.com/blongden/vnd.error) response and shown to the client. It will catch exceptions that are derived from restutils.exceptions.ApiError. The restutils.exceptions module contains a few ready-made exceptions that all extend restutils.exceptions.ApiError: BadRequest (returns by default status 400), Forbidden (returns by default status 403) and NotFound (returns by default status 404). Unhandled ObjectDoesNotExist exceptions from the Django ORM also also caught and converted to restutils.exceptions.NotFound. Messages and status codes are optional (they are set to sensible defaults), but can be overridden.

```
#!python

from restutils.exceptions import BadRequest

def view(request):
    if user_did_something_wrong:
        raise BadRequest('You did something wrong')
    elif we_did_something_wrong:
        raise ApiError('We did something wrong', 500)
    else:
        raise NotFound()
```



### "Magic" url reversing ###
When reversing a django route, you need to fill in all the kwargs. This can get very verbose: reverse('route-name', kwargs={'person_id':12, 'profile_id':34, 'pet_id':56}). The restutils.magicreverse.MagicReverser class makes this easier by already filling in the kwargs from the "current" url:

```
#!python
from restutils.magicreverse import MagicReverser

# handles the url /view/person/12/
def view(request, person_id):
    reverser = MagicReverser(request):
    # reverses the route for /view/person/12/profile/34/pet/56
    # note how you can leave out the person_id:
    url = reverser.rev('route-name', profile_id=34, pet_id=56)

```
You can also use the restutils.middleware.MagicReverseMiddleware. It adds a "rev" method to the request that does the same "magic" reversion:

```
#!python
# handles the url /view/person/12/
def view(request, person_id):
    # reverses the route for /view/person/12/profile/34/pet/56
    # note how you can leave out the person_id:
    url = request.rev('route-name', profile_id=34, pet_id=56)

```
### Parsing resource URLS ###
To parse a URI and extract the kwargs, use restutils.utils.extract_from_uri. For example, consider the following url route:

```
#!python

urlpatterns = patterns('',
    url(r'^persons/(?P<person_id>\d+)/profiles/(?P<profile_id>\d+)/',
        view_function),
)

```
Then you can extract the kwargs from a URI string as follows:
```
#!python
from restutils.utils import extract_from_uri

extract_from_uri('http://api.example.com/persons/12/profiles/34/', ['person_id', 'profile_id'])
# => {'person_id': 12, 'profile_id': 34}

extract_from_uri('http://api.example.com/persons/12/profiles/34/', 'person_id')
# => 12
```
Note that the function returns a dict when multiple kwargs are requested, but only the kwarg value when a single kwarg is requested.

### Returning ISO dates ###
Convert a datetime to an ISO 8601 date string. If the datetime is naive, it will apply the timezone in settings.TIME_ZONE. If no zone has been set, it defaults to UTC:

```
#!python
from datetime import datetime

from restutils.utils import iso_date

iso_date(datetime.now())
```