"""
This module contains all Abstract Syntax Tree representation classes that
form a template.
"""
from StringIO import StringIO
import magro.env as env
DEF_PREFIX = '!DEF!'

class Node:
    "Base node class"
    def __init__(self):
        pass

    def eval( self, context ):
        """Returns the resultant string of evaluating this tree node
        to a context.
        
        This is equivalent to evaluating a part of the template."""
        return ''
    
    def __repr__(self):
        return 'Node'

class BlockNode( Node ):
    """Represents a sequence of nodes that should be concatenated after their
    evaluation."""
    def __init__(self,code,level=0):
        self.code=[]
        self.code.extend(code)
        self.level = level

    def eval(self,context,uselevel=False):
        """Evaluates each contained node and concatenates the result.
        
        The following implicit variables will be available in the context
        during evaluation:
        
        $level: current level of indentation of this block
        $nextlevel: $level+1
        $previouslevel: $level-1
        """
        buffer = StringIO()
        if uselevel:
            context = context.copy()
            context['$level'] = self.level
            context['$nextlevel'] = self.level+1
            if self.level: context['$previouslevel'] = self.level-1
        for s in self.code:
            text = unicode(s.eval( context ))
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
    "This should be the root node of the AST. It represents the whole template."
    def __init__(self, code=[], defs={} ):
        self.code = BlockNode(code)
        self.defs = defs
       
    def eval( self, context={} ):
        """Evaluates its single BlockNode child.
        
        Before evaluation, inserts the settings defined in env.settings to
        the context.
        """
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
    "Represents a string that will be output to the result as is."
    def __init__(self, value):
        self.value = value
       
    def eval( self, context ):
        return self.value

    def __repr__(self):
        return 'StringNode("%s")'%(self.value,)

        
class ImplicitNode( Node ):
    "Represents an Implicit symbol to be looked up in the context."
    def __init__(self, name):
        self.name = name
       
    def eval( self, context ):
        "Returns the value of the implicit symbol or empty if not defined."
        try:
            return context[ self.name ]
        except KeyError:
            return ''

    def __repr__(self):
        return 'ImplicitNode("%s")'%(self.name,)

class DefNode( Node ):
    "Represents a macro definition that can be invoqued through a CallNode."
    def __init__(self, name, params, code):
        self.name = name
        self.params = params
        self.paramnames = [ p.name for p in self.params ]
        self.code = code
        
    def expandparams( self, params, context ):
        """Returns all evaluated params in a list.
        
        If a parameter evaluates to a list, all its elements are included as
        single elements of the resultant list (i.e. flattens the parameters
        one level.)
        """
        expanded = []
        for p in params:
            val = p.eval( context )
            if hasattr(val,'__iter__'):
                expanded.extend( val )
            else:
                expanded.append( p )
        return expanded
        
    def processparams(self, params, context ):
        """Evaluates all call parameters and applies default values when one
        is not defined.
        
        All defined values that are not declared in the macro definition are
        stored in the context as the $undeclared implicit variable.
        """
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
            if not context.has_key(p.name):
                if i<=len(params) and not params[i-1].name:
                    ivar = '$%d'%(i,)
                    context[p.name] = context[ivar]
                else:
                    context[p.name] = p.eval(context)
            i+=1

    def execute( self, params, contents, context ):
        """Evaluates this macro with the given parameters and context. The
        contents parameter is stored to the context as $ before evaluation.
        """
        self.processparams( params, context)
        context['$'] = contents
        return self.code.eval(context)

    def __repr__(self):
        return 'DefNode(%s):%s'%(self.name,self.code)


class ParamNode( Node ):
    """Represents a parameter used either in a macro definition
    or in a macro call."""
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
    
    def eval(self,context):
        """Returns the result of evaluating its value
        or '' if no value was given."""
        if self.value:
            return self.value.eval(context)
        else:
            return ''

    def __repr__(self):
        return 'Param( "%s", %s )'%(self.name,self.value,)
            
class CallNode( Node ):
    "Represents a call to a macro."
    def __init__(self, name, params=[], contents=BlockNode([])):
        self.name = name
        self.params = params
        self.contents = contents
       
    def eval( self, context ):
        """Searches the macro definition to be evaluated and executes it.
        
        Macro definitions are searched in the list of macro definitions. If
        not found, its value is obtained from the context and if there is a
        macro definition to be called for the type of the obtained object,
        calls that macro. Otherwise, return the object found in the context or
        an empty string if not found.
        """
        symbol = None
        target = None

        if not context.has_key(self.name):
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
    "Support class used in cycles evaluation."
    def __init__( self, pos, name, value, islast ):
        self.pos = pos
        self.name = name
        self.value = value
        self.islast = islast
            
class CycleNode( Node ):
    """Represents a cycle that evaluates its contents once for each of its 
    parameters.
    
    If a parameter evaluates to an empty string, invoques the optional else
    block. This allows this node to be used as a conditional branch."""
    def __init__(self, params=[], code=BlockNode([]), elsecode=None ):
        self.params = params
        self.code = code
        self.elsecode = elsecode
    
    def eval( self, context ):
        """Evaluates all parameters and invoques the block of code that
        corresponds to its value."""
        result = ''
        for p in self.paramsgenerator( context ):
            if p.name or p.value:
                result += self.execparam( p, self.code,context )
            elif self.elsecode:
                result += self.execparam( p, self.elsecode,context )
        return result
        
    def paramsgenerator( self, context ):
        """Used by eval to iterate over each of the parameters. 
        Flattens the parameters one level if a parameter evaluates to an
        iterable and is not given a name."""
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
            
            if hasattr(val,'__iter__') and not name:
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
        """Evaluates the given block of code for the given param. It makes the
        following implicit values available in the context:
        
        $index: current position in the iteration, starting at 0.
        $first: True if this is the first iteration, '' otherwise.
        $last: True if this is the last iteration, '' otherwise.
        $notlast: True if this is not the last iteration, '' otherwise.
        $key: name of the parameter if given.
        $value: actual value of the parameter.
        """
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
    "Groups a list of nodes so that they evaluate to a list."
    def __init__(self,value):
        self.value=[]
        self.value.extend(value)

    def eval(self,context):
        "Returns the group of nodes."
        return self.value

    def __repr__(self):
        return 'GroupNode(%s)'%(self.value,)


class PycodeNode( Node ):
    """Represents a python expression in a template.
    
    If the expression is an 'import' statement, it will make available all
    its imported symbols in the context of all subsecuent python expressions
    in the template.
    """
    def __init__(self, code='', globals={} ):
        self.code = code
        self.globals = globals
        if 'import' in self.code:
            exec self.code in self.globals
       
    def eval( self, context={} ):
        """Evaluates the python expression. It uses the context as the map of
        local symbols available.
        
        It also makes the following symbols available:
        
        _: Function to access the context directly by a string key.
        context: context used for this call.
        """
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
    "Represents a macro call to be called when an object of a certain type is found."
    def __init__(self, name, params, code):
        self.name = name
        self.defnode = DefNode(name, params, code)

    def execute( self, target, params, contents, context ):
        "Evaluates the macro using the target as the $object implicit value."
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
