"""JSON object encoder."""

from datetime import datetime
from enum import Enum
from functools import partial
from json import JSONEncoder
from typing import Any, Optional

from .factories import create_encoder
from .types import Encoder, Wrapper
from .wrappers import append_separator


def _encode_json_message(encoder: JSONEncoder, encoding: str, message: Any) -> bytes:
    return encoder.encode(message).encode(encoding)


def _encode_object_to_json(obj: Any) -> Any:
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Enum):
        return obj.name
    else:
        # Do not use hasattr(obj, "json") here because that will simply
        # try to retrieve the attribute and then throw away the result,
        # so we are doing extra work by using it
        try:
            return obj.json
        except AttributeError:
            raise TypeError(f"cannot encode {obj!r} into JSON") from None


def create_json_encoder(
    encoder: Optional[JSONEncoder] = None,
    *,
    wrapper: Optional[Wrapper] = None,
    encoding: str = "utf-8",
    **kwds,
) -> Encoder[Any]:
    """Creates an encoder that encodes outgoing RPC messages according to some
    RPC protocol.

    By default, this encoder assumes that individual messages should be separated
    by newlines and that no message contains a newline character in its encoded
    form. If this is not suitable for you, you may specify an alternative wrapper
    in the keyword arguments.

    All keyword arguments not explicitly mentioned here are forwarded to
    `create_encoder()`.

    Positional arguments:
        encoder: the JSON encoder object that the function will work with.
            Defaults to a compact JSON representation that ensures that no
            newline characters are used in any of the encoded messages.

    Keyword arguments:
        wrapper: the wrapper to use to augment the encoded messages to help the
            parser separate the individual messages
    """
    if encoder is None:
        encoder = JSONEncoder(
            separators=(",", ":"),
            sort_keys=False,
            indent=None,
            default=_encode_object_to_json,
        )

    if wrapper is None:
        wrapper = append_separator(b"\n")

    return create_encoder(
        wrapper=wrapper,
        encoder=partial(_encode_json_message, encoder, encoding),
        **kwds,
    )
