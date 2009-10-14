from StringIO import StringIO
from magro import parse, compile
from magro.ast import DefNode
from magro.context import Context
import os
import unittest

class TestTemplates( unittest.TestCase ):
    def setUp(self):
        pass
        
    def testcompile(self):
        source = 'variable\n'

        ast = compile( source )
        res = ast.eval( { 'variable':123 } )
        self.assertEqual( res, '123' )

        res = ast.eval( { 'variable':124 } )
        self.assertEqual( res, '124' )

        res = ast.eval()
        self.assertEqual( res, '' )

    def testiter(self):
        source = '[iter]: $value\n'
        
        def gen(n):
            i=0
            while i<n:
                yield i+1
                i+=1

        ast = compile( source )
        res = ast.eval( { 'iter':gen(3) } )
        self.assertEqual( res, '123' )

    def testarrayarg(self):
        source = '[array]:$value\n'

        ast = compile( source )
        res = ast.eval( { 'array':[1,2,3] } )
        self.assertEqual( res, '123' )

    def testarrayargs(self):
        source = '[ a1, a2 ]: $value\n'

        ast = compile( source )
        res = ast.eval( { 'a1':[1,2,3],'a2':[4,5,6] } )
        self.assertEqual( res, '123456' )

    def testarraygroup(self):
        source = """
[ (a1),(a2) ]:
    [$value]: $value
"""

        ast = compile( source )
        res = ast.eval( { 'a1':[1,2,3],'a2':[4,5,6] } )
        self.assertEqual( res, '123456' )

    def testarraynestedgroup(self):
        source = """
[ (a1),(a2) ]:
    [$value]:
        [$value]: $value
"""

        ast = compile( source )
        res = ast.eval( { 'a1':[[1],[2,3]],'a2':[[4,5],6] } )
        self.assertEqual( res, '123456' )

    def testtypedef(self):
        source = """
someAobject
@A():
    '>' $object.name '=' $object.value '<'
"""
        class A:
            def __init__( self, name, value ):
                self.name = name
                self.value = value
        
        ast = compile( source )
        context = Context({ 'someAobject': A('super','duper') })

        res = ast.eval( context )
        self.assertEqual( res, '>super=duper<' )

    def testtypedefinheritanceold(self):
        source = """
someAobject
@A(): 'A'
"""
        #old style classes.
        class A(): pass
        class B(A): pass
        class C(B): pass
        
        ast = compile( source )

        context = Context({ 'someAobject': C() })
        res = ast.eval( context )
        self.assertEqual( res, 'A' )

    def testtypedefinheritancenew(self):
        source = """
someAobject
@A(): 'A'
"""
        #new style classes.
        class A(object): pass
        class B(A): pass
        class C(B): pass
        
        ast = compile( source )

        context = Context({ 'someAobject': C() })
        res = ast.eval( context )
        self.assertEqual( res, 'A' )

    def testtypedefinheritanceorder(self):
        source = """
someAobject
@A(): 'A'
@B2(): 'B2'
"""

        class A(object): pass
        class B1(A): pass
        class B2(object): pass
        class C(B1,B2): pass
        class D(C): pass
        
        ast = compile( source )

        context = Context({ 'someAobject': D() })
        res = ast.eval( context )
        self.assertEqual( res, 'B2' )
    
    def testevaluationprecedence(self):
        source = """
var
def var():
    'abc'
"""
        ast = compile( source )

        res = ast.eval( {} )
        self.assertEqual( res, 'abc' )

        res = ast.eval( { 'var':'123' } )
        self.assertEqual( res, '123' )

        
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTemplates)
    unittest.TextTestRunner(verbosity=2).run(suite)

