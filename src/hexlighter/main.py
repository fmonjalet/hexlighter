from hexlighter.core import *
from hexlighter import conf
from hexlighter.termrenderer import TermRenderer

if __name__ == "__main__":
    f = open(conf.file, "r")
    renderer = TermRenderer()
    decoder = CommentedHexDecoder()
    for line in f:
        rbl = decoder.decode(line)
        ebl = EncodedByteList(rbl)
        renderer.render(ebl)
