"""
This module can be used to enable magro templates through the
django templates engine.

This script will replace the django Template class with an
implementation of it using magro.

To make this available just import the magro.django package.

"""
from django.http import HttpResponse, Http404
from django.conf import settings
from magro import Environment, Template
from magro.context import Context

__all__ = ['ResponseMiddleware','render_to_response']

class ResponseMiddleware:
    """
    Django Middleware for processing all responses as magro templates.
    """
    def __init__(self):
        pass
    
    def process_response(self, request, response):
        "Processes all the responses marked by an X-MAGRO property"
        if 'X-MAGRO' in response:
            env = _init_magro_env()
            template = Template( response.content, env )
            response.content = template.render()
        return response

def render_to_response( template_id, context=None ):
    env = _init_magro_env()
    template = env.get_template( template_id )
    
    ctx = context
    while hasattr( ctx, 'dicts' ):
        ctx = ctx.dicts[0]
    
    return HttpResponse( template.render( Context(ctx) ) )

def render_from_text( template_source, context=None ):
    env = _init_magro_env()
    template = Template( template_source, env )
    return template.render( context )

def _init_magro_env():
    globs = globals()
    if '_MAGRO_ENV' not in globs:
        _MAGRO_ENV = Environment()
        _MAGRO_ENV.loader.path.extend( settings.TEMPLATE_DIRS )
        globs['_MAGRO_ENV'] = _MAGRO_ENV
    return globs['_MAGRO_ENV']
