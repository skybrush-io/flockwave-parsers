"""Splitter generators to be used as building blocks for parsers."""

from functools import partial
from math import ceil, log

from .errors import ParseError
from .types import Splitter


def dummy_splitter() -> Splitter:
    """Dummy splitter that does nothing (i.e. it assumes that each incoming
    chunk is a message on its own).

    Returns:
        a generator that can be used with `create_parser()`
    """
    chunk = []
    while True:
        data = yield chunk
        chunk = [data]


def split_around_delimiters(delimiters: bytes) -> Splitter:
    """Generator function that takes a set of delimiters, and returns a generator
    that splits incoming messages around the given delimiters, assuming that no
    message contains any of the delimiter characters.

    Parameters:
        delimiters: the delimiter bytes between messages; any non-empty sequence
            consisting solely of these bytes is considered a delimiter between
            messages

    Returns:
        a generator that can be used with `create_parser()`
    """
    separator = bytes([delimiters[0]])
    trans = bytes.maketrans(delimiters, separator * len(delimiters))

    chunks = []
    batch = []

    data = yield ()
    data = data.translate(trans)

    while True:
        while True:
            head, mid, data = data.partition(separator)
            chunks.append(head)
            if mid:
                batch.append(b"".join(chunks))
                del chunks[:]
            else:
                break

        data = yield batch
        del batch[:]
        data = data.translate(trans)


def split_lines() -> Splitter:
    """Generator function that returns a generator that splits incoming
    messages around newline characters (``\r`` and ``\n``).

    Returns:
        a generator that can be used with `create_parser()`
    """
    yield from split_around_delimiters(b"\r\n")


def _propose_header_length(max_length: int | None) -> int:
    """Proposes how many bytes the parser should need to represent the
    length of the packets when using a length-prefixed splitter.

    When the parser has an upper limit on the packet length, this function
    returns the appropriate number of bytes to represent the packet length.
    Otherwise, the function throws an error.
    """
    if max_length is not None:
        if max_length <= 0:
            raise ValueError("maximum packet length must be positive")
        return int(ceil(log(max_length + 1, 2) / 8))
    else:
        raise ValueError(
            "at least one of the maximum packet length and the prefix "
            "length must be specified"
        )


def _validate_endianness(endianness: str) -> None:
    if endianness not in ("big", "little"):
        raise ValueError(f"unknown endianness: {endianness}")


def _get_body_length_from_header(header: bytes, endianness: str) -> int:
    """Given a fully retrieved packet header, returns how many bytes we
    should read to retrieve the full body packet.
    """
    if len(header) == 1:
        return header[0]
    elif len(header) == 2:
        if endianness == "big":
            return (header[0] << 8) + header[1]
        else:
            return (header[1] << 8) + header[0]
    else:
        it = reversed(header) if endianness == "big" else iter(header)
        result = 0
        for byte in it:
            result = (result << 8) + byte
        return result


def split_using_length_prefix(
    max_length: int | None = None,
    header_length: int | None = None,
    endianness: str = "big",
):
    _validate_endianness(endianness)

    header_length = header_length or _propose_header_length(max_length)
    get_body_length = partial(_get_body_length_from_header, endianness=endianness)

    chunks = []
    state = "header"
    remaining_bytes = header_length

    while True:
        result = []
        data = yield

        while True:
            chunks.append(data)
            remaining_bytes -= len(data)

            remaining = remaining_bytes
            if remaining <= 0:
                data = b"".join(chunks)
                if remaining < 0:
                    data, rest = data[:remaining], data[remaining:]
                else:
                    rest = b""

                chunks[:] = []

                if state == "header":
                    remaining_bytes = get_body_length(data)
                    if max_length is not None and remaining_bytes > max_length:
                        raise ParseError(
                            f"packet length exceeds limit "
                            f"({remaining_bytes} > {max_length})"
                        )
                    state = "body"
                else:
                    if max_length is None or len(data) <= max_length:
                        result.append(data)

                    remaining_bytes = header_length
                    state = "header"

                data = rest

            else:
                data = yield result
                del result[:]

        return result
