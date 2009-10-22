# coding=utf-8

from StringIO import StringIO
from magro import Template
from magro.ast import DefNode
import os
import unittest

class TestBugs( unittest.TestCase ):
    def setUp(self):
        pass
        
    def compare(self, text, result ):
        template = Template(text)
        self.assertEqual( template.render(), result )
            
    def testdefoverridingparams(self):
        source = """
parent('1','2'):
    child('A'):
        'B'
        
def parent( p1, child ):
    child ';' $

def child( _p1 ):
    _p1 '!' $

"""
        expected = "2;A!B"
        self.compare(source,expected);


    def testcontentsasparam(self):
        source = """
call:
    '#'

def call():
    put($):
        '?'

def put( param ):
    param
"""
        expected = "#"
        self.compare(source,expected);

    def testimportinlibrary(self):
        source = """
import 'library.tmp'
_( 'ABC' )
"""
        importsource = """
`import gettext`
def _( text ):
    `gettext.gettext( text )`

"""
        filename = './library.tmp'
        file = open(filename,'w');
        file.write(importsource)
        file.flush()
        file.close()
        
        result = "ABC"
        self.compare( source, result )
        os.remove(filename)

    def testlastline(self):
        source = """
call:
    '#'

def call():
    $"""
        expected = "#"
        self.compare(source,expected);

        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBugs)
    unittest.TextTestRunner(verbosity=2).run(suite)

