import magro.parser as parser
import magro.env as env
from magro.context import Context
import sys
import os.path
from optparse import OptionParser

def tool( thefile, pyfile='' ):
    text = thefile.read()
    context = Context()
    if pyfile:
        exec 'from %s import *'%(pyfile.rstrip('.py'),) in context
    return parser.parse( text, context )

if __name__ == '__main__':
    usage = 'usage: %prog [options] [filename]'
    version = '1.0'
    opparser = OptionParser(usage=usage, version="%%prog %s"%(version,))
    opparser.add_option( '-o','--output', dest='outfile',
                         help='Write output to FILE', metavar='FILE' )
    opparser.add_option( '-d','--dir', dest='outdir',
                         help='Write output to DIR directory (used with -x)', metavar='DIR' )
    opparser.add_option( '-x','--ext', dest='fileext',
                         help='Use input file name with EXT as extension as output filename', metavar='EXT' )
    opparser.add_option( '-v', action='store_true', dest='verbose', default=False,
                         help='Set verbose mode' )
    opparser.add_option( '-s', action='append', dest='settings', metavar='KEY=VALUE',
                         help='Set magro.env.settings[KEY] = VALUE' )
    opparser.add_option( '-p', dest='pyfile', metavar='PY_FILE',
                         help='Run PY_FILE and use its globals directory as context' )
    (options, args) = opparser.parse_args()

    if options.outfile and options.fileext:
        opparser.error("options -o and -x are mutually exclusive")
    
    result = ''
    if len(args) > 0:
        if options.settings:
            for s in options.settings:
                (key,value,) = s.split('=')
                env.settings[key] = value
    
        filenames = args
        for filename in filenames:
            if options.verbose:
                print 'Processing %s ...'%(filename,)
            thefile = open( filename, 'r' )
            try:
                res = tool( thefile, options.pyfile )
            finally:
                thefile.close()
            
            outputfile = None
            if options.outfile:
                outputfile = open( options.outfile, 'a' )
            elif options.fileext:
                fname = '%s.%s'%(filename.rsplit('.',1)[0], options.fileext,)
                if options.outdir:
                    fname = os.path.join( options.outdir, os.path.split(fname)[-1] )
                if options.verbose:
                    print 'Writing to %s...'%(fname,)
                outputfile = open( fname, 'w' )

            if outputfile:
                try:
                    outputfile.write( res )
                finally:
                    outputfile.close()
            else:
                result += res
    else:
        result = tool( sys.stdin, options.pyfile )
    print result
