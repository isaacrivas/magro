from magro.context import Context
import unittest

class TestContext( unittest.TestCase ):
    def setUp(self):
        pass
    
    def testnotin(self):
        c = Context()
        try:
            v = c['a']
            self.fail( 'value found: '+str(v) )
        except KeyError:
            pass

    def testhaskey(self):
        c = Context()
        class A:
            a = 1
    
        c = Context({'base':A()})
        self.assertTrue( c.has_key( 'base' ) )
        self.assertTrue( c.has_key( 'base.a' ) )
        self.assertFalse( c.has_key( 'base.b' ) )
            
    def testset(self):
        c = Context()
        c['a'] = 1
        self.assertEquals( c['a'], 1 )

    def testsimple(self):
        c = Context({'a':1})
        self.assertEquals( c['a'], 1 )

    def testgetbase(self):
        class A:
            a = 1
    
        c = Context({'base':A()})
        self.assertEquals( c['base.a'], 1 )

    def testgetbase2(self):
        class A:
            a = 1
    
        c = Context({'ba.s.e':A()})
        self.assertEquals( c['ba.s.e.a'], 1 )

    def testgetmethod(self):
        class A:
            def a(self):
                return 1
    
        c = Context({'base':A()})
        self.assertEquals( c['base.a'], 1 )
        
    def testgetmethodinthemiddle(self):
        class A:
            def a(self):
                class B:
                    b = 1
                return B()
    
        c = Context({'base':A()})
        self.assertEquals( c['base.a.b'], 1 )

    def testpreference(self):
        class A:
            def a(self):
                class B:
                    b = 1
                return B()
    
        c = Context({'base':A(), 'base.a.b': 2})
        self.assertEquals( c['base.a.b'], 2 )

    def testnoattribute(self):
        class A:
            a = 1
        c = Context({'base':A()})
        try:
            v = c['base.a.b']
            self.fail('value found: '+str(v))
        except AttributeError:
            pass
        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestContext)
    unittest.TextTestRunner(verbosity=2).run(suite)

