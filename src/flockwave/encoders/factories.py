"""Base class and interface specification for message encoders in the
Flockwave application suite.
"""

from typing import Optional

from .mergers import merge_with_newlines, merge_using_length_prefix
from .types import Encoder, Merger, T

__all__ = ("create_encoder", "create_length_prefixed_encoder", "create_line_encoder")


def _identity(x: bytes) -> bytes:
    return x


def create_encoder(
    encoder: Encoder[T] = None, merger: Optional[Merger] = None
) -> Encoder[T]:
    """Creates an encoder function from an encoder and a merger function.

    The encoder function is responsible for turning a single message into its
    byte-level representation on the network. The merger function wraps the
    encoded messages in a way that makes it possible to separate the individual
    messages later on the receiving end unambiguously.

    Keyword arguments:
        encoder: function that will receive each individual message to encode
            and must receive its byte-level representation. Defaults to the
            identity function.
        merger: function that wraps the encoded messages in a way that makes it
            possible to separate the individual messages later on the receiving
            end unambiguously
    """
    encoder = encoder or _identity
    if merger:
        return lambda message: merger(encoder(message))
    else:
        return encoder


def create_length_prefixed_encoder(
    *,
    max_length: Optional[int] = None,
    header_length: Optional[int] = None,
    endianness: str = "big",
    **kwds,
) -> Encoder[T]:
    """Creates an encoder that prefixes each encoded message with its length
    on the wire.

    All keyword arguments not mentioned here are forwarded to
    ``create_encoder()``.

    Keyword arguments:
        max_length: maximum length of messages that we will write; it will also
            be used to decide how many bytes the protocol uses to encode the
            message lengths unless `header_length` is specified
        header_length: number of bytes that the protocol uses to encode
            message lengths; inferred from `max_length` if not present
        endianness: whether lengths are encoded in little endian or big endian
            (relevant only if lengths are encoded in more than one byte)

    Raises:
        EncodingError: when trying to send a message that is too long for the
            number of bytes allocated to convey the length of the message
    """
    return create_encoder(
        merger=merge_using_length_prefix(
            max_length=max_length, header_length=header_length, endianness=endianness
        ),
        **kwds,
    )


def create_line_encoder(**kwds) -> Encoder[T]:
    """Creates a parser that assumes that outgoing messages are separated by
    newline characters.

    Note that it is _not_ checked whether the messages being encoded contain
    newlines; it is assumed that the serialization method already takes care
    of ensuring this.

    All keyword arguments not mentioned here are forwarded to
    ``create_encoder()``.
    """
    return create_encoder(merger=merge_with_newlines(), **kwds)
