import unittest
import env
import os
import sys

class TestEnv( unittest.TestCase ):
    def setUp(self):
        pass

    def testpath(self):
        print env.path

    def testsearchfile(self):
        filename = sys.argv[0]
        fullpath = env.searchfile( filename )
        self.assertEqual( fullpath, os.path.abspath(filename) )

        filename = 'unknownfile'
        fullpath = env.searchfile( filename )
        self.assertFalse( fullpath )
            
                
if __name__ == '__main__':
    unittest.main()
