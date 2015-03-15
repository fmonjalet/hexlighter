import matplotlib
import matplotlib.pyplot as plt

from hexlighter.core import Renderer
from hexlighter import conf

normal_color = 0
highlight_color = 0.25
diff_color = 0.5
no_color = 1

cdict = {
      'red'  : ((0.00, 1.00, 1.00),
                (0.25, 1.00, 1.00),
                (0.50, 0.00, 0.00),
                (0.75, 1.00, 1.00),
                (1.00, 0.00, 0.00)),

      'green': ((0.00, 1.00, 1.00),
                (0.25, 0.00, 0.00),
                (0.50, 1.00, 1.00),
                (0.75, 1.00, 1.00),
                (1.00, 0.00, 0.00)),

      'blue' : ((0.00, 1.00, 1.00),
                (0.25, 0.00, 0.00),
                (0.50, 0.00, 0.00),
                (0.75, 0.00, 0.00),
                (1.00, 0.00, 0.00)),
}

hexlighter_cm = matplotlib.colors.LinearSegmentedColormap('hexlighter', cdict,
                                                          1024)

class DrawRenderer(Renderer):
    """A renderer that prints a colored output to a terminal."""

    def __init__(self):
        super(DrawRenderer, self).__init__()
        self.lines = []

    def render(self, ebl):
        byte_list = ebl.get_encoded_byte_list()
        if not byte_list:
            return

        cur_line = []
        self.lines.append(cur_line)

        for byte in byte_list:
            color = 0.
            if byte.raw_byte.is_diff():
                color += diff_color
            if byte.raw_byte.highlight:
                color += highlight_color
            cur_line.append(color)

    def finalize(self):
        max_len = max(len(line) for line in self.lines)
        
        for line in self.lines:
            line += [no_color] * (max_len - len(line))

        fig, ax = plt.subplots()
        ax.imshow(self.lines, cmap=hexlighter_cm, vmin=0, vmax=1,
                  interpolation='nearest')
        plt.show()

