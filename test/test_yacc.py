from StringIO import StringIO
from parser import *
import os
import unittest

class TestYacc( unittest.TestCase ):
    def setUp(self):
        pass
        
    def accept(self, text):
        parse( StringIO(text) )

    def reject(self, text):
        try:
            parse( StringIO(text) )
            self.fail('The text should have been rejected.')
        except Exception:
            pass
        
    def testminimal(self):
        self.accept( "'hello world'\n" )
        
    def testcalls(self):
        self.accept( """
html:
    body:
        div( id='123' )
""" )

    def testdef(self):
        self.accept( """
def html():
    '<html>' $ '</html>'
""" )

    def testdefparams(self):
        self.accept( """
def input( id, type='text', name, value ):
    'something'
""" )


    def testcallsanddefs(self):
        self.accept( """
import 'module'

html:
    body:
        div
        
def html():
    '<html>' $ '</html>'

def body():
    '<body>'
    div:
        $
    '</body>'

def div():
    '<div>' $ '</div>'
""" )

    def testcycle(self):
        self.accept( """
def tag(name):
    '<' name [' ' $key '="' $value '"']($unknown) '>' $ '</' name '>'
""" )

    def testbadindent(self):
        self.reject( """
html:
body:
        div
""" )

    def testcomplexparamvalues(self):
        self.accept( "call( param1=anothercall('') )\n" )
        self.accept( "call( param1='(' symbol ')', param2='' )\n" )

    def testpycode(self):
        self.accept( "def native():\n    `'123'`\n" )

    def testsinglelinecall(self):
        self.accept("""
fun: '123' '456'

def fun():
    $

""");

    def testsinglelinedef(self):
        self.accept("""
fun:'123'
def foo():
    bar('0'): $ 
def bar(baz): baz $
""");

    def testattype(self):
        self.accept("""
@list():
    '[' [ $value ',']($object) ']'
""");

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestYacc)
    unittest.TextTestRunner(verbosity=2).run(suite)
