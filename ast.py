from io import StringIO
import magro.env as env
DEF_PREFIX = '!DEF!'

class Node:
    def __init__(self):
        pass

    def eval( self, context ):
        return ''
    
    def __repr__(self):
        return 'Node'

class BlockNode( Node ):
    def __init__(self,code,level=0):
        self.code=[]
        self.code.extend(code)
        self.level = level

    def eval(self,context,uselevel=False):
        buffer = StringIO()
        if uselevel:
            context = context.copy()
            context['$level'] = self.level
            context['$nextlevel'] = self.level+1
            if self.level: context['$previouslevel'] = self.level-1
        for s in self.code:
            text = s.eval( context )
            if text: buffer.write(text)

        result = buffer.getvalue()
        buffer.close()
        return result

    def __repr__(self):
        strcode = ''
        for s in self.code:
            strcode += '\n%s%s'%('  '*(self.level+1),s)
        return 'BlockNode:%s'%(strcode,)


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
        for k,v in env.settings.items():
            context['settings.'+k] = v

        return self.code.eval( context )
    
    def __repr__(self):
        return '\n*%s'%(self.code,)

class StringNode( Node ):
    def __init__(self, value):
        self.value = value
       
    def eval( self, context ):
        return self.value

    def __repr__(self):
        return 'StringNode("%s")'%(self.value,)

        
class ImplicitNode( Node ):
    def __init__(self, name):
        self.name = name
       
    def eval( self, context ):
        try:
            return context[ self.name ]
        except KeyError:
            return ''

    def __repr__(self):
        return 'ImplicitNode("%s")'%(self.name,)

class DefNode( Node ):
    def __init__(self, name, params, code):
        self.name = name
        self.params = params
        self.paramnames = [ p.name for p in self.params ]
        self.code = code
        
    def expandparams( self, params, context ):
        expanded = []
        for p in params:
            val = p.eval( context )
            if isinstance(val,list):
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
        iunnamed = 0
        for p in params:
            value = p.eval(context)
            
            context[ '$%d'%(i,) ] = value
            if p.name:
                context[ p.name ] = value
                if p.name not in self.paramnames:
                    p = ParamNode( p.name, StringNode(value) )
                    undeclared.append(p)
            else:
                iunnamed += 1
                if iunnamed > len(self.params):
                    p = ParamNode( None, StringNode(value) )
                    undeclared.append(p)
            i+=1
        context['$undeclared'] = undeclared
        
        #search default values for undefined parameters
        i = 1
        for p in self.params:
            if p.name not in context:
                if i<=len(params) and not params[i-1].name:
                    ivar = '$%d'%(i,)
                    context[p.name] = context[ivar]
                else:
                    context[p.name] = p.eval(context)
            i+=1

    def execute( self, params, contents, context ):
        self.processparams( params, context)
        context['$'] = contents
        return self.code.eval(context)

    def __repr__(self):
        return 'DefNode(%s):%s'%(self.name,self.code)


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
    def __init__(self, name, params=[], contents=BlockNode([])):
        self.name = name
        self.params = params
        self.contents = contents
       
    def eval( self, context ):
        symbol = None
        target = None

        if not self.name in context:
            try:
                symbol = context[DEF_PREFIX+self.name]
            except:
                return ''
        else:
            symbol = context[ self.name ]
            typenames = gettypenames( symbol )
            
            for typename in typenames:
                if ('@'+typename) in context:
                    target = symbol
                    symbol = context['@'+typename]
                    break
        
        if hasattr(symbol,'execute'):
            mycontext = context.copy()
            contents = self.contents.eval(mycontext, True)

            if target:
                return symbol.execute( target, self.params, contents, mycontext )
            else:
                return symbol.execute( self.params, contents, mycontext )
        else:
            return symbol
    
    def __repr__(self):
        return 'CallNode("%s"):%s'%(self.name,self.contents)    

class EvalParam( object ):
    def __init__( self, pos, name, value, islast ):
        self.pos = pos
        self.name = name
        self.value = value
        self.islast = islast
            
class CycleNode( Node ):
    def __init__(self, params=[], code=BlockNode([]), elsecode=None ):
        self.params = params
        self.code = code
        self.elsecode = elsecode
    
    def eval( self, context ):
        result = ''
        for p in self.paramsgenerator( context ):
            if p.name or p.value:
                result += self.execparam( p, self.code,context )
            elif self.elsecode:
                result += self.execparam( p, self.elsecode,context )
        return result
        
    def paramsgenerator( self, context ):
        def namevalue(p):
            if isinstance(p,Node):
                return (p.name, p.eval(context))
            else:
                return (None, p)

        i=0
        ik = 0
        nparams = len(self.params)
        for p in self.params:
            (name,val) = namevalue(p)
            
            if isinstance(val,list) and not name:
                k=0
                for p_ in val:
                    (name_,val_) = namevalue(p_)
                    islast = ( i == nparams-1 ) and hasattr(k,'__len__') and (k==len(val)-1)
                    yield EvalParam( ik+k, name_, val_, islast )
                    k+=1
                ik+=k
            else:
                islast = i == nparams-1
                yield EvalParam( ik, name, val, islast )
                ik+=1
            i+=1

    def execparam(self, p, code, context ):
        mycontext = context.copy()
        mycontext['$index'] = p.pos
        mycontext['$first'] = p.pos == 0 and 'True' or ''
        mycontext['$last'] = p.islast and 'True' or ''
        mycontext['$notlast'] = (not p.islast) and 'True' or ''
        if p.name: mycontext['$key'] = p.name
        mycontext['$value'] = p.value
        return code.eval(mycontext)

    def __repr__(self):
        return 'CycleNode["%s"]:%s else:%s'%(self.params,self.code,self.elsecode)

class GroupNode( Node ):
    def __init__(self,value):
        self.value=[]
        self.value.extend(value)

    def eval(self,context):
        return self.value

    def __repr__(self):
        return 'GroupNode(%s)'%(self.value,)


class PycodeNode( Node ):
    def __init__(self, code='', globals={} ):
        self.code = code
        self.globals = globals
        if 'import' in self.code:
            exec (self.code in self.globals)
       
    def eval( self, context={} ):
        mycontext = context.copy()
        mycontext['_'] = buildaccessor( context )
        mycontext['context'] = context
        if 'import' in self.code:
            return ''
        else:
            return eval( self.code, self.globals, mycontext )

    def __repr__(self):
        return 'PycodeNode(%s)'%(self.code,)

class TypeDefNode( Node ):
    def __init__(self, name, params, code):
        self.name = name
        self.defnode = DefNode(name, params, code)

    def execute( self, target, params, contents, context ):
        mycontext = context.copy()
        mycontext['$object'] = target
        return self.defnode.execute( params, contents, mycontext )

    def __repr__(self):
        return 'TypeDefNode("%s"):%s'%(self.name,self.defnode,)
        
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
