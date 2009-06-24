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
        code = BlockNode([
            StringNode('ab'),
            StringNode('cd'),
            StringNode('ef'),
        ])
        text = 'abcdef'
        node = DefNode( name, [], code )
        self.assertEqual( node.execute([],'',{}), text )

    def testcall(self):
        name = 'dummy'
        code = BlockNode([ StringNode('Done') ])
        defnode = DefNode( name, [], code )
        context = { 'dummy':defnode }
        text = 'Done'
        
        node = CallNode( name )
        self.assertEqual(node.eval(context),text)

    def testcallcontents(self):
        name = 'dummy'
        code = BlockNode([ StringNode('>|'), ImplicitNode('$'), StringNode('|<')])
        defnode = DefNode( name, [], code )
        context = { 'dummy':defnode }
        thecontents = 'Thisisthecontents'
        text = '>|'+thecontents+'|<'
        contents = BlockNode([StringNode(thecontents)])
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
        code = BlockNode([ StringNode('<'), CallNode('p1'), StringNode('>'), ])
        defnode = DefNode( name, paramdefs, code )
        context = { 'dummy':defnode }
        
        callparams = [ ParamNode('p1', StringNode('v1') ) ]
        text = '<v1>'
        
        node = CallNode( name, callparams )
        self.assertEqual(node.eval(context),text)

    def testcalllwithblockparam(self):
        name = 'dummy'
        paramdefs = [ ParamNode('p1') ]
        code = BlockNode([ StringNode('<'), CallNode('p1'), StringNode('>'), ])
        defnode = DefNode( name, paramdefs, code )
        context = { 'dummy':defnode }
        
        value = BlockNode( [
            StringNode('v'),
            StringNode('a'),
            StringNode('l'),
        ])
        paramnode = ParamNode( 'p1', value )
        text = '<val>'
        
        node = CallNode( name, [paramnode] )
        self.assertEqual(node.eval(context),text)

    def testparamdefaultvalue(self):
        name = 'dummy'
        paramdefs = [ ParamNode('p1',StringNode('d1')) ]
        code = BlockNode([ StringNode('<'), CallNode('p1'), StringNode('>'), ])
        defnode = DefNode( name, paramdefs, code )
        context = { 'dummy':defnode }
        
        callparams = []
        text = '<d1>'
        
        node = CallNode( name, callparams )
        self.assertEqual(node.eval(context),text)

    def testcycle(self):
        code = BlockNode([ ImplicitNode('$key'), StringNode('='), ImplicitNode('$value'), StringNode(' '), ])
        params = [
            ParamNode('p1',StringNode('v1')),
            ParamNode('p2',StringNode('v2')),
            ParamNode('p3',StringNode('v3')),
        ]
        text = 'p1=v1 p2=v2 p3=v3 '
        node = CycleNode( params, code )
        self.assertEqual(node.eval({}),text)

    def testtypenode(self):
        node = TypeDefNode( name='NoneType', params=[] , code=BlockNode([
            StringNode('>Empty<(i.e. '),
            ImplicitNode('$object'),
            StringNode(')'),
        ]))
        text = '>Empty<(i.e. None)'
        self.assertEqual( node.execute( None, [], '', {} ),text )
        
    def testcycleelse(self):
        code = BlockNode([ StringNode('True') ])
        elsecode = BlockNode([ StringNode('False') ])
        params = [
            ParamNode('p1',StringNode('v1')),
            ParamNode(None,StringNode('')),
            ParamNode('p3',StringNode('')),
            ParamNode(None,StringNode('v4')),
            ParamNode(None,CallNode('non')),
        ]
        text = 'TrueFalseTrueTrueFalse'
        node = CycleNode( params, code, elsecode )
        self.assertEqual(node.eval({}),text)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAst)
    unittest.TextTestRunner(verbosity=2).run(suite)
