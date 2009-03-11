from magro.ast import *
import unittest

class TestAst( unittest.TestCase ):
    def setUp(self):
        pass
        
    def teststring(self):
        text = 'somestring'
        node = StringNode(text)
        self.assertEqual(node.eval(None),text)

    def testimplicit(self):
        name = '$implicitname'
        text = 'value of the implicit variable'
        node = ImplicitNode(name)
        self.assertEqual(node.eval({name:text}),text)

    def testdef(self):
        name = 'adef'
        code = [
            StringNode('ab'),
            StringNode('cd'),
            StringNode('ef'),
        ]
        text = 'abcdef'
        node = DefNode( name, [], code )
        self.assertEqual( node.execute([],{}), text )

    def testcall(self):
        name = 'dummy'
        code = [ StringNode('Done') ]
        defnode = DefNode( name, [], code )
        context = { 'dummy':defnode }
        text = 'Done'
        
        node = CallNode( name )
        self.assertEqual(node.eval(context),text)

    def testcallcontents(self):
        name = 'dummy'
        code = [ StringNode('>|'), ImplicitNode('$'), StringNode('|<')]
        defnode = DefNode( name, [], code )
        context = { 'dummy':defnode }
        thecontents = 'Thisisthecontents'
        text = '>|'+thecontents+'|<'
        contents = [StringNode(thecontents)]
        node = CallNode( name, contents=contents )
        self.assertEqual(node.eval(context),text)

    def testcallparam(self):
        name = 'param'
        value = StringNode('val')
        node = ParamNode( name, value )
        text = 'val'
        self.assertEqual(node.eval({}),text)

    def testblockparam(self):
        name = 'param'
        value = BlockNode( [
            StringNode('v'),
            StringNode('a'),
            StringNode('l'),
        ])
        node = ParamNode( name, value )
        text = 'val'
        self.assertEqual(node.eval({}),text)

        
    def testcallwithparams(self):
        name = 'dummy'
        paramdefs = [ ParamNode('p1') ]
        code = [ StringNode('<'), CallNode('p1'), StringNode('>'), ]
        defnode = DefNode( name, paramdefs, code )
        context = { 'dummy':defnode }
        
        callparams = [ ParamNode('p1', StringNode('v1') ) ]
        text = '<v1>'
        
        node = CallNode( name, callparams )
        self.assertEqual(node.eval(context),text)

    def testcalllwithblockparam(self):
        name = 'dummy'
        paramdefs = [ ParamNode('p1') ]
        code = [ StringNode('<'), CallNode('p1'), StringNode('>'), ]
        defnode = DefNode( name, paramdefs, code )
        context = { 'dummy':defnode }
        
        value = BlockNode( [
            StringNode('v'),
            StringNode('a'),
            StringNode('l'),
        ])
        paramnode = ParamNode( name, value )
        text = '<val>'
        
        node = CallNode( name, [paramnode] )
        self.assertEqual(node.eval(context),text)

    def testparamdefaultvalue(self):
        name = 'dummy'
        paramdefs = [ ParamNode('p1',StringNode('d1')) ]
        code = [ StringNode('<'), CallNode('p1'), StringNode('>'), ]
        defnode = DefNode( name, paramdefs, code )
        context = { 'dummy':defnode }
        
        callparams = []
        text = '<d1>'
        
        node = CallNode( name, callparams )
        self.assertEqual(node.eval(context),text)

    def testcycle(self):
        code = [ ImplicitNode('$key'), StringNode('='), ImplicitNode('$value'), StringNode(' '), ]
        params = [
            ParamNode('p1',StringNode('v1')),
            ParamNode('p2',StringNode('v2')),
            ParamNode('p3',StringNode('v3')),
        ]
        text = 'p1=v1 p2=v2 p3=v3 '
        node = CycleNode( params, code )
        self.assertEqual(node.eval({}),text)

    def testtypenode(self):
        node = TypeDefNode( name='NoneType', params=[] , code=[
            StringNode('>Empty<(i.e. '),
            ImplicitNode('$object'),
            StringNode(')'),
        ])
        text = '>Empty<(i.e. None)'
        self.assertEqual( node.execute( None, [], {} ),text )
        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAst)
    unittest.TextTestRunner(verbosity=2).run(suite)
