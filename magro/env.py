"""This module contains the objects used for the
configuration of the magro engine.

path is a list of search paths where magro template libraries can be found.
settings is a dictionary containing the string values that should be
available in the context for all templates.

"""
import os

__all__ = [ 'path', 'settings', 'searchfile' ]

PATHVARNAME = 'MAGRO_PATH'
path = ['.']
settings = {}

if os.environ.has_key(PATHVARNAME):
    PATHVAR = os.environ[PATHVARNAME]
    for path_entry in PATHVAR.split( os.pathsep ):
        path.append( path_entry )

        
def searchfile( filename ):
    """
    Find the fullpath of a file by searching in all registered
    paths.
    """
    for _path in path:
        fullname = _path + os.sep + filename
        if os.path.exists( fullname ):
            return os.path.abspath(fullname)
    return None
