"""
Tests for named bitfields
"""

from nose.tools import ok_, eq_, assert_raises, raises


from named_bitfield.named_bitfield import mutable_named_bitfield


def test_has_attributes():
    """Instances of the named_bitfield have attributes matching the field names
    """
    nbf = mutable_named_bitfield('TestBitfield',
                                 [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf()
    ok_(hasattr(test1, 'a'))
    ok_(hasattr(test1, 'b'))
    ok_(hasattr(test1, 'c'))
    ok_(not hasattr(test1, 'bogus'))


def test_set_attributes():
    """Can set the attributes of a named_bitfield
    """
    nbf = mutable_named_bitfield('TestBitfield',
                                 [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf()
    test1.a = 3
    test1.b = 7
    test1.c = 1
    eq_(test1.a, 3)
    eq_(test1.b, 7)
    eq_(test1.c, 1)


def test_instance_attributes():
    """named_bitfield attributes are instance, not class, attributes
    """
    nbf = mutable_named_bitfield('TestBitfield',
                                 [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf()
    test2 = nbf()
    test1.a = 3
    test1.b = 7
    test1.c = 1

    test2.a = 0
    test2.b = 0
    test2.c = 0

    eq_(test1.a, 3)
    eq_(test1.b, 7)
    eq_(test1.c, 1)

    eq_(test2.a, 0)
    eq_(test2.b, 0)
    eq_(test2.c, 0)


def test_invalid_types():
    """named_bitfield fields must be integer values
    """
    nbf = mutable_named_bitfield('TestBitfield',
                                 [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf()

    def check_setter(obj, val):
        "Try to set a value, so we can trap the exception"
        obj.a = val

    assert_raises(TypeError, check_setter, test1, [1, 2, 3])
    assert_raises(TypeError, check_setter, test1, (1, 2, 3))
    assert_raises(TypeError, check_setter, test1, 'bogus')


def test_overrun():
    """Overrunning a field doesn't corrupt the adjecent fields
    """
    nbf = mutable_named_bitfield('TestBitfield',
                                 [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf()
    test1.a = 2
    test1.b = 7
    test1.c = 3

    try:
        test1.b = 2**6 - 1
    except Exception:
        # Other tests make sure this raises the right error; here we just want
        # to check for side effects
        pass

    eq_(test1.a, 2)
    # b is in an undefined state, no sane test for its value
    eq_(test1.c, 3)


def test_positional_init():
    """Can initilize field values by position
    """
    nbf = mutable_named_bitfield('TestBitfield',
                                 [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf(3, 7, 3)
    eq_(test1.a, 3)
    eq_(test1.b, 7)
    eq_(test1.c, 3)


def test_kwargs_init():
    """Can initilize field values by keyword arg
    """
    nbf = mutable_named_bitfield('TestBitfield',
                                 [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf(c=2, a=3, b=7)
    eq_(test1.a, 3)
    eq_(test1.b, 7)
    eq_(test1.c, 2)


@raises(TypeError)
def test_unknown_kwarg():
    """Unknown field names in kwargs raises type error
    """
    nbf = mutable_named_bitfield('TestBitfield',
                                 [('a', 2), ('b', 4), ('c', 2)])
    nbf(c=2, a=3, b=7, x=4)


def test_mixed_init():
    """Can initilize field values by keyword arg
    """
    nbf = mutable_named_bitfield('TestBitfield',
                                 [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf(3, c=2, b=7)
    eq_(test1.a, 3)
    eq_(test1.b, 7)
    eq_(test1.c, 2)
