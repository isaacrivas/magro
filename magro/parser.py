"Magro's parser using ply"
from magro.lexer import *
from magro.ast import *
import ply.yacc as yacc
import os
import stat

def p_program(p):
    'program : statements'
    p[0] = RootNode( code=p[1], defs=p.parser.context )
    
        

def p_statements(p):
    """statements : statements statement
                  | empty"""
    if len(p) == 3:
        if (p[2]):
            p[0] = extendorappend( p[1], p[2] )
        else:
            p[0] = p[1]
    else:
        p[0] = []

def p_statement(p):
    """statement : call
                 | definition
                 | typerenderer
                 | import
                 | nop"""
    p[0] = p[1]

def p_import(p):
    "import : IMPORT STRING EOL"
    p.parser.magro_parser.import_file( p[2], p.parser.context )
    
def p_definition(p):
    "definition : DEF SYMBOL paramdefs ':' callsorblock"
    node = DefNode( name=p[2], params=p[3], code=p[5])
    p.parser.context[ DEF_PREFIX+node.name ] = node
    if ( hasattr(p.parser,'currentmodule') ):
        p.parser.context[ DEF_PREFIX+p.parser.currentmodule+'.'+node.name ] = node
    p[0] = node

def p_typerenderer(p):
    "typerenderer : '@' SYMBOL paramdefs ':' callsorblock"
    node = TypeDefNode( name=p[2], params=p[3], code=p[5] )
    p.parser.context[ '@%s' % (node.name,) ] = node
    p[0] = node
    
def p_block(p):
    'block : INDENT calls DEDENT'
    p[0] = BlockNode( p[2], p[1] )
    
def p_calls(p):
    """calls : calls call
             | empty"""
    if len(p) == 3:
        p[0] = extendorappend( p[1], p[2] )
    else:
        p[0] = []

def p_call(p):
    """call : fullcall
            | cyclecall
            | exprs EOL"""
    p[0] = p[1]

def p_exprs(p):
    """exprs : exprs expr
             | expr"""
    if len(p) == 3:
        p[0] = p[1]
        p[0].append(p[2])
    else:
        p[0] = [p[1]]

def p_expr(p):
    """expr : string
            | implicit
            | simplecall
            | pycode"""
    p[0] = p[1]
    
def p_string(p):
    "string : STRING"
    p[0] = StringNode(p[1])

def p_implicit(p):
    "implicit : IMPLICIT"
    p[0] = ImplicitNode(p[1])

def p_simplecall(p):
    'simplecall : SYMBOL callparams'
    p[0] = CallNode( name=p[1], params=p[2] )

def p_pycode(p):
    'pycode : PYCODE'
    p[0] = PycodeNode( code=p[1], globals=p.parser.globals )

def p_fullcall(p):
    "fullcall : SYMBOL callparams ':' callsorblock"
    p[0] = CallNode( name=p[1], params=p[2], contents=p[4] )

def p_cyclecall(p):
    "cyclecall : cycleparams ':' callsorblock elseblock"
    p[0] = CycleNode( params=p[1], code=p[3], elsecode=p[4] )
    
def p_callsorblock(p):
    """callsorblock : EOL block
                    | exprs EOL"""
    if hasattr(p[1],'__iter__'):
        p[0] = BlockNode(p[1])
    else:
        p[0] = p[2]

def p_elseblock(p):
    """elseblock : ':' exprs EOL
                 | ':' EOL block
                 | ':' cyclecall
                 | empty"""
    if len(p) > 2:
        if hasattr(p[2],'__iter__'):
            p[0] = BlockNode(p[2])
        elif len(p) > 3:
            p[0] = p[3]
        else:
            p[0] = BlockNode([p[2]])
    else:
        p[0] = None

    
def p_paramdefs(p):
    """paramdefs : '(' paramnames ')'
                 | '(' ')'"""
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = []

def p_paramnames(p):
    """paramnames : paramnames ',' paramname
                  | paramname"""
    if len(p) == 4:
        p[0] = extendorappend( p[1], p[3] )
    else:
        p[0] = [p[1]]

def p_paramname(p):
    """paramname : SYMBOL '=' STRING
                 | SYMBOL"""
    if len(p) == 4:
        p[0] = ParamNode( p[1], StringNode(p[3]) )
    else:
        p[0] = ParamNode( p[1], None )

def p_cycleparams(p):
    "cycleparams : '[' paramvalues ']'"
    p[0] = p[2]

def p_callparams(p):
    """callparams : '(' paramvalues ')'
                  | empty"""
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = []
    
def p_paramvalues(p):
    """paramvalues : paramvalues ',' paramvalue
                   | paramvalue"""
    if len(p) == 4:
        p[0] = extendorappend( p[1], p[3] )
    else:
        p[0] = [p[1]]

def p_paramvalue(p):
    """paramvalue : SYMBOL '=' paramexpr
                  | paramexpr"""
    if len(p) == 4:
        p[0] = ParamNode( p[1], p[3] )
    else:
        p[0] = ParamNode( None, p[1] )

def p_paramexpr(p):
    """paramexpr : exprs
                 | group"""
    if hasattr(p[1],'__iter__'):
        if len(p[1]) > 1:
            p[0] = BlockNode(p[1])
        else:
            #it might be a single expression that evaluates to an array, which will be automatically expanded on evaluation.
            p[0] = p[1][0]
    else:
        p[0] = p[1]
    
def p_group(p):
    "group : '(' paramvalues ')'"
    p[0] = GroupNode( p[2] )
    
def p_empty(p):
    'empty :'
    pass

def p_nop(p):
    'nop : EOL'
    pass

def p_error(p):
    if p:
        msg = "Error at token %s" % (p, )
    else:
        msg = "EOF reached prematurely"
    print msg
    raise SyntaxError( msg )

#Public interface

class MagroParser(object):
    "Used for creating templates."
    def __init__( self, loader ):
        self.loader = loader
        self.parser = yacc.yacc()
        self.parser.magro_parser = self

    def compile(self, the_input):
        "Compiles a template into an AST RootNode."
        self.parser.context = {}
        self.parser.globals = {}
        return self.parser.parse( tokenfunc=tokenizer(the_input) )
    
    def import_file( self, template_id, context ):
        "Imports a template file given the name of the file."
        if self.loader.is_dirty( template_id ):
            template_source = self.loader.get_source( template_id )
            
            myctx = {}
            temp_yacc = yacc.yacc()
            temp_yacc.magro_parser = self
            temp_yacc.context = myctx
            temp_yacc.globals = {}
            temp_yacc.currentmodule = template_id
            temp_yacc.parse( tokenfunc=tokenizer(template_source) )
            
            context.update( myctx )
            self.loader.update( template_id, myctx )
        else:
            cached = self.loader.get_current( template_id )
            if cached:
                context.update( cached )    
            else:
                print "WARNING: %s file not found" % (template_id,)
        
def extendorappend( the_list, list_or_single):
    """Extends the list of the first argument using the second argument, which
    can be another list or a single element."""
    if isinstance(list_or_single, list):
        the_list.extend(list_or_single)
    else:
        the_list.append(list_or_single)
    return the_list
