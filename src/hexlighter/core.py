from hexlighter import conf

def is_byte(b):
    """ Returns True if b is a char byte """
    return isinstance(b, str) and len(b) == 1


def is_byte_list(bl):
    """ Returns True if bl is a char byte list """
    res = isinstance(bl, list)
    if res and len(bl) > 0:
        return is_byte(bl[0])
    return res


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


class NoByte(RawByte):
    """Represent an empty RawByte."""
    def __init__(self, diff=None, highlight=None):
        RawByte.__init__(self, None, diff, highlight)


class RawByteList(object):
    """ An abstraction for a list of bytes. Used to store and process bytes of
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
        for raw_byte, diff_byte in zip(self._pbytes, ref._pbytes):
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

