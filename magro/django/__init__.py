from django.http import HttpResponse, Http404
from django.conf import settings
import magro.parser
import magro.env
from magro.context import Context

import django.template as original

class ResponseMiddleware:
    def process_response(self, request, response):
        if 'X-MAGRO' in response:
            prepare_env()
            response.content =  magro.parser.parse( response.content )
        return response

class FalseNodeList(list):
    def __init__(self,target):
        self.target = target

    def render(self, context):
        while hasattr( context, 'dicts' ):
            context = context.dicts[0]
        self.target.rootnode.eval(Context(context))
        
class Template( object ):

    def __init__(self, template_string, origin=None, name='<Unknown Template>'):
        self.original = None
        if '{%' in template_string:
            self.original = OriginalTemplateClass( template_string, origin, name )
        else:
            self.rootnode = magro.parser.compile( template_string )
        self.name = name

    def get_nodelist(self):
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
