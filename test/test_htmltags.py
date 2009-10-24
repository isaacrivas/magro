import unittest

from StringIO import StringIO
from magro import Environment, Template
from magro.loaders import FileSystemLoader
import os
import sys

class TestHtmlTags( unittest.TestCase ):
    def setUp(self):
        self.env = Environment( FileSystemLoader(['./magro/templates']) )

    def compare(self, text, result ):
        template = Template( text, self.env )
        self.assertEqual( template.render(), result )

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
        self.env.settings['html.indentsize'] = 4
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
