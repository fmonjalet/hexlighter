import sys

from hexlighter.core import Renderer
from hexlighter import conf

no_color = '\033[39;49m'
reset_style = '\033[0m'

if conf.retro:
    c1 = reset_style
    c2 = '\033[34;40m'
    d1 = '\033[4m'
    d2 = '\033[24m'
    highlight_color = '\033[1;31m'
    diff_color = '\033[1;32m'
else:
    c1 = '\033[97;100m'
    c2 = '\033[94;40m'
    d1 = '\033[4m'
    d2 = '\033[24m'
    highlight_color = '\033[91m'
    diff_color = '\033[92m'
if not conf.color:
    c1 = c2 = d1 = d2 = ""

col_c = [c1, c2]
ncc = len(col_c)

line_c = [d1, d2]
nlc = len(line_c)

class TermRenderer(Renderer):
    """A renderer that prints a colored output to a terminal."""

    def __init__(self):
        super(TermRenderer, self).__init__()
        self.line_no = 0

    def render(self, ebl):
        out = []
        out.append(line_c[self.line_no % nlc])

        byte_list = ebl.get_encoded_byte_list()
        for i, byte in enumerate(byte_list):
            out.append(col_c[i % ncc])
            for c in byte.get_qchars():
                if conf.diff and c.diff:
                    out.append(diff_color)
                if c.highlight:
                    out.append(highlight_color)
                out.append(c.value)

        out.append(reset_style)
        print ''.join(out)
        self.line_no += 1

