"""
Create collections of named fixed width integers backed by python ints
or longs (as appropriate) and with clean interfaces to the fields.
"""


def mutable_named_bitfield(cname, fields):
    """Create a named bitfield for the given specification

    :param cname: Name of the generated class
    :param fields: An ordered list of pairs (field name, field width). Field
                   width should be a number of bits, and field name should be
                   a valid python identifier.
    :returns: A new type representing the bitfield structure described in the
              parameters

    """

    def mk_property(fieldname):
        """use a clousre to build out the getter & setter for the given field
        """
        def field_setter(self, value):
            """Validate and set the given field
            """
            if isinstance(value, basestring):
                raise TypeError("Cannot set integer field to a string")
            self._fields[fieldname] = int(value)

        def field_getter(self):
            """Return the value for the given field
            """
            return self._fields[fieldname]

        return property(field_getter, field_setter)

    props = {fn: mk_property(fn) for fn, v in fields}

    def initer(self, *args, **kwargs):
        """closuer to initilize the new class
        """
        args = list(args)
        fieldnames = [k for k, _ in fields]
        while len(args) < len(fieldnames):
            args.append(0)
        self._fields = {k: v for k, v in zip(fieldnames, args)}
        for key, value in kwargs.iteritems():
            if key not in self._fields:
                raise TypeError("%s got unexpected keyword argument %s"
                                % (cname, key))
            self._fields[key] = value

    props['__init__'] = initer
    return type(cname, (object,), props)
