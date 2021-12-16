from typing import Callable, TypeVar


__all__ = ("Encoder", "Wrapper", "T")

T = TypeVar("T")

Encoder = Callable[[T], bytes]
"""Type specification for message encoder functions that take a message
and return its serialized variant that is suitable to be sent over the
network.

Parameters:
    message: the message to send

Returns:
    the raw byte representation of the message on the network

Raises:
    EncodingError: in case of unrecoverable encoding errors
"""

Wrapper = Callable[[bytes], bytes]
"""Type specification for message wrapper functions that take a serialized
version of a message and wraps it with the appropriate separator or header
bytes that ensure that individual messages can be separated on the wire
when they are parsed again.

Accepts:
    the raw bytes to feed into the wrapper

Returns:
    the raw bytes, prefixed or suffixed with the appropriate extra delimiter
    bytes

Raises:
    EncodingError: in case of unrecoverable encoding errors
"""
