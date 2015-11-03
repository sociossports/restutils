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
This will automatically generate urls for the list-based methods of your resource (/persons/) and the item-based methods of your resource (/persons/1) that correspond to the methods that you implemented in the view class. If you only implement item-based methods in your class, you don't need to add a route for the list_urls and vice-versa. A class that implements the RoutableResourceMixin can use the following methods:

|Class method|Corresponds to HTTP method|on URL example|in URL patterns|URL name (for reversing)|Purpose|
|---|---|---|---|---|---|
|index|GET|/persons/|list_urls()|[prefix]-list|Show a list of all items|
|show|GET|/persons/1|item_urls()|[prefix]-item|Show the details of a single item|
|create|POST|/persons/|list_urls()|[prefix]-list|Create a new item|
|update|PUT|/persons/1|item_urls()|[prefix]-item|Update an existing item|
|edit|GET|/persons/1/edit/|item_urls()|[prefix]-edit-form|The edit form to update an item|
|new|GET|/persons/new/|list_urls()|[prefix]-create-form|The form to create a new item|
|delete|GET|/persons/1|item_urls()|[prefix]-item|Delete an item|

To route an additional HTTP method to either the list_urls() or the item_urls(), you can override the corresponding method of the view class that implements RoutableResourceMixin: get_list_handlers or get_item_handlers as follows:

```
#!python
from restutils.router import RoutableResourceMixin

class PersonView(RoutableResourceMixin):

    def get_list_handlers(self):
        # Add a PUT operation to the list url to replace the whole list at once
        handlers = super().get_list_handlers()
        handlers['replace_all'] = {'method': 'PUT', 'name': 'list'}
        return handlers

    def replace_all(self, request):
        pass

```
The "name" key should be set to either 'list' for list-type urls (when overriding get_list_handlers) and to 'item' for item-type urls (when overriding get_item_handlers). If you do not want to route an additional HTTP method through the list or item urls, but want to route a new view method to a different url (for example to implement the "overloaded POST" anti-pattern), you can just use normal Django routing for that:

```
#!python
from restutils.router import RoutableResourceMixin

class PersonView(RoutableResourceMixin):

    def do_something(self, request, person_id):
        # do something weird to the person
        pass
```

```
#!python
from xxx.xxx import person_view

urlpatterns = patterns('',
    url(r'^persons/(?P<person_id>\d+)/do_something/',
        person_view.do_something),
)

```

### HAL representation ###

### Returning json responses ###

### Processing POST/PUT data ###

### Returning errors ###

### "Magic" url reversing ###

### Parsing resource URLS ###

### Returning ISO dates ###