from IPython.core.magic import (Magics, magics_class, line_cell_magic)
from IPython.display import display, HTML
import sys
import io
from typing import Optional

from .parser import parse_thinkpy
from .interpreter import ThinkPyInterpreter

@magics_class
class ThinkPyMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        self.explain_mode = False

    def format_error_message(self, error):
        """Format error message with proper styling"""
        css = """
        <style>
            .thinkpy-error {
                font-family: monospace;
                white-space: pre;
                background-color: #fff0f0;
                padding: 15px;
                border-left: 4px solid #ff0000;
            }
            .error-content {
                background-color: #ffffff;
                padding: 15px;
                border-radius: 3px;
            }
            .error-title {
                color: #ff0000;
                margin-bottom: 15px;
            }
            .error-location {
                color: #000;
                line-height: 1;
                text-align: left;
            }
            .context-label {
                color: #000;
                line-height: 1;
                text-align: left;
            }
            .token-info {
                color: #000;
                line-height: 1;
                text-align: left;
            }
            .source-code {
                color: #000;
                line-height: 1;
                text-align: left;
            }
            .code-line {
                white-space: pre;
                line-height: 1;
                text-align: left;
            }
            .line-number {
                display: inline-block;
                width: 30px;
                color: #000;
            }
            .line-content {
                display: inline;
                color: #000;
            }
            .error-line .line-number {
                color: #ff0000;
            }
            .error-line .line-content {
                color: #ff0000;
            }
            .arrow {
                color: #ff0000;
                margin-right: 5px;
            }
        </style>
        """
        
        error_html = f""" 
        {css}
        <div class="thinkpy-error">
        <div class="error-content" style="color: black;">
        <span style="color: red;">
        ThinkPy Error: {error.message}
        </span> 
        Line: {error.line} 
        Column: {error.column} 
        Context: Near token: '{error.token}'
        </span>
        Source code:
        """    
        
        # Format source code lines
        if hasattr(error, 'source_snippet'):
            lines = error.source_snippet.split('\n')
            for line in lines:
                if '->' in line:
                    # Error line
                    number = line.split(':')[0].strip().replace('->', '')
                    code = line.split(':')[1] if ':' in line else ''
                    error_html += f"""
<p style="color: red;">--> {number}:{' ' * 8}{code.strip()}</p>"""
                else:
                    # Normal line
                    if ':' in line:
                        number, code = line.split(':', 1)
                        error_html += f"""
{number.strip()}:{' ' * 8}{code.strip()}"""
        
        error_html += """
            </div>
        </div>"""
        return error_html

    @line_cell_magic
    def thinkpy(self, line='', cell=None):
        """Execute ThinkPy code in a Jupyter notebook cell."""
        if cell is None:
            cell = line
            line = ''

        self.explain_mode = '--explain' in line
        
        try:
            # Parse and execute the code
            ast = parse_thinkpy(cell)
            if ast is None:
                display(HTML(self.format_error_message("Failed to parse ThinkPy code")))
                return
            
            interpreter = ThinkPyInterpreter(explain_mode=self.explain_mode)
            interpreter.execute(ast)
            
        except Exception as e:
            if hasattr(e, 'format_message'):
                error_html = self.format_error_message(e)
            else:
                error_html = self.format_error_message(type('ThinkPyError', (), {
                    'message': str(e),
                    'line': None,
                    'column': None,
                    'token': '',
                    'source_snippet': ''
                }))
            display(HTML(error_html))

def load_ipython_extension(ipython):
    """Register the ThinkPy magic when the extension is loaded."""
    ipython.register_magics(ThinkPyMagics)