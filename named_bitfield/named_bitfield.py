"""
Create collections of named fixed width integers backed by python ints
or longs (as appropriate) and with clean interfaces to the fields.
"""

from collections import OrderedDict, namedtuple


class BaseNamedBitfield(object):
    """Baseclass for named bitfields.  Don't implement or instantiate this,
    instead call mutable_named_bitfield or immutable_named_bitfield as needed.
    """
    _field_mapping = {}

    def __init__(self, *args, **kwargs):
        """closuer to initilize the new class
        """
        self._bitstring = 0
        args = list(args)
        vals = []
        fieldnames = self._field_mapping.keys()
        # validate kwargs
        for key in kwargs:
            if key not in fieldnames:
                raise TypeError("%s got unexpected keyword argument %s"
                                % (self.__class__.__name__, key))
        while args:
            vals.insert(0, args.pop(0))
            fieldnames.pop(0)
        while fieldnames:
            vals.insert(0, kwargs.get(fieldnames.pop(0), 0))
        self._build_from_vals(vals)

    def _build_from_vals(self, vals):
        """Construct a bitstring from a spec and a series of values
        """
        self._bitstring = 0
        for field_spec, value in zip(self._field_mapping.values(), vals):
            if bitwidth(value) > field_spec.width:
                raise ValueError("%d will not fit in %d bit wide field",
                                 value, field_spec.width)
            self._bitstring = self._bitstring << field_spec.width
            self._bitstring |= value

    def __cmp__(self, other):
        return int(self) - int(other)

    def __int__(self):
        return self._bitstring

    def __long__(self):
        return self._bitstring

    def __oct__(self):
        return oct(self._bitstring)

    def __hex__(self):
        return hex(self._bitstring)


def bitwidth(num):
    """Return the number of bits required to represent num
    """
    count = 0
    while num:
        count += 1
        num = num >> 1
    return count


def mutable_named_bitfield(cname, fields):
    """Create a named bitfield for the given specification

    :param cname: Name of the generated class
    :param fields: An ordered list of pairs (field name, field width). Field
                   width should be a number of bits, and field name should be
                   a valid python identifier.
    :returns: A new type representing the bitfield structure described in the
              parameters

    """

    FieldSpec = namedtuple('FieldSpec', "offset mask width")
    field_mapping = OrderedDict()
    # build out masks & offsets
    offset = 0
    for fieldname, width in fields:
        mask = (2**(offset + width) - 1) - (2**offset - 1)
        field_mapping[fieldname] = FieldSpec(offset, mask, width)
        offset += width

    def mk_property(fieldname):
        """use a clousre to build out the getter & setter for the given field
        """
        def field_setter(self, value):
            """Validate and set the given field
            """
            if isinstance(value, basestring):
                raise TypeError("Cannot set integer field to a string")
            value = int(value)
            vals = []
            for fname, fspec in self._field_mapping.iteritems():
                if fname != fieldname:
                    vals.insert(0, getattr(self, fname))
                else:
                    vals.insert(0, value)
            # Rebuilding the whole string is a little kludgy, but it's good for
            # a proof of concept iteration
            self._build_from_vals(vals)

        def field_getter(self):
            """Return the value for the given field
            """
            field_spec = self._field_mapping[fieldname]
            return (self._bitstring & field_spec.mask) >> field_spec.offset

        return property(field_getter, field_setter)

    props = {fn: mk_property(fn) for fn, v in fields}
    props['_field_mapping'] = field_mapping
    return type(cname, (BaseNamedBitfield,), props)
