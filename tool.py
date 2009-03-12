import magro.parser as parser
import sys
import os.path
from optparse import OptionParser

def tool( thefile ):
    text = thefile.read()
    return parser.parse( text )

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
    (options, args) = opparser.parse_args()

    if options.outfile and options.fileext:
        opparser.error("options -o and -x are mutually exclusive")
    
    result = ''
    if len(args) > 0:
        filenames = args
        for filename in filenames:
            if options.verbose:
                print 'Processing %s ...'%(filename,)
            thefile = open( filename, 'r' )
            try:
                res = tool( thefile )
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
        result = tool( sys.stdin )
    print result
