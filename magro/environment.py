"""
This module contains the Environment class that should be
used to load and create templates.

"""
import os
import sys
import magro
from magro.loaders import FileSystemLoader
from magro.parser import MagroParser
from magro.context import Context

__all__ = [ 'Environment', 'Template' ]

PATHVARNAME = 'MAGRO_PATH'
DEFAULT_TEMPLATES_LIBRARY_DIR = 'templates'

class Environment( object ):
    """
    Used to obtain templates using a given templates
    loader.
    """
    def __init__( self, loader = None, settings=None ):
        self.path = ['.']
        self.path.extend( [ path + os.sep + DEFAULT_TEMPLATES_LIBRARY_DIR
                           for path in sys.modules['magro'].__path__ ])
        if os.environ.has_key(PATHVARNAME):
            path_value = os.environ[PATHVARNAME]
            for path_entry in path_value.split( os.pathsep ):
                self.path.append( path_entry )

        self.loader = loader or FileSystemLoader( self.path )
        self.parser = MagroParser( self.loader )
        self.settings = settings or {}
        
    def get_template( self, template_id ):
        """
        Load and build a template by its id (path,url,etc.)
        """
        template_code = self.loader.get_source( template_id )
        return Template( template_code, self )


_DEFAULT_ENVIRONMENT = Environment()

class Template( object ):
    """
    Represents a template that can be evaluated many times for
    different context values.
    """
    def __init__( self, template_source, environment=None ):
        self.template_source = template_source
        self.environment = environment or _DEFAULT_ENVIRONMENT
        self._ast = self.environment.parser.compile( template_source )
    
    def render( self, context=None ):
        "Evaluate the template to a given context."
        ctx = Context()
        for key, value in  self.environment.settings.items():
            ctx['settings.'+key] = value
        if context:
            ctx.update( context )
        
        return self._ast.eval( ctx )
        
        