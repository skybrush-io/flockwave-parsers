"""Merger factory functions to be used as building blocks for encoders."""

__all__ = ("merge_with_newlines", "merge_using_length_prefix")

from struct import Struct
from typing import Optional

from ..parsers.splitters import _propose_header_length, _validate_endianness

from .errors import EncodingError
from .types import Merger


def _merge_with_newlines(data: bytes) -> bytes:
    return data + b"\n"


def merge_with_newlines() -> Merger:
    return _merge_with_newlines


def merge_using_length_prefix(
    *,
    max_length: Optional[int] = None,
    header_length: Optional[int] = None,
    endianness: str = "big",
) -> Merger:
    header_length = header_length or _propose_header_length(max_length)
    if max_length is None:
        max_length = (2 ** (8 * header_length)) - 1

    _validate_endianness(endianness)

    if header_length == 1:
        length_struct = Struct("B")
    elif header_length == 2:
        length_struct = Struct(">H") if endianness == "big" else Struct("<H")
    elif header_length == 4:
        length_struct = Struct(">I") if endianness == "big" else Struct("<I")
    else:
        length_struct = None

    def merger(data: bytes) -> bytes:
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

    return merger
