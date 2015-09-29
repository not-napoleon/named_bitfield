# named_bitfield
Python tools for compact representations of fixed width numeric values


## Goals
named_bitfield lets you define fixed width bit fields within an integer, and
address those fields as class attributes, while still providing access to the
backing integer representation.  The original use case for this is
"intelligent IDs".  Essentially, this is a unique numeric id, suitable for use
as a database primary key, which encodes some information about the object it
identifies.  Obviously, this should be immutable information so your IDs don't
change or (worse) get out of sync with reality.  Some suggestions are the
object type, the create time, or the data source.  Saving a few bits for a
serial counter is also advisable, as timestamps aren't reliable as unique ids.

Another application is an array of named flags, although a namedtuple probably
better serves that requirement unless there is some need for binary
communication of the data.


## Example Usage
Suppose you work on an analytics system for a shopping site.  You track
several different event counts per day, broken out by both user and product
counts (e.g. this user made this many clicks, and this product was clicked on
this many times).  You could set up a named_bitfield ID to encode this data:

    >>> from named_bitfield import named_bitfield
    >>> CounterID = named_bitfield('CounterID', [('day', 20), ('domain', 2), ('event', 10)])
    >>> domains = {'user': 0, 'product': 1}
    >>> events = {'search_click': 51, 'related_click': 52} # etc

And build an ID like so:

    >>> from datetime import date
    >>> event_id = CounterID(date.today().toordinal(), domains['user'], events['search_click'])
    >>> event_id
    CounterID(day=735870,domain=0,event=51)
    >>> int(event_id)
    3014123571

The 32 bit integer id could be used as a database primary key.  Later, getting
an ID out of the database, you can use it to build a new instance and address
the sub-fields directly:

    >>> # Some data model operation
    3013866547
    >>> fromdb = CounterID.fromint(3013866547)
    >>> date.fromordinal(fromdb.day)
    datetime.date(2015, 7, 28)
    >>>


## Realted Work
If this doesn't do what you need, maybe one of these packages does:

https://github.com/ilanschnell/bitarray
https://github.com/scott-griffiths/bitstring
https://github.com/stestagg/bitfield
https://github.com/xflr6/bitsets

