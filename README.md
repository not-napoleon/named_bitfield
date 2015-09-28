# named_bitfield
Python tools for compact representations of fixed width numeric values


## Goals
named_bitfield lets you define fixed width bit fields within an integer, and
address those fields as class attributes, while still providing access to the
backing integer representation.  The original use case for this is
"intellignet IDs".  Essentially, this is a unique numeric id, sutiable for use
as a database primary key, which encodes some information about the object it
identifies.  Obviously, this should be immutable information so your IDs don't
change or (worse) get out of sync with reality.  Some suggestions are the
object type, the create time, or the data source.  Saving a few bits for a
serial counter is also advisable, as timestamps aren't reliable as unique ids.

Another application is an array of named flags, although a namedtuple probably
better serves that requirement unless there is some need for binary
communication of the data.
