import os

PATHVARNAME='MAGRO_PATH'
path=['.']
settings={}

if PATHVARNAME in os.environ:
    pathvar = os.environ[PATHVARNAME]
    for p in pathvar.split( os.pathsep ):
        path.append(p)

        
def searchfile( filename ):
    for p in path:
        fullname = p + os.sep + filename
        if os.path.exists( fullname ):
            return os.path.abspath(fullname)
    return None
