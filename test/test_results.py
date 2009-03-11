# coding=utf-8

from StringIO import StringIO
from parser import *
from ast import DefNode
import os
import unittest

class TestResults( unittest.TestCase ):
    def setUp(self):
        pass
        
    def compare(self, text, result ):
        self.assertEqual( parse( StringIO(text) ), result )
        
    def testempty(self):
        source = ""
        result = ""
        self.compare( source, result )

    def teststring(self):
        self.compare( "'hello'\n",'hello' )
    
    def testcalls(self):
        source = """
html:
    body:
        div:
            'ABC'

def html():
    '<html>' $ '</html>'

def body():
    '<body>'
    div:
        $
    '</body>'

def div():
    '<div>' $ '</div>'
"""
        result = "<html><body><div><div>ABC</div></div></body></html>"
        self.compare( source, result )

    def testimport(self):
        source = """
import 'html.tmp'

html:
    body:
        div:
            'ABC'
"""
        importsource = """
def html():
    '<html>' $ '</html>'

def body():
    '<body>'
    div:
        $
    '</body>'

def div():
    '<div>' $ '</div>'
"""
        filename = './html.tmp'
        file = open(filename,'w');
        file.write(importsource)
        file.flush()
        file.close()
        
        result = "<html><body><div><div>ABC</div></div></body></html>"
        self.compare( source, result )
        os.remove(filename)
    
    def testparampassing(self):
        source = """
div:
    '123'
tag('vid'):
    '456'
    
def div():
    tag(name='div'):
        $

def tag( name ):
    '<' name '>'
    $
    '</' $1 '>'
"""
        result = "<div>123</div><vid>456</vid>"
        self.compare( source, result )

    def testcycle1(self):
        source = "[$value]('1','2','3')\n"
        result = "123"
        self.compare( source, result )

    def testcycle2(self):
        source = "[ $key '=' $value ' '](one='1',two='2',three='3')\n"
        result = "one=1 two=2 three=3 "
        self.compare( source, result )

    def testcycleall(self):
        source = """
f(one='1',two='2','3')

def f():
    [ $key '=' $value ' ']($all)
"""
        result = "one=1 two=2 =3 "
        self.compare( source, result )

    def testcycleundeclared(self):
        source = """
tag(name='div', id='d1', class='c1')

def tag(name):
    '<' name [ ' ' $key '="' $value '"']($undeclared) '>'
"""
        result = '<div id="d1" class="c1">'
        self.compare( source, result )

    def testcyclegroup(self):
        source = """
tag(name='div', id='d1', class='c1')

def tag(name):
    '<' name [ [' ' $key '="' $value '"']($value) ]( ($undeclared) ) '>'
"""
        result = '<div id="d1" class="c1">'
        self.compare( source, result )

        
    def testcyclecondition(self):
        source = """
if('true'):
    'this should be printed'

if(''):
    "this shouldn't be printed"

def if( condition ):
    [ $ ](condition)
"""
        result = "this should be printed"
        self.compare( source, result )

    def testcycleconditions(self):
        source = """
[ 'yes' ]('true')
[ 'yes' ](somekey='')
[ 'no' ]('')
"""
        result = "yesyes"
        self.compare( source, result )

    def testcycleimplicits(self):
        self.compare( "[$index]('a','b','c')\n",'012' )
        self.compare( "[$value]('a','b','c')\n",'abc' )
        self.compare( "[$key](A='a',B='b',C='c')\n",'ABC' )

    def testundeclared(self):
        source = """

divs(id='d1', class='c1', hidden="don't print this")
        
def divs( id ):
    tag(name='div', id=id ):
        tag(name='div', id=id, $undeclared )
        
def tag(name, hidden):
    name '(' [$key "='" $value "' "]($undeclared) ')' [ '[' $ ']' ]($)
"""
        result = "div(id='d1' )[div(id='d1' class='c1' )]"
        self.compare( source, result )

    def testcomplexparamvalue(self):
        source=""""""
        result=""
        self.compare( source, result )
        
    def testdefoverwrite(self):
        source = """
import 'originaldefs'

templatemethod('123'):
    '456'

def somemethod( param ):
    'overridden\\n'
    originaldefs.somemethod(param)
"""
        importsource = """
def templatemethod(param):
    '(' somemethod(param)
    $ ')'
def somemethod(param):
    'original:' param
"""
        filename = './originaldefs'
        file = open(filename,'w');
        file.write(importsource)
        file.flush()
        file.close()
        
        result = "(overridden\noriginal:123456)"
        self.compare( source, result )
        os.remove(filename)
        
    def testpycode(self):
        source = "`'123'`\n"
        result = "123"
        self.compare( source, result )

    def testpycodecall(self):
        source = """
native(`"0%d0"%(100+20+3,)`):
    '456'
        
def native( param ):
    `param[1:-1]`
    '456'
"""
        result = "123456"
        self.compare( source, result )

    def testpycodecycle(self):
        source = "[$value](`xrange(1,6)`)\n"
        result = "12345"
        self.compare( source, result )

    def testpycodeimplicit(self):
        source = "[` int(_('$value'))+1 `]( '1','2','3' )\n"
        result = "234"
        self.compare( source, result )

    def testnonascii(self):
        source = "'αινφω'\n"
        result = "αινφω"
        self.compare( source, result )

    def testpycodeimport(self):
        source = """
`from random import random as rrr`
`rrr()*0`
"""
        result = "0.0"
        self.compare( source, result )

    def testsamenameparam(self):
        source = """
m1('B',C='C')
        
def m1( A ):
    m( A='A' A, $undeclared)
def m():
    [$value]($undeclared)
"""
        result = "ABC"
        self.compare( source, result )
    
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestResults)
    unittest.TextTestRunner(verbosity=2).run(suite)

