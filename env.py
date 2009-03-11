import os

PATHVARNAME='MAGRO_PATH'
path=['.']

if os.environ.has_key(PATHVARNAME):
    pathvar = os.environ[PATHVARNAME]
    for p in pathvar.split( os.pathsep ):
        path.append(p)

        
def searchfile( filename ):
    for p in path:
        fullname = p + os.sep + filename
        if os.path.exists( fullname ):
            return os.path.abspath(fullname)
    return None
