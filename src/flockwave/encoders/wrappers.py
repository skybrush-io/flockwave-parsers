"""Wrapper factory functions to be used as building blocks for encoders."""

__all__ = ("append_separator", "prefix_with_length")

from functools import lru_cache
from struct import Struct

from ..parsers.splitters import _propose_header_length, _validate_endianness

from .errors import EncodingError
from .types import Wrapper


@lru_cache(maxsize=None)
def append_separator(separator: bytes) -> Wrapper:
    def wrapper(data: bytes) -> bytes:
        return data + separator

    return wrapper


def prefix_with_length(
    *,
    max_length: int | None = None,
    header_length: int | None = None,
    endianness: str = "big",
) -> Wrapper:
    header_length = header_length or _propose_header_length(max_length)
    if max_length is None:
        max_length = (2 ** (8 * header_length)) - 1

    assert max_length is not None

    _validate_endianness(endianness)

    if header_length == 1:
        length_struct = Struct("B")
    elif header_length == 2:
        length_struct = Struct(">H") if endianness == "big" else Struct("<H")
    elif header_length == 4:
        length_struct = Struct(">I") if endianness == "big" else Struct("<I")
    else:
        length_struct = None

    def wrapper(data: bytes) -> bytes:
        length = len(data)
        if length > max_length:
            raise EncodingError(
                f"packet length exceeds limit ({length} > {max_length})"
            )

        if length_struct:
            return length_struct.pack(length) + data
        else:
            header = [0] * header_length
            i = 0
            while length > 0:
                header[i] = length & 0xFF
                length >>= 8
                i += 1
            if endianness == "big":
                header.reverse()
            return bytes(header) + data

    return wrapper
