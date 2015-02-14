import binascii

from hexlighter import conf


my_printables = map(chr, range(0x20, 0x7e))

encoding2len = {
    'hex':2,
    'bin':8,
}

def is_byte(b):
    """Returns True if b is a char byte"""
    return isinstance(b, str) and len(b) == 1


class Decoder(object):
    """Base class. Child classes allow transforming a line of input to a
    RawByteList.
    """

    name = None

    def decode(self, input_line):
        """Decodes an @input_line (str) to a @return RawByteList."""
        raise NotImplementedError("Abstract method")


class CommentedHexDecoder(object):
    """Input must be <text> <hex>. For example:

    this is a comment  0a3b640058c4a2
    """

    name = "hex"

    def decode(self, input_line):
        rbl = RawByteList()
        sp = input_line.strip().rsplit(" ", 1)
        if len(sp) > 1:
            rbl.comment = sp[0]
        str_hex = sp[-1]
        try:
            raw_bytes = binascii.unhexlify(str_hex)
            rbl.set_bytes(raw_bytes)
        except TypeError:
            rbl.comment = "%s %s" % (rbl.comment, str_hex)
        return rbl


class RawByteFilter(object):
    """A class to filter RawByteLists."""

    def __init__(self):
        self.filter = {}
        self.anti_filter = {}

    def add_filter(self, filter_spec):
        """Adds a constraint on this filter.

        Args:
            @filter_spec: a str of the following form:
                n{=,!}XX, with n a decimal integer and XX a hex value for a
                byte. n=XX will keep lines that match the rule, n!XX the lines
                that do not match the rule.
        """
        if "=" in filter_spec:
            filter = self.filter
            l = filter_spec.split("=")
        elif "!" in filter_spec:
            filter = self.anti_filter
            l = filter_list.split("!")
        else:
            raise ValueError("filter_spec must match n{=,!}XX")
        n = int(l[0])
        byte = chr(int(l[1], 16))
        filter[n] = byte

    def rem_filter(self, byte_off):
        """Deletes all filters concerning @byte_off offset."""
        if byte_off in self.filter:
            del(self.filter[byte_off])
        if byte_off in self.anti_filter:
            del(self.anti_filter[byte_off])

    def add_filters(self, filter_list):
        """Adds a list of constraints on this filter. See add_filter doc for
        the constraint syntax.

        Args:
            @filter_list: a list of str representing constraints (see
                add_filter).
        """
        for f in filter_list:
            self.add_filter(f)

    def match(self, rb_list):
        """True if a RawByteList matches this filter."""
        blist = rb_list.get_bytes()
        l = len(blist)
        for index, value in self.filter.iteritems():
            if index >= l or blist[index].value != value:
                return False
        for index, value in self.anti_filter.iteritems():
            if index < l and blist[index].value == value:
                return False
        return True


class RawByte(object):
    """A raw byte with some additionnal information.

    Attributes:
        @value: internal value (a str byte)
        @diff: another RawByte to compare self with.
        @highlight: boolean indicating whether this byte is highlit or not.
    """

    def __init__(self, value, diff=None, highlight=False):
        if not is_byte(value):
            raise ValueError("a byte (as str) should be provided")
        self.value = value
        self.diff = diff
        self.highlight = highlight

    def __cmp__(self, other):
        if not isinstance(other, RawByte):
            return 1
        else:
            return cmp(self.value, other.value)

    def __str__(self):
        return "RawByte(%s)" % binascii.hexlify(self.value)


class NoByte(RawByte):
    """Represent an empty RawByte."""
    def __init__(self, diff=None, highlight=None):
        RawByte.__init__(self, None, diff, highlight)

    def __str__(self):
        return "NoByte"


class RawByteList(object):
    """An abstraction for a list of bytes. Used to store and process bytes of
    input. Inputs can be processed towards a reference RawByteList (self.ref).
    """
    def __init__(self):
        self._bytes = []
        # Processed bytes
        self._pbytes = None
        self.ref = None
        self.comment = ""
        self.is_processed = False

    def add_byte(self, b):
        """Adds a byte to this RawByteList.
            
        Args:
            @b: one str character.
        """
        if not is_byte(b):
            raise ValueError("a byte (as str) should be provided")
        self._bytes.append(RawByte(b))

    def set_bytes(self, byte_list):
        """Set byte list. This converts the byte list to an internal
        representation.

        Args:
            @byte_list: a list of bytes as characters (['\\x05', 'm', ...])
                or a str ('\\x05m...')
        """
        self._bytes = [b for b in byte_list]

    def set_ref(self, ref_raw_bytes):
        """Sets a reference byte list to be diffed with.

        Args:
            @ref_raw_bytes: a RawByteList instance.
        """
        self.ref = ref_raw_bytes

    def get_bytes(self):
        """Returns a list of bytes processed. By default, all the processing
        parameters are taken from the conf.

        Return:
            a list of char bytes that may contain None bytes:
            ['a', None, '\x00', ...]
        """
        if not self.is_processed:
            self.process()
        return self._pbytes

    def process(self):
        """Processes the raw bytes to reshape, filter, highlight and diff
        this line."""
        self.is_processed = True
        self._pbytes = [RawByte(b) for b in self._bytes]
        # shape tweaks (start + width + alignment)
        self._reshape()
        # filter (byte + size)
        self._filter()
        # highlight
        self._highlight()
        # diff
        self._diff()

    def _reshape(self):
        """Applies all the filters that affect the shape of a RawByteList,
        with values taken from the conf.

        This includes : start, width and align
        """
        self._apply_start()
        self._apply_width()
        self._apply_align()

    def _filter(self):
        """Applies filters that may set the processed bytes to [] if this
        RawByteList does not match the filters.
        
        This includes: min, byte filter"""
        self._apply_min()
        self._apply_byte_filter()

    def _highlight(self, start=None, width=None, cycle=None):
        """Sets the highlight flat on highlit bytes"""
        if (start is None or width is None) and conf.highlight is None:
            return
        start = start if start is not None else conf.highlight[0]
        width = width if width is not None else conf.highlight[1]
        cycle = cycle if cycle is not None else conf.cycle
        l = len(self._pbytes)
        if l < start:
            return
        end = min(l, start + width)
        if cycle:
            for i in range(start, l - width, cycle):
                for k in range(i, i + width):
                    self._pbytes[i].highlight = True
        else:
            for i in range(start, start + width):
                self._pbytes[i].highlight = True

    def _diff(self):
        if self.ref:
            for raw_byte, diff_byte in zip(self._pbytes, self.ref._pbytes):
                raw_byte.diff = diff_byte

    def _apply_start(self, start=None):
        start = start if start is not None else conf.start
        if len(self._pbytes) < start:
            self._pbytes = []
        else:
            self._pbytes = self._pbytes[start:]

    def _apply_width(self, width=None):
        width = width if width is not None else conf.width
        if len(self._pbytes) > width:
            self._pbytes = self._pbytes[:width]

    def _apply_align(self, start=None, end=None):
        if (start is None or end is None) and conf.align is None:
            return
        start = start if start is not None else conf.align[0]
        end   = end   if end   is not None else conf.align[1]
        l = len(self._pbytes)
        if end > l:
            dif = end - l
            self._pbytes[start:start] = [NoByte()] * dif

    def _apply_min(self, min=None):
        if min is None:
            min = conf.min
        if len(self._pbytes) < min:
            self._pbytes = []

    def _apply_byte_filter(self, rules=None):
        """Applies a RawByteFilter on self, constructed with @rules or
        conf.filter if @rules is None. @rule is a list of constraints, as
        specified the in RawByteFilter.add_filter doc."""
        rules = rules if rules is not None else conf.filter
        f = RawByteFilter()
        f.add_filters(rules)
        if not f.match(self):
            self._pbytes = []


class QualifiedChar(object):
    """A simple character with special qualifiers (diff, highlight)
    
    Attributes:
        @value: a char
        @diff: boolean
        @highlight: boolean
    """

    def __init__(self, value, diff=None, highlight=None):
        self.value = value
        self.diff = diff
        self.highlight = highlight


class EncodedByte(object):
    """Represents an encoded RawByte

    Attributes:
        @value: a RawByte
        @chars: a list of QualifiedChars
    """

    def __init__(self, raw_byte):
        self.raw_byte = raw_byte
        self.chars = []

    def get_qchars(self):
        """Returns a list of correctly qualified QualifiedChar that can
        be used to render this encoded byte."""
        if not self.chars:
            self.encode()
        return self.chars

    def encode(self, encoding=None):
        """Triggers the (re)generation of the internal list of QualifiedChar.
        Automatically called when get_qchars is called. Can be called to force
        reencoding.
        """
        enc = encoding if encoding is not None else conf.enc
        self.chars = [QualifiedChar(c)
                      for c in self._encode_raw_byte(self.raw_byte, enc)]
        if self.raw_byte.diff is None:
            diff_chars = self.chars
        else:
            diff_chars = [QualifiedChar(c)
                      for c in self._encode_raw_byte(self.raw_byte.diff, enc)]
        if self.raw_byte.diff is not None:
            diff = (self.raw_byte != self.raw_byte.diff)
        else:
            diff = False
        for myqc, refqc in zip(self.chars, diff_chars):
            if myqc.value != refqc.value or (diff and not conf.precision):
                myqc.diff = True
            if self.raw_byte.highlight:
                myqc.highlight = True

    def _encode_raw_byte(self, raw_byte, encoding):
        # ASCII option
        if isinstance(raw_byte, NoByte) or raw_byte is None:
            return " " * encoding2len[encoding]
        if conf.ascii and raw_byte.value in my_printables:
            return raw_byte + " " * (encoding2len[encoding]-1)
        if encoding == 'hex':
            return binascii.hexlify(raw_byte.value)
        elif encoding == 'bin':
            return "{:08b}".format(ord(raw_byte))
        else:
            raise ValueError("Unknown encoding: %s" % encoding)


class EncodedByteList(object):
    """Represents a RawByteList encoded as characters (hex, bin...)

    Attributes:
        @rbl: the RawByteList this object represents
    """
    
    def __init__(self, raw_byte_list):
        self.rbl = raw_byte_list
        self._ebl =  [EncodedByte(rb) for rb in self.rbl.get_bytes()]

    def get_encoded_byte_list(self):
        """Returns an EncodedByteList generated from the internal RawByteList.
        """
        return self._ebl


class Renderer(object):
    """ABSTRACT. A class that is able to render an EncodedByteList to a user.
    """

    def render(self, ebl):
        """ABSTRACT. Render an EncodedByteList.

        Args:
            @ebl: an EncodedByteList
        """
        raise NotImplementedError("Abstract method")

