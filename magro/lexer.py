"Magro's lexer using Ply"
import ply.lex as lex

reserved = {
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
    """Calculates the current indentation level and generates artificial
    tokens accordingly"""
    indentsize =  blanks and len( blanks ) or 0
        
    indentlevel = len(lexer.levels)
    if ( indentsize > lexer.levels[-1] ):
        lexer.levels.append( indentsize )
        lexer.pendingtokens.append( create_indent( indentlevel ) )
    else:
        while ( indentsize < lexer.levels[-1] ):
            lexer.levels.pop()
            lexer.pendingtokens.append( create_dedent( indentlevel ) )

def create_token( token_type, value ):
    "Used to create any kind of tokens"
    token = lex.LexToken()
    token.type = token_type
    token.value = value
    token.lineno = lex.lexer.lineno
    token.lexpos = lex.lexer.lexpos
    return token

def create_indent( value ):
    "Creates an INDENT token"
    return create_token( 'INDENT', value )

def create_dedent( value ):
    "Creates a DEDENT token"
    return create_token( 'DEDENT', value )

#Public interface    
   
def tokenizer( the_input ):
    "Used by the magro parser to tokenize the input string."
    lexer = lex.lex()
    lexer.levels = [ 0 ]
    lexer.pendingtokens = []
    lexer.input( the_input.replace('\r', '\n') +'\n' )
    def tokenfunc_():
        """Tokenize the function keeping proper account of artificial tokens
        such as INDENT and DEDENT"""
        if len( lexer.pendingtokens ):
            return lexer.pendingtokens.pop(0)

        tok = lexer.token()

        if len( lexer.pendingtokens ) and ( tok and tok.type != 'EOL'):
            pending = lexer.pendingtokens.pop(0)
            lexer.pendingtokens.append(tok)
            return pending

        return tok
    return tokenfunc_

