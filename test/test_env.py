import unittest
from magro.environment import Environment
import os
import sys

class TestEnv( unittest.TestCase ):
    def setUp(self):
        pass

    def testdefault(self):
        env = Environment()

    def testsearchfile(self):
        filename = sys.argv[0]
        env = Environment()
        loader = env.loader
        fullpath = loader.search_file( filename )
        self.assertEqual( fullpath, os.path.abspath(filename) )

        filename = 'unknownfile'
        fullpath = loader.search_file( filename )
        self.assertFalse( fullpath )
            
                
if __name__ == '__main__':
    unittest.main()
