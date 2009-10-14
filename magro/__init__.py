"Magro Templates main package"

from magro.parser import MagroParser
import magro.ast as ast

__all__ = [ 'parse', 'compile', 'ast' ]

_GLOBAL_PARSER = MagroParser()

def parse( the_input, context=None ):
    "Compiles and evaluates a template to a given context."
    root_node = _GLOBAL_PARSER.compile( the_input )
    return root_node.eval( context or {} )
    
def compile( the_input ):
    "Compiles a template."
    return _GLOBAL_PARSER.compile( the_input )
