# coding=utf-8

from StringIO import StringIO
from magro import Template
from magro.ast import DefNode
import os
import unittest

class TestResults( unittest.TestCase ):
    def setUp(self):
        pass
        
    def compare(self, text, result ):
        template = Template( text )
        self.assertEqual( template.render(), result )
        
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

    def testdefaultparams(self):
        source = """
macro( '1', p3='3')
macro( '4', '5', '6', p7='7')
        
def macro( p1, p2='II' ):
    '(' p1 ',' p2
    [ $undeclared ]: ',' $value
    ')'
"""
        result = "(1,II,3)(4,5,6,7)"
        self.compare( source, result )
        
    def testcycle1(self):
        source = "['1','2','3']: $value\n"
        result = "123"
        self.compare( source, result )

    def testcycle2(self):
        source = "[ one='1',two='2',three='3']: $key '=' $value ' '\n"
        result = "one=1 two=2 three=3 "
        self.compare( source, result )

    def testcycleall(self):
        source = """
f(one='1',two='2','3')

def f():
    [$all]: $key '=' $value ' '
"""
        result = "one=1 two=2 =3 "
        self.compare( source, result )

    def testcycleundeclared(self):
        source = """
tag(name='div', id='d1', class='c1')

def tag(name):
    '<' name
    [$undeclared]: ' ' $key '="' $value '"'
    '>'
"""
        result = '<div id="d1" class="c1">'
        self.compare( source, result )

    def testcyclegroup(self):
        source = """
tag(name='div', id='d1', class='c1')

def tag(name):
    '<' name
    [($undeclared)]:
        [$value]: ' ' $key '="' $value '"'
    '>'
"""
        result = '<div id="d1" class="c1">'
        self.compare( source, result )

    def testcyclenamedgroup(self):
        source = """
[ a=('1', '2', '3'), b=('A','B','C') ]:
    $key '={'
    [$value]: $value ' '
    '} '
"""
        result = 'a={1 2 3 } b={A B C } '
        self.compare( source, result )

        
    def testcyclecondition(self):
        source = """
if('true'):
    'this should be printed'

if(''):
    "this shouldn't be printed"

def if( condition ):
    [condition]: $
"""
        result = "this should be printed"
        self.compare( source, result )

    def testcycleconditions(self):
        source = """
['true']: 'yes'
[somekey='']: 'yes'
['']: 'no'
"""
        result = "yesyes"
        self.compare( source, result )

    def testcycleimplicits(self):
        self.compare( "['a','b','c']: $index\n",'012' )
        self.compare( "['a','b','c']: $value\n",'abc' )
        self.compare( "[A='a',B='b',C='c']: $key\n",'ABC' )

        source = u"""

cycle('A','B','C')
        
def cycle():
    [ `range(1,4)`, $undeclared, '$' ]:
        [$first]: '{'
        $value
        [$notlast]: ', '
        [$last]: '}'
"""
        result = "{1, 2, 3, A, B, C, $}"
        self.compare( source, result )

    def testundeclared(self):
        source = """

divs(id='d1', class='c1', hidden="don't print this")
        
def divs( id ):
    tag(name='div', id=id ):
        tag(name='div', id=id, $undeclared )
        
def tag(name, hidden):
    name '('
    [$undeclared]: $key "='" $value "' "
    ')'
    [$]: '[' $ ']'
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
        source = "[`xrange(1,6)`]: $value\n"
        result = "12345"
        self.compare( source, result )

    def testpycodeimplicit(self):
        source = "['1','2','3']: ` int(_('$value'))+1 `\n"
        result = "234"
        self.compare( source, result )

    def testnonascii(self):
        source = u"'áéïóÙ'\n"
        result = u"áéïóÙ"
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
    [$undeclared]: $value
"""
        result = "ABC"
        self.compare( source, result )

    def testcyclecall(self):
        source = """
def a():
    'A' $
        
['1','2','3']:
    a:
        $value
"""
        result = "A1A2A3"
        self.compare( source, result )

    def testcycleelse(self):
        source = """
def a():
    'A' $
        
['1','','3']:
    a:
        $value
:
    '!'

"""
        result = "A1!A3"
        self.compare( source, result )

    def testcycleelif(self):
        source = """
def a():
    'A' $
        
['1','','3']:
    a:
        $value
: ['']:
    '!'
: ['yes']:
    '?'
:
    'no'

"""
        result = "A1?A3"
        self.compare( source, result )


        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestResults)
    unittest.TextTestRunner(verbosity=2).run(suite)

