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
This will automatically generate urls for the list-based view of your resource (/persons/) and the item-based view of your resource (/persons/1) that correspond to the methods that you implemented in the view class. A class that implements the RoutableResourceMixin can use the following methods:

|Method name|HTTP method|URL patterns|URL name (for reversing)|URL example|Purpose|
|---|---|---|---|---|---|
|index|GET|list_urls()|[prefix]-list|/persons/|Show a list of all items|
|show|GET|item_urls()|[prefix]-item|/persons/1|Show the details of a single item|
|create|POST|list_urls()|[prefix]-list|/persons/|Create a new item|
|update|PUT|item_urls()|[prefix]-item|/persons/1|Update an existing item|
|edit|GET|item_urls()|[prefix]-edit-form|/persons/1/edit/|The edit form to update an item|
|new|GET|list_urls()|[prefix]-create-form|/persons/new/|The form to create a new item|
|delete|GET|item_urls()|[prefix]-item|/persons/1|Delete an item|



### HAL representation ###

### Returning json responses ###

### Processing POST/PUT data ###

### Returning errors ###

### "Magic" url reversing ###

### Parsing resource URLS ###

### Returning ISO dates ###