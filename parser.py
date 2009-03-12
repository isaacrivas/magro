from lexer import *
from ast import *
import ply.yacc as yacc
import env


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
    importfile( p[2], p.parser.context )
    
def p_definition(p):
    "definition : DEF SYMBOL paramdefs ':' callsorblock"
    node = DefNode( name=p[2], params=p[3], code=p[5])
    p.parser.context[ node.name ] = node
    if ( hasattr(p.parser,'currentmodule') ):
        p.parser.context[ p.parser.currentmodule+'.'+node.name ] = node
    p[0] = node

def p_typerenderer(p):
    "typerenderer : '@' SYMBOL paramdefs ':' callsorblock"
    node = TypeDefNode( name=p[2], params=p[3], code=p[5] )
    p.parser.context[ '@%s'%(node.name,) ] = node
    p[0] = node
    
def p_block(p):
    'block : INDENT calls DEDENT'
    p[0] = p[2]
    
def p_calls(p):
    """calls : calls call
             | empty"""
    if len(p) == 3:
        p[0] = extendorappend( p[1], p[2] )
    else:
        p[0] = []

def p_call(p):
    """call : fullcall
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
            | cycle
            | simplecall
            | pycode"""
    p[0] = p[1]
    
def p_string(p):
    "string : STRING"
    p[0] = StringNode(p[1])

def p_implicit(p):
    "implicit : IMPLICIT"
    p[0] = ImplicitNode(p[1])
    
def p_cycle(p):
    "cycle : '[' exprs ']' callparams"
    p[0] = CycleNode( params=p[4], code=p[2] )

def p_simplecall(p):
    'simplecall : SYMBOL callparams'
    p[0] = CallNode( name=p[1], params=p[2] )

def p_pycode(p):
    'pycode : PYCODE'
    p[0] = PycodeNode( code=p[1], globals=p.parser.globals )

def p_fullcall(p):
    "fullcall : SYMBOL callparams ':' callsorblock"
    p[0] = CallNode( name=p[1], params=p[2], contents=p[4] )

def p_callsorblock(p):
    """callsorblock : EOL block
                    | exprs EOL"""
    if hasattr(p[1],'__iter__'):
        p[0] = p[1]
    else:
        p[0] = p[2]
    
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
        raise SyntaxError( "Error at token %s"%(p, ) )
    else:
        raise SyntaxError( "EOF reached prematurely" )

#Public interface

def compile(input):
    parser = yacc.yacc()
    parser.context = {}
    parser.globals = {}
    return parser.parse( tokenfunc=tokenizer(input) )

def parse( input ):
    root = compile(input)
    return root.eval()

def importfile( filename, context ):
    fullpath = env.searchfile( filename )
    if fullpath:
        f = open( fullpath )
        text = f.read()
        f.close()

        pr = yacc.yacc()
        pr.context = context
        pr.globals = {}
        pr.currentmodule = filename
        pr.parse( tokenfunc=tokenizer(text) )
    else:
        print "WARNING: %s file not found"%(filename,)
        
def extendorappend(l1,l2):
    if isinstance(l2,list):
        l1.extend(l2)
    else:
        l1.append(l2)
    return l1
