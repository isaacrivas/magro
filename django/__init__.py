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

class Template( object ):
    def __init__(self, template_string, origin=None, name='<Unknown Template>'):
        self.original = None
        if '{%' in template_string:
            self.original = OriginalTemplateClass( template_string, origin, name )
        else:
            self.rootnode = magro.parser.compile( template_string )
        self.name = name

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
            return self.rootnode.eval(context.dicts[0])


OriginalTemplateClass = original.Template
original.Template = Template
