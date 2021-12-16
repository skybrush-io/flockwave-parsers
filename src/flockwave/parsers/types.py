from typing import Callable, Generator, Iterable, TypeVar


__all__ = ("Parser", "ParserGenerator", "Splitter", "T")

T = TypeVar("T")

Parser = Callable[[bytes], Iterable[T]]
"""Type specification for message parser functions that can be fed with
incoming data and that return the parsed messages.

Parameters:
    data: the raw bytes to feed into the parser

Returns:
    iterables of parsed messages from the current chunk (and from any
    unprocessed data in previous chunks)

Raises:
    ParseError: in case of unrecoverable parse errors
"""

ParserGenerator = Generator[Iterable[T], bytes, None]
"""Type specification for message parser generators that can be fed with
incoming data and that yield the parsed messages.

Accepts:
    the raw bytes to feed into the parser

Yields:
    iterables of parsed messages from the current chunk (and from any
    unprocessed data in previous chunks)

Raises:
    ParseError: in case of unrecoverable parse errors
"""

Splitter = ParserGenerator[bytes]
"""Type specification for message splitter generators that can be fed with
incoming data and that yield the individual, raw (not parsed) messages.

Accepts:
    the raw bytes to feed into the parser

Yields:
    iterables of individual messages from the current chunk (and from
    any unprocessed data in previous chunks)

Raises:
    ParseError: in case of unrecoverable parse errors
"""

Filter = Callable[[T], bool]
"""Type specification for filter functions (both pre-filter and post-filter).

Pre-filters accept raw messages and return whether the message should be
processed further.

Post-filters accept parsed (converted) messages and return whether they should
be yielded back to the caller of the parser.
"""
