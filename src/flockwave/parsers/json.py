"""JSON object parser."""

from functools import partial
from json import JSONDecoder
from typing import Any, Optional

from .factories import create_parser
from .filters import reject_shorter_than
from .splitters import split_lines
from .types import Parser


def _decode_json_message(decoder: JSONDecoder, encoding: str, data: bytes) -> Any:
    return decoder.decode(data.decode(encoding))


def create_json_parser(
    decoder: Optional[JSONDecoder] = None, *, encoding: str = "utf-8", **kwds
) -> Parser[Any]:
    """Creates a parser that parses incoming bytes as JSON objects.

    By default, this parser assumes that individual messages are separated by
    newline characters, and that no message contains a newline character on its
    own. If this is not suitable for you, you may specify an alternative
    splitter in the keyword arguments.

    All keyword arguments not explicitly mentioned here are forwarded to
    `create_parser()`.

    Positional arguments:
        decoder: the JSON parser to use

    Keyword arguments:
        splitter: the splitter to use to determine the boundaries between
            objects to be decoded.
        encoding: the encoding of the inbound messages to parse
    """
    if decoder is None:
        decoder = JSONDecoder()

    if "splitter" in kwds:
        splitter = kwds.pop("splitter")
    else:
        splitter = split_lines()

    return create_parser(
        splitter=splitter,
        decoder=partial(_decode_json_message, decoder, encoding),
        pre_filter=reject_shorter_than(1),
        **kwds,
    )
