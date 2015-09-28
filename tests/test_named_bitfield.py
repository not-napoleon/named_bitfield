"""
Tests for named bitfields
"""
import collections

import six

from nose.tools import ok_, eq_, assert_raises, raises


from named_bitfield import named_bitfield


###
# Tests making sure I used type correctly
def test_has_attributes():
    """Instances of the named_bitfield have attributes matching the field names
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf()
    ok_(hasattr(test1, 'a'))
    ok_(hasattr(test1, 'b'))
    ok_(hasattr(test1, 'c'))
    ok_(not hasattr(test1, 'bogus'))


def test_instance_attributes():
    """named_bitfield attributes are instance, not class, attributes
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf(3, 7, 1)
    test2 = nbf(0, 0, 0)

    eq_(test1.a, 3)
    eq_(test1.b, 7)
    eq_(test1.c, 1)

    eq_(test2.a, 0)
    eq_(test2.b, 0)
    eq_(test2.c, 0)


###
# Init tests
def test_positional_init():
    """Can initilize field values by position
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf(3, 7, 3)
    eq_(test1.a, 3)
    eq_(test1.b, 7)
    eq_(test1.c, 3)


def test_kwargs_init():
    """Can initilize field values by keyword arg
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf(c=2, a=3, b=7)
    eq_(test1.a, 3)
    eq_(test1.b, 7)
    eq_(test1.c, 2)


@raises(TypeError)
def test_unknown_kwarg():
    """Unknown field names in kwargs raises type error
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    nbf(c=2, a=3, b=7, x=4)


def test_mixed_init():
    """Can initilize field values by keyword arg
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf(3, c=2, b=7)
    eq_(test1.a, 3)
    eq_(test1.b, 7)
    eq_(test1.c, 2)


@raises(ValueError)
def test_init_too_big():
    """Initilizing a field to a value that doesn't fit raises
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    nbf(1024, 1024, 1024)


def test_from_int():
    """Can create a named_bitfield from an integer
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf.fromint(85)
    eq_(test1.a, 1)
    eq_(test1.b, 5)
    eq_(test1.c, 1)


@raises(ValueError)
def test_from_int_validation():
    """Passing fromint a value with more bits than defined in the spec raises
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    nbf.fromint(1024)


####
# Setter tests
def test_set_attributes():
    """Can set the attributes of a named_bitfield
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)],
                         mutable=True)
    test1 = nbf()
    test1.a = 3
    test1.b = 7
    test1.c = 1
    eq_(test1.a, 3)
    eq_(test1.b, 7)
    eq_(test1.c, 1)


def test_invalid_types():
    """named_bitfield fields must be integer values
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)],
                         mutable=True)
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
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)],
                         mutable=True)
    test1 = nbf()
    test1.a = 0
    test1.b = 7
    test1.c = 0

    try:
        test1.b = 2**6 - 1
    except ValueError:
        # Other tests make sure this raises the right error; here we just want
        # to check for side effects
        pass

    eq_(test1.a, 0)
    # b is in an undefined state, no sane test for its value
    eq_(test1.c, 0)


@raises(AttributeError)
def test_immutable_no_setter():
    """Trying to use a field of an immutable bitfield as an lvalue raises
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)],
                         mutable=False)
    test1 = nbf(3, 7, 1)
    test1.a = 0


@raises(ValueError)
def test_set_too_big():
    """Setting a field to a value that doesn't fit in those bits raises
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)],
                         mutable=True)
    test1 = nbf()
    test1.b = 2**6 - 1


###
# Magic Method Tests
def test_to_int():
    """Can cast the named_bitfield to an int correctly
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf(2, 5, 2)
    eq_(int(test1), 150)


def test_to_long():
    """Can cast the named_bitfield to a long correctly
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf(2, 5, 2)
    eq_(int(test1), 150)


def test_to_oct():
    """Correctly show octal representation when asked
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf(2, 5, 2)
    expected = '0226'
    if six.PY3:
        expected = '0o226'
    eq_(oct(test1), expected)


def test_to_hex():
    """Correctly show hex representation when asked
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf(2, 5, 2)
    eq_(hex(test1), '0x96')


def test_equality_same_type():
    """Equality works as expected within a named_bitfield type
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf(2, 5, 2)
    test2 = nbf(2, 5, 2)
    eq_(test1, test2)


def test_lt_same_type():
    """Less than works within a named_bitfield type
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf(2, 5, 2)
    test2 = nbf(0, 0, 0)
    ok_(test2 < test1)


def test_gt_same_type():
    """Greater than works within a named_bitfield type
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)])
    test1 = nbf(2, 5, 2)
    test2 = nbf(0, 0, 0)
    ok_(test1 > test2)


###
# Hash behavior tests
@raises(TypeError)
def test_unhashable_mutables_1():
    """Attempting to hash a mutable bitfield raises
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)],
                         mutable=True)
    test1 = nbf(2, 5, 2)
    hash(test1)


def test_unhashable_mutables_2():
    """Mutable bitfields are not instances of collections.Hashable
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)],
                         mutable=True)
    test1 = nbf(2, 5, 2)
    ok_(not isinstance(test1, collections.Hashable))


def test_immutable_hashes_as_int():
    """Hash of a mutable bitfield is the hash of the int
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)],
                         mutable=False)
    test1 = nbf(2, 5, 2)
    eq_(hash(test1), hash(int(test1)))


def test_immutable_is_hashable():
    """Immutable bitfields are instances of collections.Hashable
    """
    nbf = named_bitfield('TestBitfield', [('a', 2), ('b', 4), ('c', 2)],
                         mutable=False)
    test1 = nbf(2, 5, 2)
    ok_(isinstance(test1, collections.Hashable))
