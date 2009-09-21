import magro.parser as parser
import magro.env as env
from magro.context import Context
from io import StringIO

class TemplateBridge(object):
    def init(self, builder, theme=None, dirs=None):
        env.path.extend( builder.config.templates_path )

    def newest_template_mtime(self):
        return 0
        
    def render(self, template, context):
        filename = env.searchfile(template)
        
        buffer = ''
        if filename:
            f = open(filename,'r')
            buffer = f.read()
            f.close()
        else:
            raise Exception( 'Template not found: %s'%( template, ) )
        
        return buffer

    def render_string(self, template, context):
        try:
            ctx = Context(context)
            return parser.parse(template,ctx)
        except:
            return template
        
