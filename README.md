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

Create a class in your view:

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
To link the methods to the routes. A class that implements the RoutableResourceMixin can use the following methods:

|Method name|HTTP method|URL function|Purpose|
|---|---|---|---|
|index|GET|list_urls|   |
|show|GET|item_urls|   |
|create|POST|list_urls|   |
|update|PUT|item_urls|   |
|edit|GET|item_urls|   |
|new|GET|list_urls|   |
|delete|GET|item_urls|   |



### HAL representation ###

### Returning json responses ###

### Processing POST/PUT data ###

### Returning errors ###

### "Magic" url reversing ###

### Parsing resource URLS ###

### Returning ISO dates ###