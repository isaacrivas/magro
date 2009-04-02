import unittest

from StringIO import StringIO
from magro.parser import parse
import os
import sys

import magro.env as env


class TestHtmlTags( unittest.TestCase ):
    def setUp(self):
        env.path.append("./lib")

    def compare(self, text, result ):
        r = parse( text )
        self.assertEqual( r, result )

    def test_path(self):
        print env.path,

    def testhtml(self):
        source = """
import 'html5'

html:
    body(onload=''):
        div( id='d1', class='c1' )

"""
        result = '<html><body onload=""><div id="d1" class="c1"></div></body></html>'
        self.compare( source, result )

    def testindentation(self):
        source = """
import 'html5'

html:
    body(onload=''):
        div( id='d1', class='c1' ):
            '123'
            '456'
    script:
        'var a=1;'

"""
        env.settings['html.indentsize'] = 4
        result = """\
<html>
    <body onload="">
        <div id="d1" class="c1">
            123456
        </div>
    </body>
    <script>
        var a=1;
    </script>
</html>"""
        self.compare( source, result )

        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHtmlTags)
    unittest.TextTestRunner(verbosity=2).run(suite)
