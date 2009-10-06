"""This module provides a dict subclass for use with magro templates.
If the key contains one or more period characters (.) it treats the
key as a series of calls for attributes or functions on an object.
"""

class Context( dict ):
    """Subclass of dict that gives special treatment to key of the form:
    "key(.subkey)+"
    
    If the especified key is not found as is in the dict, it tries to
    obtain an object and attribute pair that matches the key. For example,
    given the key "user.name", it will first try to find the whole key.
    If not found, it will try to find the value for the key "user", and
    obtain its "name" attribute.
    
    If the requested attribute is callable, it will try to call it without
    arguments to obtain the desired value.
    """
    
    def __init__(self, values=None):
        dict.__init__(self)
        if values:
            self.update(values)
    
    def copy(self):
        "Create a shallow copy of this Context."
        return Context( self )
        
    def has_key( self, key ):
        """"Returns True if the key is stored in the dict, or if a
        chain of object.attribute call can be obtained."""
        try:
            self.__getitem__(key)
            return True
        except (KeyError, AttributeError):
            return False
            
    def __getitem__(self, key):
        """Obtain the value for the given key.
        If the key contains one or more period characters, will try to
        find a chain of object.attribute calls that satisfy the key.

        Raises KeyError if the key is not found in any form,
        and AttributeError is a key satisfying the leftmost part of
        an object.attribute call is found, but no attribute or function
        has the name indicated by the right part of the expression.
        """
        k = key
        value = None
        while k:
            try:
                value = dict.__getitem__( self, k )
                break
            except KeyError:
                if '.' in k:
                    k = k.rsplit('.', 1)[0]
                else:
                    raise

        if k == key:
            return value

        parts = key[len(k)+1:].split('.')
        for part in parts:
            value = getattr( value, part )
            if hasattr(value,'__call__'):
                value = value()
        return value

        
