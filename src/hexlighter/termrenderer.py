import sys

from hexlighter.core import Renderer, encoding2len
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

def build_rule(l, shift=0, byte_len=2, start=0):
    """Returns a string representing a rule with a number every 8 graduations.

    Args:
        @l: length of the rule, in number of graduations
        @shift: number of spaces to prepend to the rule
        @byte_len: size of one graduation
        @start: first graduation number
    """
    ret = []
    ret.append(' '*shift)
    i = 0
    byte_rule = "+" + "-" * (byte_len - 1)
    for i in xrange(0, l-8, 8):
        ret.append("|" + (byte_rule * 8)[1:])
    ret.append("|" + (byte_rule * (l % 8))[1:])
    ret.append('\n')
    ret.append(' '*shift)
    fmt = "%%-%dd" % (byte_len*8)
    for i in xrange(start, start+l, 8):
        ret.append(fmt % i)
    return ''.join(ret).rstrip()

class TermRenderer(Renderer):
    """A renderer that prints a colored output to a terminal."""

    def __init__(self):
        super(TermRenderer, self).__init__()
        self.line_no = 0
        self.shift = None
        self.max_len = 0

    def render(self, ebl):
        out = []
        comment = (ebl.comment + " ") if ebl.comment else ""
        out.append(ebl.comment)
        out.append(" ")
        out.append(line_c[self.line_no % nlc])

        shift = len(comment)
        self.shift = shift

        displayed = shift
        i = 0
        byte_list = ebl.get_encoded_byte_list()
        if not byte_list:
            return
        l = 0
        for byte in byte_list:
            l += 1
            displayed += encoding2len[conf.enc]
            if displayed > conf.disp_width:
                out.append(reset_style)
                out.append("\n")
                out.append(" " * shift)
                displayed = shift + encoding2len[conf.enc]
                i = 0

            out.append(col_c[i % ncc])
            for c in byte.get_qchars():
                if conf.diff and c.diff:
                    out.append(diff_color)
                if c.highlight:
                    out.append(highlight_color)
                out.append(c.value)
            out.append(reset_style)
            i += 1

        self.max_len = max(self.max_len, l)
        out.append(reset_style)
        print(''.join(out))
        self.line_no += 1

    def finalize(self):
        self._print_rule()

    def _print_rule(self):
        start = 0
        max_dump_width = conf.disp_width - self.shift
        max_bytes = max_dump_width // encoding2len[conf.enc]

        out = []
        for i in xrange(self.max_len//max_bytes + 1):
            out.append(build_rule(max_bytes, self.shift,
                                  encoding2len[conf.enc],
                                  start=i*max_bytes))
        print('\n'.join(out))

