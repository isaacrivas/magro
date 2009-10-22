"""
This module contains the Environment class that should be
used to load and create templates.

"""
import os
from magro.loaders import FileSystemLoader
from magro.parser import MagroParser
from magro.context import Context

__all__ = [ 'Environment', 'Template' ]

PATHVARNAME = 'MAGRO_PATH'

class Environment( object ):
    """
    Used to obtain templates using a given templates
    loader.
    
    TODO: Include a cache strategy into the configuration.
    """
    def __init__( self, loader = None, settings=None ):
        self.path = ['.']
        if os.environ.has_key(PATHVARNAME):
            path_value = os.environ[PATHVARNAME]
            for path_entry in path_value.split( os.pathsep ):
                self.path.append( path_entry )

        self.loader = loader or FileSystemLoader( self.path )
        self.parser = MagroParser( self.loader )
        self.settings = settings or {}
        
    def get_template( template_id ):
        """
        Load and build a template by its id (path,url,etc.)
        """
        template_code = self.loader.get_source( template_id )
        return Template( template_code, self )


_DEFAULT_ENVIRONMENT = Environment()

class Template( object ):
    def __init__( self, template_source, environment=None ):
        self.template_source = template_source
        self.environment = environment or _DEFAULT_ENVIRONMENT
        self._ast = self.environment.parser.compile( template_source )
    
    def render( self, context=None ):
        ctx = Context()
        for key, value in  self.environment.settings.items():
            ctx['settings.'+key] = value
        if context:
            ctx.update( context )
        
        return self._ast.eval( ctx )
        
        