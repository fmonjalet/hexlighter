
def is_byte(b):
    """ Returns True if b is a char byte """
    return isinstance(b, str) and len(b) == 1


def is_byte_list(bl):
    """ Returns True if bl is a char byte list """
    res = isinstance(bl, list)
    if res and len(bl) > 0:
        return is_byte(bl[0])
    return res


class RawByte(object):
    """ A raw byte with some additionnal information.

        Attributes:
            @value: internal value (an str byte)
            @diff: another RawByte to compare self with.
            @highlight: boolean indicating whether this byte is highlit or not.
    """

    def __init__(self, value, diff=None, highlight=False):
        if not is_byte(b):
            raise ValueError("a byte (as str) should be provided")
        self.value = value
        self.diff = diff
        self.highlight = highlight


class RawByteList(object):
    """ An abstraction for a list of bytes. Used to store and process bytes of
        input. Inputs can be processed towards a reference RawByteList
        (self.ref).
    """
    def __init__(self):
        self._bytes = []
        self.ref = None
        self.comment = ""

    def add_byte(self, b):
        """ Adds a byte to this RawByteList.
            
            Args:
                @b: one str character.
        """
        if not is_byte(b):
            raise ValueError("a byte (as str) should be provided")
        self._bytes.append(RawByte(b))

    def set_bytes(self, byte_list):
        """ Set byte list. This converts the byte list to an internal
            representation.
        """
        self._bytes = [RawByte(b) for b in byte_list]

    def process(self):
        # shape tweaks (start + width + alignment)
        # filter (byte + size)
        # highlight
        # diff
        pass
