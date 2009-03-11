from cStringIO import StringIO

class Node:
    def __init__(self):
        pass

    def eval( self, context ):
        return ''

class RootNode( Node ):
    def __init__(self, code=[], defs={} ):
        self.code = BlockNode(code)
        self.defs = defs
       
    def eval( self, context={} ):
        if context: 
            context = context.copy()
        for k,v in self.defs.items():
            if k not in context:
                context[k] = v

        return self.code.eval( context )
    

class StringNode( Node ):
    def __init__(self, value):
        self.value = value
       
    def eval( self, context ):
        return self.value

    def __str__(self):
        return 'StringNode("%s")'%(self.value,)

        
class ImplicitNode( Node ):
    def __init__(self, name):
        self.name = name
       
    def eval( self, context ):
        try:
            return context[ self.name ]
        except KeyError:
            return ''

class DefNode( Node ):
    def __init__(self, name, params, code):
        self.name = name
        self.params = params
        self.paramnames = [ p.name for p in self.params ]
        if hasattr(code,'__iter__'):
            self.code = BlockNode(code)
        else:
            self.code = code
        
    def expandparams( self, params, context ):
        expanded = []
        for p in params:
            val = p.eval( context )
            if hasattr(val,'__iter__'):
                expanded.extend( val )
            else:
                expanded.append( p )
        return expanded
        
    def processparams(self, params, context ):
        params = self.expandparams( params, context )
        context['$all'] = params

        #evaluate params and see if they were declared.
        undeclared = []
        i = 1
        for p in params:
            value = p.eval(context)
            context[ '$%d'%(i,) ] = value
            if p.name:
                context[ p.name ] = value
                if p.name not in self.paramnames:
                    p = ParamNode( p.name, StringNode(value) )
                    undeclared.append(p)
                
            i+=1
        context['$undeclared'] = undeclared

        #search default values for undefined parameters
        i = 1
        for p in self.params:
            if not context.has_key(p.name):
                ivar = '$%d'%(i,)
                if context.has_key( ivar ):
                    context[p.name] = context[ivar]
                else:
                    context[p.name] = p.eval(context)
            i+=1

    def execute( self, params, context ):
        self.processparams( params, context)
        return self.code.eval(context)

class ParamNode( Node ):
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
    
    def eval(self,context):
        if self.value:
            return self.value.eval(context)
        else:
            return ''

    def __repr__(self):
        return 'Param( "%s", %s )'%(self.name,self.value,)
            
class CallNode( Node ):
    def __init__(self, name, params=[], contents=[]):
        self.name = name
        self.params = params
        self.contents = contents
       
    def eval( self, context ):
        if not context.has_key(self.name):
            return ''
            
        symbol = context[ self.name ]
        typenames = gettypenames( symbol )
        
        target = None
        for typename in typenames:
            if ('@'+typename) in context:
                target = symbol
                symbol = context['@'+typename]
                break
        
        if hasattr(symbol,'execute'):
            thecontents = ''
            mycontext = context.copy()
            for c in self.contents:
                thecontents += c.eval(mycontext)
            mycontext['$'] = thecontents

            if target:
                return symbol.execute( target, self.params, mycontext )
            else:
                return symbol.execute( self.params, mycontext )
        else:
            return symbol
        
class CycleNode( Node ):
    def __init__(self, params=[], code=[]):
        self.params = params
        self.code = code
    
    def eval( self, context ):
        return self.processparams( self.params, context )
            
    def processparams(self, params, context):
        result = ''
        i=-1
        for p in params:
            i+=1
            name = None
            if isinstance(p,Node):
                name = p.name
                val = p.eval(context)
            else:
                val = p

            if not name and not val: continue

            if hasattr(val,'__iter__'):
                result += self.processparams( val, context )
            else:
                result += self.execparam( i, name, val, context )
        return result

    def execparam(self, pos, name, value, context ):
        result = ''
        mycontext = context.copy()
        mycontext['$index'] = pos
        if name: mycontext['$key'] = name
        if value: mycontext['$value'] = value
        for c in self.code:
            result += str( c.eval(mycontext) )
        return result

class GroupNode( Node ):
    def __init__(self,value):
        self.value=[]
        self.value.extend(value)

    def eval(self,context):
        return self.value
class BlockNode():
    def __init__(self,code):
        self.code=[]
        self.code.extend(code)

    def eval(self,context):
        buffer = StringIO()
        for s in self.code:
            text = str(s.eval( context ))
            if text: buffer.write(text)

        result = buffer.getvalue()
        buffer.close()
        return result

class PycodeNode( Node ):
    def __init__(self, code='', globals={} ):
        self.code = code
        self.globals = globals
       
    def eval( self, context={} ):
        mycontext = context.copy()
        mycontext['_'] = buildaccessor( context )
        if 'import' in self.code:
            exec self.code in self.globals
            return ''
        else:
            return eval( self.code, self.globals, mycontext )

class TypeDefNode( Node ):
    def __init__(self, name, params, code):
        self.name = name
        self.defnode = DefNode(name, params, code)

    def execute( self, target, params, context ):
        mycontext = context.copy()
        mycontext['$object'] = target
        return self.defnode.execute( params, mycontext )
        
def buildaccessor( locals ):
    def accessor(key):
        return locals[key]
    return accessor

def gettypenames( object ):
    thetype = type(object)
    if thetype.__name__ == 'instance':
        thetype = object.__class__
    
    result = [thetype.__name__]
    result.extend( gettypebases(thetype) )
    
    return result

def gettypebases(thetype):
    result = []
    processtypebases(thetype, result, 0)
    return [ t for l in result for t in l]
    
def processtypebases(thetype, levels, currlevel):    
    while (currlevel >= len(levels)):
        levels.append([])
    for base in thetype.__bases__:
        levels[currlevel].append(base.__name__)
    for base in thetype.__bases__:
        processtypebases(base, levels, currlevel+1)
