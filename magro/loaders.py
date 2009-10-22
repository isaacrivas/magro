"""
Template loaders that supply the template source given
an id (path, url, etc.)
"""

import os
import stat

class BaseLoader( object ):
    """
    Base class to be extended by loaders. Implements a simple
    cache using a map
    """
    def __init__( self ):
        self.cache = {}
    
    def is_dirty(self, key):
        "Evaluate if the current value of key is newer than the timestamp."
        timestamp = self.get_timestamp( key )
        if not timestamp:
            return False
        if key in self.cache and self.cache[key][0] >= timestamp:
            return False
        return True
    
    def get_current(self, key):
        "Get the current value of a key"
        if key in self.cache:
            return self.cache[key][1]
        return None
        
    def update(self, key, value):
        "Set the current value of a key"
        timestamp = self.get_timestamp( key )
        if timestamp:
            self.cache[key] = (timestamp, value,)
            
    def get_source( self, template_id ):
        "Get the source code of a template."
        raise NotImplementedError('Implement for all subclasses')

    def get_timestamp( self, template_id ):
        "Return the current timestamp of a template if it can be calculated."
        raise NotImplementedError('Implement for all subclasses')


class DummyLoader( BaseLoader ):
    "Mock Loader class for testing"
    def get_source( self, template_id ):
        "Always returns empty string."
        return ""
    def get_timestamp( self, template_id ):
        "Always return None."
        return None


class CompositeLoader( BaseLoader ):
    """
    Used for loading a template by searching on a list of loaders
    in sequence.
    """
    def __init__( self, loaders ):
        BaseLoader.__init__( self )
        self.loaders = loaders
    
    def get_source( self, template_id ):
        "Get the template source by searching on every loader of the list."
        for loader in self.loaders:
            template_source = loader.get_source( template_id )
            if template_source:
                return template_source
        return None
    
    def get_timestamp( self, template_id ):
        "Get the timestamp of the template using the corresponding loader."
        for loader in self.loaders:
            timestamp = loader.get_timestamp( template_id )
            if timestamp:
                return timestamp
        return None

class FileSystemLoader( BaseLoader ):
    """
    Loads templates searching from a list of paths.
    """
    def __init__(self, path=None):
        BaseLoader.__init__( self )
        self.path = path or ['.']
    
    def get_source( self, template_id ):
        "Load a template using its filename as id."
        fullpath = self.search_file( template_id )
        if fullpath:
            template_file = open( fullpath )
            template_source = template_file.read()
            template_file.close()
            return template_source
        return None

    def search_file( self, filename ):
        """
        Find the fullpath of a file by searching in all registered
        paths.
        """
        for path_entry in self.path:
            fullpath = path_entry + os.sep + filename
            if os.path.exists( fullpath ):
                return os.path.abspath(fullpath)
        return None

    def get_timestamp( self, key ):
        "Get the timestamp of the template using the file's modification time."
        fullpath = self.search_file( key )
        if fullpath:
            filestat = os.stat(fullpath)
            return filestat[stat.ST_MTIME]
        return None
