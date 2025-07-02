"""JSON object encoder."""

from datetime import datetime
from enum import Enum
from functools import partial
from json import JSONEncoder
from typing import Any, Literal
from warnings import warn

from .factories import create_encoder
from .types import Encoder, Wrapper
from .wrappers import append_separator

__all__ = ("create_json_encoder", "object_to_jsonable")


def object_to_jsonable(obj: Any) -> Any:
    """Converts an object to a JSON-serializable form.

    This function is used as a default `default` function for the
    `json.JSONEncoder` class. It converts objects to a JSON-serializable form
    according to the following rules:

    - If the object is a `datetime`, it is converted to an ISO 8601
      formatted string.

    - If the object is an `Enum`, it is converted to its name.

    - If the object has a `json` property, it is used as the JSON-serializable
      representation of the object.

    - If none of the above applies, a `TypeError` is raised.
    """
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


def _adapt_builtin_encoder(encoder: JSONEncoder) -> Encoder[Any]:
    def encode(message: Any) -> bytes:
        """Encodes a message using the provided JSON encoder."""
        return encoder.encode(message).encode("utf-8")

    return encode


def _adapt_orjson_encoder(
    option: int | None = None,
) -> Encoder[Any]:
    from orjson import dumps, OPT_SORT_KEYS

    if option is None:
        option = OPT_SORT_KEYS
    return partial(dumps, default=object_to_jsonable, option=option)


def create_json_encoder(
    encoder: Encoder[Any] | JSONEncoder | Literal["builtin"] | None = None,
    *,
    wrapper: Wrapper | None = None,
    **kwds,
) -> Encoder[Any]:
    """Creates an encoder that encodes outgoing JSON messages using the built-in
    `json` module or using a custom encoder function.

    By default, this encoder assumes that individual messages should be separated
    by newlines and that no message contains a newline character in its encoded
    form. If this is not suitable for you, you may specify an alternative wrapper
    in the keyword arguments.

    All keyword arguments not explicitly mentioned here are forwarded to
    `create_encoder()`.

    Args:
        encoder: the JSON encoder object that the function will work with.
            This can be a `JSONEncoder` instance from the `json` module of the
            Python standard library, or a callable that takes the object to
            encode and returns a `bytes` object. The latter is useful if you
            want to integrate a high-performance JSON library such as `orjson`.
            If not specified, the function attempts to create the most efficient
            implementation based on `orjson` if it is installed, falling back to
            a default `JSONEncoder` instance from the built-in `json` module.
            It also ensures that no newline characters are used in any of the
            encoded messages.
        wrapper: the wrapper to use to augment the encoded messages to help the
            parser separate the individual messages
    """
    if "encoding" in kwds:
        warn(
            "The 'encoding' keyword argument is deprecated and will be "
            "removed in a future version.",
            stacklevel=2,
        )

    encoding = kwds.pop("encoding", "utf-8")
    if encoding != "utf-8":
        raise ValueError("Only 'utf-8' encoding is supported for JSON encoding")

    if encoder is None:
        try:
            encoder = _adapt_orjson_encoder()
        except ImportError:
            encoder = "builtin"

    if encoder == "builtin":
        encoder = JSONEncoder(
            separators=(",", ":"),
            sort_keys=False,
            indent=None,
            default=object_to_jsonable,
        )

    if isinstance(encoder, JSONEncoder):
        encoder = _adapt_builtin_encoder(encoder)

    if wrapper is None:
        wrapper = append_separator(b"\n")

    return create_encoder(
        wrapper=wrapper,
        encoder=encoder,
        **kwds,
    )
