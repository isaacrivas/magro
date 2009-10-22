"""
This module contains all Abstract Syntax Tree representation classes that
form a template.
"""
from StringIO import StringIO
DEF_PREFIX = '!DEF!'

__all__ = [
    'DEF_PREFIX',
    'BlockNode',
    'RootNode',
    'StringNode',
    'ImplicitNode',
    'DefNode',
    'ParamNode',
    'CallNode',
    'CycleNode',
    'GroupNode',
    'PycodeNode',
    'TypeDefNode'
]

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
    def __init__(self, code, level=0):
        Node.__init__( self )
        self.code = []
        self.code.extend(code)
        self.level = level

    def eval(self, context, uselevel=False):
        """Evaluates each contained node and concatenates the result.
        
        The following implicit variables will be available in the context
        during evaluation:
        
        $level: current level of indentation of this block
        $nextlevel: $level+1
        $previouslevel: $level-1
        """
        result_buf = StringIO()
        if uselevel:
            context = context.copy()
            context['$level'] = self.level
            context['$nextlevel'] = self.level+1
            if self.level:
                context['$previouslevel'] = self.level-1
        for node in self.code:
            text = unicode(node.eval( context ))
            if text:
                result_buf.write(text)

        result = result_buf.getvalue()
        result_buf.close()
        return result

    def __repr__(self):
        strcode = ''
        for node in self.code:
            strcode += '\n%s%s' % ('  '*(self.level+1), node)
        return 'BlockNode:%s' % (strcode,)


class RootNode( Node ):
    "This should be the root node of the AST. It represents the whole template."
    def __init__(self, code=None, defs=None ):
        Node.__init__( self )
        self.code = BlockNode(code)
        self.defs = defs or {}
       
    def eval( self, context=None ):
        """
        Evaluates its single BlockNode child.
        """
        if context: 
            mycontext = context.copy()
        else:
            mycontext = {}
        for key, val in self.defs.items():
            if key not in mycontext:
                mycontext[key] = val

        return self.code.eval( mycontext )
    
    def __repr__(self):
        return '\n*%s' % (self.code,)

class StringNode( Node ):
    "Represents a string that will be output to the result as is."
    def __init__(self, value):
        Node.__init__( self )
        self.value = value
       
    def eval( self, context ):
        "Simply returns the value of this node."
        return self.value

    def __repr__(self):
        return 'StringNode("%s")' % (self.value,)

        
class ImplicitNode( Node ):
    "Represents an Implicit symbol to be looked up in the context."
    def __init__(self, name):
        Node.__init__( self )
        self.name = name
       
    def eval( self, context ):
        "Returns the value of the implicit symbol or empty if not defined."
        try:
            return context[ self.name ]
        except KeyError:
            return ''

    def __repr__(self):
        return 'ImplicitNode("%s")' % (self.name,)

class DefNode( Node ):
    "Represents a macro definition that can be invoqued through a CallNode."
    def __init__(self, name, params, code):
        Node.__init__( self )
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
        for param in params:
            val = param.eval( context )
            if hasattr(val,'__iter__'):
                expanded.extend( val )
            else:
                expanded.append( param )
        return expanded
        
    def processparams(self, params, context ):
        """Evaluates all call parameters and applies default values when one
        is not defined.
        
        All defined values that are not declared in the macro definition are
        stored in the context as the $undeclared implicit variable.
        """
        exp_params = self.expandparams( params, context )
        context['$all'] = exp_params

        #evaluate params and see if they were declared.
        undeclared = []
        i = 1
        iunnamed = 0
        for param in exp_params:
            value = param.eval(context)
            
            context[ '$%d' % (i,) ] = value
            if param.name:
                context[ param.name ] = value
                if param.name not in self.paramnames:
                    ev_param = ParamNode( param.name, StringNode(value) )
                    undeclared.append( ev_param )
            else:
                iunnamed += 1
                if iunnamed > len(self.params):
                    ev_param = ParamNode( None, StringNode(value) )
                    undeclared.append( ev_param)
            i += 1
        context['$undeclared'] = undeclared
        
        #search default values for undefined parameters
        i = 1
        for param in self.params:
            if not context.has_key( param.name ):
                if i <= len(exp_params) and not exp_params[i-1].name:
                    ivar = '$%d' % (i,)
                    context[param.name] = context[ivar]
                else:
                    context[param.name] = param.eval(context)
            i += 1

    def execute( self, params, contents, context ):
        """Evaluates this macro with the given parameters and context. The
        contents parameter is stored to the context as $ before evaluation.
        """
        self.processparams( params, context)
        context['$'] = contents
        return self.code.eval(context)

    def __repr__(self):
        return 'DefNode(%s):%s' % (self.name, self.code)


class ParamNode( Node ):
    """Represents a parameter used either in a macro definition
    or in a macro call."""
    def __init__(self, name, value=None):
        Node.__init__( self )
        self.name = name
        self.value = value
    
    def eval(self, context):
        """Returns the result of evaluating its value
        or '' if no value was given."""
        if self.value:
            return self.value.eval( context )
        else:
            return ''

    def __repr__(self):
        return 'Param( "%s", %s )' % (self.name, self.value,)
            
class CallNode( Node ):
    "Represents a call to a macro."
    def __init__(self, name, params=None, contents=None):
        Node.__init__( self )
        self.name = name
        self.params = params or []
        self.contents = contents or BlockNode([])
       
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
            except KeyError:
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
        return 'CallNode("%s"):%s' % (self.name, self.contents)    

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
    def __init__(self, params=None, code=None, elsecode=None ):
        Node.__init__( self )
        self.params = params or []
        self.code = code or BlockNode([])
        self.elsecode = elsecode
    
    def eval( self, context ):
        """Evaluates all parameters and invoques the block of code that
        corresponds to its value."""
        result = ''
        for param in self.paramsgenerator( context ):
            if param.name or param.value:
                result += self.execparam( param, self.code, context )
            elif self.elsecode:
                result += self.execparam( param, self.elsecode, context )
        return result
        
    def paramsgenerator( self, context ):
        """Used by eval to iterate over each of the parameters. 
        Flattens the parameters one level if a parameter evaluates to an
        iterable and is not given a name."""
        def namevalue(param):
            "Obtains a tuple with the name and value of the parameter."
            if isinstance( param, Node):
                return (param.name, param.eval(context))
            else:
                return (None, param)

        i = 0
        i_k = 0
        nparams = len(self.params)
        for param in self.params:
            (name, val) = namevalue(param)
            
            if hasattr(val,'__iter__') and not name:
                k = 0
                for param_ in val:
                    (name_, val_) = namevalue(param_)
                    islast = ( i == nparams-1 ) and hasattr(k,'__len__') and (k==len(val)-1)
                    yield EvalParam( i_k+k, name_, val_, islast )
                    k += 1
                i_k += k
            else:
                islast = i == nparams-1
                yield EvalParam( i_k, name, val, islast )
                i_k += 1
            i += 1

    def execparam(self, param, code, context ):
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
        mycontext['$index'] = param.pos
        mycontext['$first'] = param.pos == 0 and 'True' or ''
        mycontext['$last'] = param.islast and 'True' or ''
        mycontext['$notlast'] = (not param.islast) and 'True' or ''
        if param.name:
            mycontext['$key'] = param.name
        mycontext['$value'] = param.value
        return code.eval(mycontext)

    def __repr__(self):
        return 'CycleNode["%s"]:%s else:%s' % (self.params, self.code, self.elsecode)

class GroupNode( Node ):
    "Groups a list of nodes so that they evaluate to a list."
    def __init__(self, value):
        Node.__init__( self )
        self.value = []
        self.value.extend(value)

    def eval(self, context):
        "Returns the group of nodes."
        return self.value

    def __repr__(self):
        return 'GroupNode(%s)' % (self.value,)


class PycodeNode( Node ):
    """Represents a python expression in a template.
    
    If the expression is an 'import' statement, it will make available all
    its imported symbols in the context of all subsecuent python expressions
    in the template.
    """
    COMMON_GLOBALS = {}
    
    def __init__(self, code='', globals=None ):
        Node.__init__( self )
        self.code = code
        self.globals = globals or PycodeNode.COMMON_GLOBALS
        if 'import' in self.code:
            exec self.code in self.globals
       
    def eval( self, context=None ):
        """Evaluates the python expression. It uses the context as the map of
        local symbols available.
        
        It also makes the following symbols available:
        
        _: Function to access the context directly by a string key.
        context: context used for this call.
        """
        mycontext = context and context.copy() or {}
        mycontext['_'] = buildaccessor( context )
        mycontext['context'] = context
        if 'import' in self.code:
            return ''
        else:
            return eval( self.code, self.globals, mycontext )

    def __repr__(self):
        return 'PycodeNode(%s)' % (self.code,)

class TypeDefNode( Node ):
    "Represents a macro call to be called when an object of a certain type is found."
    def __init__(self, name, params, code):
        Node.__init__( self )
        self.name = name
        self.defnode = DefNode(name, params, code)

    def execute( self, target, params, contents, context ):
        "Evaluates the macro using the target as the $object implicit value."
        mycontext = context.copy()
        mycontext['$object'] = target
        return self.defnode.execute( params, contents, mycontext )

    def __repr__(self):
        return 'TypeDefNode("%s"):%s' % (self.name, self.defnode,)
        
def buildaccessor( ctx ):
    "Creates the accessor function to be used in python expressions (_)"
    def accessor(key):
        "The actual accessor function."
        return ctx[key]
    return accessor

def gettypenames( obj ):
    """Obtains the name of the class of the object and of the classes it is a
    subclass of."""
    thetype = type( obj )
    if thetype.__name__ == 'instance':
        thetype = obj.__class__
    
    result = [thetype.__name__]
    result.extend( gettypebases(thetype) )
    
    return result

def gettypebases(thetype):
    "Obtains the list of parent classes of a type. Ordered from bottom to top."
    result = []
    processtypebases(thetype, result, 0)
    return [ t for l in result for t in l]
    
def processtypebases(thetype, levels, currlevel):
    """Gets the parents classes of a type recursively. Returns a list of list
    where each position stores all the classes in that level of the tree."""
    while (currlevel >= len(levels)):
        levels.append([])
    for base in thetype.__bases__:
        levels[currlevel].append(base.__name__)
    for base in thetype.__bases__:
        processtypebases(base, levels, currlevel+1)
