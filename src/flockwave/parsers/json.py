"""JSON object parser."""

from json import JSONDecoder
from typing import Any, Callable, Literal
from warnings import warn

from .factories import create_parser
from .filters import reject_shorter_than
from .splitters import split_lines
from .types import Parser


def _adapt_builtin_decoder(decoder: JSONDecoder) -> Parser[Any]:
    def decode(data: bytes) -> Any:
        """Decodes a message using the provided JSON decoder."""
        return decoder.decode(data.decode("utf-8"))

    return decode


def _adapt_orjson_decoder() -> Parser[Any]:
    from orjson import loads

    return loads


def create_json_parser(
    decoder: Callable[[bytes], Any] | JSONDecoder | Literal["builtin"] | None = None,
    **kwds,
) -> Parser[Any]:
    """Creates a parser that parses incoming bytes as JSON objects.

    By default, this parser assumes that individual messages are separated by
    newline characters, and that no message contains a newline character on its
    own. If this is not suitable for you, you may specify an alternative
    splitter in the keyword arguments.

    All keyword arguments not explicitly mentioned here are forwarded to
    `create_parser()`.

    Args:
        decoder: the JSON parser to use
        splitter: the splitter to use to determine the boundaries between
            objects to be decoded.
        encoding: the encoding of the inbound messages to parse
    """
    if "encoding" in kwds:
        warn(
            "The 'encoding' keyword argument is deprecated and will be "
            "removed in a future version.",
            stacklevel=2,
        )

    encoding = kwds.pop("encoding", "utf-8")
    if encoding != "utf-8":
        raise ValueError("Only 'utf-8' encoding is supported for JSON decoding")

    if decoder is None:
        try:
            decoder = _adapt_orjson_decoder()
        except ImportError:
            decoder = "builtin"

    if decoder == "builtin":
        decoder = JSONDecoder()

    if isinstance(decoder, JSONDecoder):
        decoder = _adapt_builtin_decoder(decoder)

    if "splitter" in kwds:
        splitter = kwds.pop("splitter")
    else:
        splitter = split_lines()

    return create_parser(
        splitter=splitter,
        decoder=decoder,
        pre_filter=reject_shorter_than(1),
        **kwds,
    )
