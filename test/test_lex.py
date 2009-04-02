from StringIO import StringIO
from magro.lexer import *
import unittest

class TestLex( unittest.TestCase ):
    def setUp(self):
        pass
        
    def dotest(self, text, tokens):
        tokfun = tokenizer( text )
        i=1
        for t in tokens:
            tok = tokfun()
            if not tok: self.fail( 'Expected %d tokens, %d  found'%(len(tokens),i) )
            self.assertEqual( t, tok.type )
            i+=1

    def testcomments(self):
        self.dotest(
            "#comment\ndef something: #this is a comment\n    asymbol\n",
            ['DEF', 'SYMBOL', ':', 'EOL', 'INDENT', 'SYMBOL', 'EOL', 'DEDENT', ] )

            
    def testwords(self):
        self.dotest(
            "def deff",
            ['DEF', 'SYMBOL'] )
    
    def teststring(self):
        strings = """'una cadena' "una cadena" "otra cad'na" 'otra cad"na'"""
        self.dotest(
            strings,
            ['STRING']*4 )

    def teststringlines(self):
        strings = """'primera\n'"segunda"\n"tercera\n"'cuarta'\n'\n"\n"""
        self.dotest(
            strings,
            ['STRING', 'EOL', ]*6 )

    def testlongstrings(self):
        strings = "'''\nesta es\nuna\prueba de una \n\n cadena larga''' ok '''a'b'c''' ok" \
                  '"""\nesta es\nuna\prueba de una \n\n cadena larga""" ok """a"b"c""" ok'
        
        self.dotest(
            strings,
            ['STRING', 'SYMBOL']*4 )

    def testescape(self):
        text = r"'1\n2\t3'"
        expected = "1\n2\t3"
        tokfun = tokenizer( text )
        tok = tokfun()
        self.assertEqual( tok.value, expected )

    def testsymbols(self):
        symbols = "acb acb123 _abc a.b.c a_b_1_2 a_._..b_bc.c..c some-name"
        self.dotest(
            symbols,
            ['SYMBOL']*7 )

    def testimplicit(self):
        symbols = "$ $$ $abc $unknown $key $a.b.c $_"
        self.dotest(
            symbols,
            ['IMPLICIT']*7 )
            
    def testindentvalue(self):
        text = "a\n    b\n        c"
        tokfun = tokenizer( text )
        tok = tokfun() #symbol
        tok = tokfun() #eof
        tok = tokfun() #indent
        self.assertEqual( tok.value, 1 )
        tok = tokfun() #symbol
        tok = tokfun() #eof
        tok = tokfun() #indent
        self.assertEqual( tok.value, 2 )
        
    def testindentation(self):
        self.dotest(
            """
abc
  fed
  efg
    ghi
jkl
""",
            ['SYMBOL','EOL',
             'INDENT', 'SYMBOL', 'EOL', 
                       'SYMBOL', 'EOL',
                       'INDENT', 'SYMBOL', 'EOL',
                       'DEDENT',
             'DEDENT', 'SYMBOL', 'EOL', ] )
                
    def testignoreeols(self):
        self.dotest('\n\n\nA\n\n\n   \n\n\n\n"B"',('SYMBOL',  'EOL', 'STRING') )

    def testignoreindentedcomment(self):
        self.dotest('symbol\n      #comment\n  "string"',('SYMBOL', 'EOL', 'INDENT', 'STRING') )

    def dotestoel(self, eol):
        text = 'symbol'+eol+'"string"#comment'+eol+'$implicit   #comment'+eol+'def'
        self.dotest( text ,('SYMBOL', 'EOL', 'STRING', 'EOL', 'IMPLICIT', 'EOL', 'DEF') )
 
    def testunixeol(self):
        self.dotestoel('\n')
        
    def testwindowseol(self):
        self.dotestoel('\r\n')

    def testmaceol(self):
        self.dotestoel('\r')


    def testpycode(self):
        self.dotest('`print x`',('PYCODE',) )
        
                
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLex)
    unittest.TextTestRunner(verbosity=2).run(suite)
