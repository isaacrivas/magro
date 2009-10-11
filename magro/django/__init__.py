"""
This module can be used to enable magro templates through the
django templates engine.

This script will replace the django Template class with an
implementation of it using magro.

To make this available just import the magro.django package.

"""
from django.http import HttpResponse, Http404
from django.conf import settings
import magro.parser
import magro.env
from magro.context import Context

import django.template as original

class ResponseMiddleware:
    """
    Django Middleware for processing all responses as magro templates.
    """
    def __init__(self):
        pass
    
    def process_response(self, request, response):
        "Processes all the responses marked by an X-MAGRO property"
        if 'X-MAGRO' in response:
            prepare_env()
            response.content =  magro.parser.parse( response.content )
        return response

class FalseNodeList(list):
    "Dummy node list used by this the Template class of this module."
    def __init__(self, target):
        self.target = target

    def render(self, context):
        "Evaluates the magro templates passed on construction."
        while hasattr( context, 'dicts' ):
            context = context.dicts[0]
        self.target.rootnode.eval(Context(context))
        
class Template( object ):
    """Replace the django Template class with this one. Can be used with
    standard django templates or with magro files."""
    def __init__(self, template_string, origin=None, name='<Unknown Template>'):
        self.original = None
        if '{%' in template_string:
            self.original = OriginalTemplateClass( template_string, origin, name )
        else:
            self.rootnode = magro.parser.compile( template_string )
        self.name = name

    def get_nodelist(self):
        "Creates a nodelist for django code that uses this function."
        if self.original:
            return self.original.nodelist
        else:
            return FalseNodeList( self )
        
    nodelist = property(get_nodelist)
        
    def __iter__(self):
        if self.original:
            yield self.original.__iter__()
        else:
            for node in self.rootnode.code:
                for subnode in node.code:
                    yield subnode

    def render(self, context):
        "Display stage -- can be called many times"
        if self.original:
            return self.original.render(context)
        else:
            while hasattr( context, 'dicts' ):
                context = context.dicts[0]
            return self.rootnode.eval(Context(context))


OriginalTemplateClass = original.Template
original.Template = Template
