import argparse
from collections import OrderedDict

class ConfParam(object):
    """ Represent a global parameter of a program """
    def __init__(self, name, shortname="", type=bool, nargs=0, help="",
                 syntax=("arg"), default=None, choices=None):
        self.name = name
        self.shortname = shortname
        self.type = type
        self.nargs = nargs
        self.help = help
        self.syntax = syntax
        self.default = default
        self.choices = choices

    def add_to_parser(self, parser):
        args = []
        kwargs = {}
        args.append("--" + self.name)
        if self.shortname:
            args.append("-" + self.shortname)
        if self.type == bool:
            kwargs["action"] = "store_true"
        else:
            kwargs["type"] = self.type
            kwargs["metavar"] = self.syntax
        kwargs["help"] = self.help
        kwargs["default"] = self.default
        if self.type != bool and self.nargs == 0: 
            nargs = len(self.syntax) if isinstance(self.syntax, tuple) else 1
        else:
            nargs = self.nargs
        if nargs != 0:
            kwargs["nargs"] = nargs
        if self.choices:
            kwargs["choices"] = self.choices
        parser.add_argument(*args, **kwargs)


available_encodings = ['hex', 'bin']

opt = OrderedDict()
opt['color']     = ConfParam('color', shortname='c',
                    help="Colors bytes to clarify the hexdump")
opt['diff']      = ConfParam('diff', shortname='d',
                    help="Highlights differences between successive lines.")
opt['precision'] = ConfParam('precision', 'p',
                    help="Diff is as precise as the current encoding allows it "
                    "to be")
opt['master']    = ConfParam('master', shortname='m',
                    help="When enabling diff, the diff is always done with the "
                    "first line.")
opt['highlight'] = ConfParam('highlight', shortname="l", type=int,
                    syntax=("offset", "size"),
                    help="Highlights @size bytes from @offset")
opt['cycle']     = ConfParam('cycle', type=int, syntax=("cycle-length"),
                    help="Highlit bytes are now highlit cyclically")
opt['enc']       = ConfParam('enc', 'e', type=str, choices=available_encodings,
                    syntax=("encoding"), default='hex',
                    help="Encoding of bytes when displayed")
opt['ascii']     = ConfParam('ascii', shortname='a',
                    help="Displays most displayable bytes as ascii characters")
opt['start']     = ConfParam('start', 's', type=int, syntax=("start"),
                    help="Start offset: cuts the @start first bytes of each "
                    "line")
opt['width']     = ConfParam('width', shortname='w', type=int, syntax=("width"),
                    help="Maximum width (in bytes) to display")
opt['align']     = ConfParam('align', type=int, syntax=('start', 'end'),
                    help="Aligns every line to end at @end (or further), by "
                    "shifting its content from @start to the right. Works with "
                    "negative indeces.")
opt['min']       = ConfParam('min', type=int, syntax=("min_size"),
                    help="Minimum size to display")
opt['filter']    = ConfParam('filter', shortname='f', type=str, nargs='+',
                    syntax="n{=,!}XX",
                    help="Filter lines that have byte @n set to @XX (in hex). "
                    "Use n=XX to keep lines that match and n!XX for lines that "
                    "do not match")
opt['sort']      = ConfParam('sort', type=int, syntax=("from_offset"),
                    default=0,
                    help="Sorts the lines based on the [@from_offset:end] part "
                    "of the line")
opt['retro']     = ConfParam('retro',
                    help="Enables very basic coloring for old terminals")
opt['disp-width'] = ConfParam('disp-width', type=int, syntax=("width"),
                     help="Maximum amount of character to display. Default is "
                     "computed from the terminal properties.")
opt['ui']        = ConfParam('ui', 'x',
                    help="Start hexlighter's ncurses interface")

parser = argparse.ArgumentParser()
for arg in opt.itervalues():
    arg.add_to_parser(parser)
args = parser.parse_args()

if args.w is not None:
    args.w += args.s

if args.sort is not None:
    args.sort += args.s

globals().update(vars(args))

