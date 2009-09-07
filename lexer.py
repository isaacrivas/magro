import re
import ply.lex as lex

reserved ={
   'def' : 'DEF',
   'import' : 'IMPORT',
}

# List of token names.   This is always required
tokens = [
   'SYMBOL',
   'IMPLICIT',
   'STRING',
   'PYCODE',
   'INDENT',
   'DEDENT',
   'EOL',
] + reserved.values()

literals = ":()[]=,@"

t_ignore = ' \t'

def t_comment(t):
    r'^(\#.*\n)+' \
    r'|(?=\n)\#.*\n' \
    r'|\#.*'
    pass

def t_emptylines(t):
    r'^\n+' \
    r'|(?=\n)\s+?(\#.*)?(?=\n)'
    pass

def t_EOL(t):
    r"\n+(?P<indent>[ \t]*)"
    t.lexer.lineno += len(t.value)
    blanks = t.lexer.lexmatch.group("indent")
    processindentation( t.lexer, blanks[:-1] )
    return t
    
def t_SYMBOL(t):
    r'[a-zA-Z0-9._-]+'
    t.type = reserved.get( t.value , 'SYMBOL' )
    return t

def t_IMPLICIT(t):
    r'\$[\$a-zA-Z0-9._-]*'
    return t

def t_longSTRING(t):    
    r'"{3}(.|\n)*?"{3}' \
    r"|'{3}(.|\n)*?'{3}"
    t.type = 'STRING'
    t.value = eval('u'+t.value)
    return t

def t_STRING(t):
    r"'.*?'" \
    r'|".*?"' \
    r"|'[^']*?(?=\n)" \
    r'|"[^"]*?(?=\n)'
    if t.value[0] != t.value[-1] or len(t.value)==1:
        t.value = eval( 'u'+t.value+t.value[0] )+'\n'
    else:
        t.value = eval( 'u'+t.value)
    return t

def t_PYCODE(t):
    r'`[^`]*`'
    t.value = t.value[1:-1]
    return t

def t_error(t):
    raise SyntaxError("syntax error on line %d near '%s'" % (t.lineno, t.value))

def processindentation( lexer, blanks ):
    indentsize =  blanks and len( blanks ) or 0
        
    indentlevel = len(lexer.levels)
    if ( indentsize > lexer.levels[-1] ):
        lexer.levels.append( indentsize )
        lexer.pendingtokens.append( createIndent( indentlevel ) )
    else:
        while ( indentsize < lexer.levels[-1] ):
            lexer.levels.pop()
            lexer.pendingtokens.append( createDedent( indentlevel ) )

def createToken( type, value ):
    indent_token = lex.LexToken()
    indent_token.type = type
    indent_token.value = value
    indent_token.lineno = lex.lexer.lineno
    indent_token.lexpos = lex.lexer.lexpos
    return indent_token

def createIndent( value ):
    return createToken( 'INDENT', value )

def createDedent( value ):
    return createToken( 'DEDENT', value )

#Public interface    
   
def tokenizer( input ):
    lexer = lex.lex()
    lexer.levels = [ 0 ]
    lexer.pendingtokens = []
    lexer.input( input.replace('\r','\n') +'\n' )
    def tokenfunc_():
        if len( lexer.pendingtokens ):
            return lexer.pendingtokens.pop(0)

        tok = lexer.token()

        if len( lexer.pendingtokens ) and ( tok and tok.type != 'EOL'):
            pending = lexer.pendingtokens.pop(0)
            lexer.pendingtokens.append(tok)
            return pending

        return tok
    return tokenfunc_

