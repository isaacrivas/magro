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
   'EOL',
   'INDENT',
   'DEDENT',
] + reserved.values()

literals = ":()[]=,@"

def t_comment(t):
    r'\#.*'
    pass

def t_SYMBOL(t):
    r'[a-zA-Z0-9._-]+'
    t.type = reserved.get( t.value , 'SYMBOL' )
    return t

def t_IMPLICIT(t):
    r'\$[\$a-zA-Z0-9._-]*'
    return t
    
def t_STRING(t):
    r'\'.*?\'|\".*?\"|\'[^\']*\n|\"[^\"]*\n'
    if t.value[-1] == "\n":
        t.value = eval( t.value[:-1]+t.value[0])+'\n'
        #rescan the \n
        t.lexer.lexpos -= 1
    else:
        t.value = eval(t.value)
    return t

def t_PYCODE(t):
    r'`[^`]*`'
    t.value = t.value[1:-1]
    return t
    
def t_EOL(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t
    
t_ignore = ' \t'

def t_error(t):
    raise SyntaxError("syntax error on line %d near '%s'" % (t.lineno, t.value))


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
    
indent_expr = re.compile('^([ \t]+)')
emptyline = re.compile('^\s*(\#.*)?\n')
    
def tokenizer( input ):
    lexer = lex.lex()
    lexer.levels = [ 0 ]
    lexer.pendingtokens = []
    lexer.parsing = False
    def tokenfunc_():
        if not lexer.parsing:
            currline = input.readline()
            while emptyline.match( currline ):
                currline = input.readline()
            
            lineindent = indent_expr.match( currline )
            indentsize = 0
            if ( lineindent ):
                indentsize =  len( lineindent.group(1) )
                
            if ( indentsize > lexer.levels[-1] ):
                lexer.levels.append( indentsize )
                lexer.pendingtokens.append( createIndent( indentsize ) )
            else:
                while ( indentsize < lexer.levels[-1] ):
                    dedentsize = lexer.levels.pop()
                    lexer.pendingtokens.append( createDedent( dedentsize ) )

            lexer.input( currline )
            lexer.parsing = True
        
        if len( lexer.pendingtokens ):
            return lexer.pendingtokens.pop()
            
        tok = lexer.token()
        if not tok or tok.type == 'EOL' :
            lexer.parsing = False

        return tok
    return tokenfunc_

