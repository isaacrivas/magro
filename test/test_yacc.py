from magro.parser import MagroParser
from magro.loaders import DummyLoader

import os
import unittest

class TestYacc( unittest.TestCase ):
    def setUp(self):
        self.parser = MagroParser( DummyLoader() )
        
    def accept(self, text):
        self.parser.compile( text )

    def reject(self, text):
        try:
            self.parser.compile( text )
            fail = True
        except Exception:
            fail = False
        if fail:
            self.fail('The text should have been rejected.')
        
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
    '<' name
    [$unknown]:
        ' ' $key '="' $value '"'
    '>' $ '</' name '>'
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
    '['
    [$object]:
        $value ','
    ']'
""");

    def testaltcycle(self):
        self.accept("""
['1','2','3']:
    'a' $value
""");

    def testsingleelse(self):
        self.reject("""
:
    'b'
""");


    def testcycleelse(self):
        self.accept("""
['1','','3']:
    'a' $value
:
    'b'
""");


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestYacc)
    unittest.TextTestRunner(verbosity=2).run(suite)

