

class Context( dict ):
    def __init__(self, values={}):
        dict.__init__(self)
        if values:
            self.update(values)
    
    def copy(self):
        return Context( self )
        
    def has_key( self, key ):
        try:
            self[key]
            return True
        except:
            return False
            
    def __getitem__(self,key):
        k = key
        value = None
        while k:
            try:
               value = dict.__getitem__( self, k )
               break
            except KeyError:
                if '.' in k:
                    k = k.rsplit('.',1)[0]
                else:
                    raise

        if k == key: return value

        parts = key[len(k)+1:].split('.')
        for p in parts:
            value = getattr( value, p )
            if hasattr(value,'__call__'):
                value = value()
        return value

        
