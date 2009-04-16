from django.http import HttpResponse, Http404
from django.conf import settings
import magro.parser
import magro.env
from magro.context import Context

_templates_cache = {}
_env_prepared = False

class ResponseMiddleware:
    def process_response(self, request, response):
        if 'X-MAGRO' in response:
            prepare_env()
            response.content =  magro.parser.parse( response.content )
        return response

class TemplateNotFound(Exception):
    pass

def render_to_response( templatename, context, **kwargs):
    global _templates_cache
    """
    Returns a HttpResponse whose content is filled with the result of calling
    the specified magro template with the passed arguments.
    """
    httpresponse_kwargs = {'mimetype': kwargs.pop('mimetype', None)}
    
    response = ''
    template = None
    
    prepare_env()
    fullpath = magro.env.searchfile( templatename )
    if fullpath:
        try:
            template = _templates_cache[ fullpath ]
            print 'Read %s from cache'%(fullpath,)
        except KeyError:
            print 'Compiling %s'%(fullpath,)
            f = open( fullpath )
            templatecode = f.read()
            f.close()
            template = magro.parser.compile( templatecode )
            _templates_cache[ fullpath ] = template
    else:
        raise TemplateNotFound( templatename )
    
    if template:
        response = template.eval( Context( context ) )
    
    return HttpResponse(response, **httpresponse_kwargs)

def prepare_env():
    global _env_prepared
    if _env_prepared: return
    print 'Preparing magro environment'
    magro.env.path.extend( settings.TEMPLATE_DIRS )
    _env_prepared = True
