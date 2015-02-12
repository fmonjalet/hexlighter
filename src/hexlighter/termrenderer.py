import sys

from hexlighter.core import Renderer

class TermRenderer(Renderer):
    """A renderer that prints a colored output to a terminal."""

    def render(self, ebl):
        ebl = ebl.get_encoded_byte_list()
        for eb in ebl:
            for c in eb.get_qchars():
                sys.stdout.write(c.value)
        print("")

