"""
Create collections of named fixed width integers backed by python ints
or longs (as appropriate) and with clean interfaces to the fields.
"""

from collections import OrderedDict, namedtuple
from keyword import iskeyword

import six


class BaseNamedBitfield(object):
    """Baseclass for named bitfields.  Don't implement or instantiate this,
    instead call named_bitfield or immutable_named_bitfield as needed.
    """
    _field_mapping = {}

    def __init__(self, *args, **kwargs):
        """closuer to initilize the new class
        """
        self._bitstring = 0
        args = list(args)
        vals = []
        fieldnames = list(self._field_mapping.keys())
        # validate kwargs
        for key in kwargs:
            if key not in fieldnames:
                raise TypeError("%s got unexpected keyword argument %s"
                                % (self.__class__.__name__, key))
        while args:
            vals.append(args.pop(0))
            fieldnames.pop(0)
        while fieldnames:
            vals.append(kwargs.get(fieldnames.pop(0), 0))
        self._bitstring = self._build_from_vals(vals)

    def _build_from_vals(self, vals):
        """Construct a bitstring from a spec and a series of values
        """
        bitstring = 0
        for field_spec, value in zip(list(self._field_mapping.values()), vals):
            if bitwidth(value) > field_spec.width:
                raise ValueError("%d will not fit in %d bit wide field",
                                 value, field_spec.width)
            bitstring = bitstring << field_spec.width
            bitstring |= value
        return bitstring

    @classmethod
    def fromint(cls, num):
        """Create a new named_bitfield from the given integer

        :param num: The integer to build the instance from
        :returns: New class instance

        """
        # We can't validate each individual field, but we can make sure the
        # whole integer fits in the defined fields
        total_bits = sum([f.width for f in list(cls._field_mapping.values())])
        if bitwidth(num) > total_bits:
            raise ValueError("{0} will not fit in a {1}".format(num,
                                                                cls.__name__))
        result = cls()
        result._bitstring = num
        return result

    def __int__(self):
        return self._bitstring

    def __long__(self):
        return self._bitstring

    def __oct__(self):
        return oct(self._bitstring)

    def __hex__(self):
        return hex(self._bitstring)

    def __index__(self):
        return self._bitstring

    def __str__(self):
        return str(int(self))

    def __repr__(self):
        field_string = ",".join(["{0}={1}".format(fn, getattr(self, fn))
                                 for fn in list(self._field_mapping.keys())])
        return "{0}({1})".format(self.__class__.__name__, field_string)

    def __cmp__(self, other):
        return int(self) - int(other)

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __hash__(self):
        # This means different named_bitfields that happen to have the same
        # integer representation will hash to the same thing.  That matches the
        # definition of equality used above, but might not be the most sensible
        # thing to do.
        return hash(int(self))


def bitwidth(num):
    """Return the number of bits required to represent num
    """
    count = 0
    while num:
        count += 1
        num = num >> 1
    return count


def named_bitfield(cname, fields, mutable=False):
    """Create a named bitfield for the given specification

    :param cname: Name of the generated class
    :param fields: An ordered list of pairs (field name, field width). Field
                   width should be a number of bits, and field name should be
                   a valid python identifier.
    :returns: A new type representing the bitfield structure described in the
              parameters

    """
    # This is the same set of field checks namedtuple uses.  See code at
    # https://hg.python.org/cpython/file/2.7/Lib/collections.py#l334
    # (Available under the PSF license)
    for name in [cname] + [f[0] for f in fields]:
        if type(name) != str:
            raise TypeError('Type names and field names must be strings')
        if not all(c.isalnum() or c == '_' for c in name):
            raise ValueError('Type names and field names can only contain '
                             'alphanumeric characters and underscores: %r'
                             % name)
        if iskeyword(name):
            raise ValueError('Type names and field names cannot be a '
                             'keyword: %r' % name)
        if name[0].isdigit():
            raise ValueError('Type names and field names cannot start with '
                             'a number: %r' % name)
    seen = set()
    for name in [f[0] for f in fields]:
        if name.startswith('_'):
            raise ValueError('Field names cannot start with an underscore: '
                             '%r' % name)
        if name in seen:
            raise ValueError('Encountered duplicate field name: %r' % name)
        seen.add(name)

    FieldSpec = namedtuple('FieldSpec', "offset mask width")
    field_mapping = OrderedDict()
    # build out masks & offsets
    offset = 0
    for fieldname, width in reversed(fields):
        mask = (2**(offset + width) - 1) - (2**offset - 1)
        field_mapping[fieldname] = FieldSpec(offset, mask, width)
        offset += width

    field_mapping = OrderedDict(reversed(list(field_mapping.items())))

    def mk_property(fieldname):
        """use a clousre to build out the getter & setter for the given field
        """
        if mutable:
            def field_setter(self, value):
                """Validate and set the given field
                """
                if isinstance(value, six.string_types):
                    raise TypeError("Cannot set integer field to a string")
                value = int(value)
                vals = []
                for fname, fspec in self._field_mapping.items():
                    if fname != fieldname:
                        vals.append(getattr(self, fname))
                    else:
                        vals.append(value)
                # Rebuilding the whole string is a little kludgy, but it's
                # good for a proof of concept iteration
                self._bitstring = self._build_from_vals(vals)

        def field_getter(self):
            """Return the value for the given field
            """
            field_spec = self._field_mapping[fieldname]
            return (self._bitstring & field_spec.mask) >> field_spec.offset

        if mutable:
            return property(field_getter, field_setter)
        else:
            return property(field_getter)

    props = {fn: mk_property(fn) for fn, v in fields}
    props['_field_mapping'] = field_mapping
    # Explicitly mark the mutalbe version as unhashable
    if mutable:
        props['__hash__'] = None
    return type(cname, (BaseNamedBitfield,), props)
