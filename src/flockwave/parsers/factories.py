"""Base class and interface specification for message parsers in the
Flockwave application suite.
"""

from typing import Callable

from .filters import reject_shorter_than
from .splitters import dummy_splitter, split_lines, split_using_length_prefix
from .types import Filter, Parser, ParserGenerator, Splitter, T

__all__ = (
    "create_length_prefixed_parser",
    "create_line_parser",
    "create_parser",
    "create_parser_generator",
)


def create_parser_generator(
    *,
    splitter: Splitter | None = None,
    decoder: Callable[[bytes], T] | None = None,
    pre_filter: Filter[bytes] | None = None,
    post_filter: Filter[T] | None = None,
    filter: Filter[T] | None = None,
) -> ParserGenerator[T]:
    """Creates a parser generator from a splitter and a decoder function
    and several optional filters.

    Keyword arguments:
        splitter: generator that will receive each chunk that is fed into
            the parser, and that must yield raw bytes of the individual
            packets detected in the input stream. Defaults to the identity
            generator that simply yields whatever was sent to it.
        decoder: optional function to call on the raw bytes of each detected
            incoming message before it is given to the callback as
            the first argument. The return value of the function will be
            given to the callback instead of the incoming message.
        pre_filter: optional function to call on the raw bytes of each
            detected incoming message before it is given to the decoder. The
            function must return ``True`` or ``False``; if it returns
            ``False``, the message will be dropped.
        post_filter: optional function to call on each detected incoming
            message after it was passed through the decoder. The function
            must return ``True`` or ``False``; if it returns ``False``, the
            message will be dropped. `filter` is an alias to this keyword
            argument.
        filter: alias to ``post_filter``.
    """
    if filter and post_filter:
        raise ValueError("filter=... and post_filter=... are mutually exclusive")

    post_filter = post_filter or filter

    if splitter is None:
        splitter = dummy_splitter()

    # Syntactic sugar: allow the user to pass in a function that returns
    # a generator when called with no arguments
    if callable(splitter):
        splitter = splitter()

    assert splitter is not None

    next(splitter)  # prime the generator
    data = yield ()

    while True:
        messages = []

        for chunk in splitter.send(data):
            if pre_filter and not pre_filter(chunk):
                continue

            message = decoder(chunk) if decoder else chunk

            if post_filter and not post_filter(message):
                continue

            messages.append(message)

        data = yield messages


def create_parser(gen: ParserGenerator[T] | None = None, **kwds) -> Parser[T]:
    """Creates a parser from a parser generator.

    You can either supply a parser generator directly as the first positional
    argument, or you can supply a set of keyword arguments that are passed
    directly to `create_parser_generator()`; in the latter case, the result
    of the `create_parser_generator()` call will be converted into a parser
    function.

    See the docstring of `create_parser_generator()` for the list of allowed
    keyword arguments.
    """
    if gen is None:
        gen = create_parser_generator(**kwds)  # type: ignore
    elif kwds:
        raise ValueError(
            "no keyword arguments should be specified if you supply a generator directly"
        )

    assert gen is not None

    next(gen)
    return gen.send


def create_length_prefixed_parser(
    *,
    min_length: int | None = None,
    max_length: int | None = None,
    header_length: int | None = None,
    endianness: str = "big",
    **kwds,
) -> Parser[T]:
    """Creates a parser that assumes that incoming messages are prefixed by
    their length in bytes.

    All keyword arguments not mentioned here are forwarded to
    ``create_parser()``.

    Keyword arguments:
        min_length: minimum length of messages that we are interested in
        max_length: maximum length of messages that we are interested in; it
            will also be used to decide how many bytes the protocol uses to
            encode the message lengths unless `header_length` is specified
        header_length: number of bytes that the protocol uses to encode
            message lengths; inferred from `max_length` if not present
        endianness: whether lengths are encoded in little endian or big endian
            (relevant only if lengths are encoded in more than one byte)
    """
    if min_length is not None:
        kwds["pre_filter"] = reject_shorter_than(min_length)

    return create_parser(
        splitter=split_using_length_prefix(
            max_length=max_length, header_length=header_length, endianness=endianness
        ),
        **kwds,
    )


def create_line_parser(*, min_length: int | None = None, **kwds) -> Parser[T]:
    """Creates a parser that assumes that incoming messages are separated by
    newline characters.

    All keyword arguments not mentioned here are forwarded to
    ``create_parser()``.

    Keyword arguments:
        min_length: minimum length of messages that we are interested in
    """
    if min_length is not None:
        kwds["pre_filter"] = reject_shorter_than(min_length)

    return create_parser(splitter=split_lines, **kwds)
