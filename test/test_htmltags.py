import unittest

from StringIO import StringIO
from parser import parse
import os
import sys

import env


class TestHtmlTags( unittest.TestCase ):
    def setUp(self):
        env.path.append("./lib")

    def compare(self, text, result ):
        self.assertEqual( parse( StringIO(text) ), result )

    def test_path(self):
        print env.path,

    def testhtml(self):
        source = """
import 'html5'

html:
    body(onload=''):
        div( id='d1', class='c1' )

"""
        result = '<html><body onload=""><div id="d1" class="c1"/></body></html>'
        self.compare( source, result )
                
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHtmlTags)
    unittest.TextTestRunner(verbosity=2).run(suite)