import json
import collections

from restutils.lib.uri_tools import full_uri

# http://www.iana.org/assignments/link-relations/link-relations.xhtml
default_titles = {
    'profile': 'Documentation for this resource',
    'self': 'URI of this resource',
    'collection': 'Back to the collection',
    'create-form': 'Form to create a new resource in this collection',
    'first': 'First page',
    'last': 'Last page',
    'next': 'Next page',
    'previous': 'Previous page',
    'prev': 'Previous page',
}


def contains_curie(rel):
    return ':' in rel


def contains_template(rel):
    return '{' in rel and '}' in rel


def _object_data(item):
    return None if item is None else item.data


class Link:

    def set_value(self, key, value):
        if value is not None:
            self.data[key] = value

    def __init__(self, href=None, templated=None, media_type=None,
                 deprecation=None, name=None, profile=None, title=None,
                 hreflang=None):
        assert href is not None
        self.data = collections.OrderedDict()
        if contains_template(href):
            templated = True
        self.set_value('href', href)
        self.set_value('templated', templated)
        self.set_value('type', media_type)
        self.set_value('name', name)
        self.set_value('profile', profile)
        self.set_value('title', title)
        self.set_value('hreflang', hreflang)


class Representation:

    curies = collections.OrderedDict()

    def __init__(self, request):
        self.data = collections.OrderedDict()
        self.request = request

    def has_curie(self, name):
        links = self.data.get('_links')
        if not links:
            return False
        curies = links.get('curies')
        if not curies:
            return False
        for item in curies:
            if item['name'] == name:
                return True
        return False

    def add_curie(self, name, href):
        if not self.has_curie(name):
            self.add_link_list('curies', Link(
                href=full_uri(self.request, href),
                name=name,
                # title='Compact URI for namespacing',
            ))

    def add_curie_for_rel(self, rel):
        name = rel[:rel.index(':')]
        href = self.curies.get(name)
        if href:
            self.add_curie(name, href)

    def link_to_hal(self, link_object):
        if isinstance(link_object, Link):
            link_data = link_object.data
        else:
            link_data = {'href': link_object}
        link_data['href'] = full_uri(self.request, link_data['href'])
        return link_data

    def _set_link(self, rel, value):
        if contains_curie(rel):
            self.add_curie_for_rel(rel)
        self.data['_links'] = self.data.get(
            '_links', collections.OrderedDict())
        current_items = self.data['_links'].get(rel)
        if type(current_items) is list:
            value += current_items
        self.data['_links'][rel] = value

    def add_link_list(self, rel, link_list):
        if type(link_list) is not list:
            link_list = [link_list]
        self._set_link(rel, [self.link_to_hal(link) for link in link_list])

    def add_link(self, rel, link_object):
        link_data = self.link_to_hal(link_object)
        if not link_data.get('title'):
            default_title = default_titles.get(rel)
            if default_title:
                link_data['title'] = default_title
        self._set_link(rel, link_data)

    def _set_object(self, rel, value):
        if contains_curie(rel):
            self.add_curie_for_rel(rel)
        self.data['_embedded'] = self.data.get(
            '_embedded', collections.OrderedDict())
        self.data['_embedded'][rel] = value

    def move_curies_to_top(self, embedded_object):
        if embedded_object is None:
            return
        if(embedded_object.data.get('_links') and
           embedded_object.data['_links'].get('curies')):
            curies = embedded_object.data['_links']['curies']
            del(embedded_object.data['_links']['curies'])
            # remove _links if it is empty after removing the curie link
            if len(embedded_object.data['_links']) == 0:
                del(embedded_object.data['_links'])
            for curie in curies:
                if not self.has_curie(curie['name']):
                    self.add_curie(curie['name'], curie['href'])

    def add_object_list(self, rel, object_list):
        if type(object_list) is not list:
            object_list = [object_list]
        for value in object_list:
            self.move_curies_to_top(value)
        self._set_object(rel, [_object_data(item) for item in object_list])

    def add_object(self, rel, value):
        self.move_curies_to_top(value)
        self._set_object(rel, _object_data(value))

    def add_property(self, name, value):
        self.data[name] = value

    def to_json(self):
        return json.dumps(self.data, indent=4, ensure_ascii=False)

    def to_dict(self):
        return self.data
