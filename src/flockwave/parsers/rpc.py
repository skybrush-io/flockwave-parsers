"""RPC protocol parser."""

try:
    from tinyrpc import InvalidRequestError
    from tinyrpc.protocols import RPCProtocol, RPCRequest, RPCResponse
except ImportError:
    raise ImportError("install 'tinyrpc' to use RPC-related parsers")

from functools import partial
from typing import Optional, Union

from .factories import create_parser
from .splitters import split_using_length_prefix
from .types import Parser, Splitter


RPCMessage = Union[RPCRequest, RPCResponse]


def _parse_rpc_message(protocol: RPCProtocol, data: bytes) -> RPCMessage:
    try:
        return protocol.parse_request(data)
    except InvalidRequestError as ex:
        try:
            return protocol.parse_reply(data)
        except Exception:
            raise ex


def create_rpc_parser(
    *, protocol: RPCProtocol, splitter: Optional[Splitter] = None, **kwds
) -> Parser[RPCMessage]:
    """Creates a parser that parses incoming bytes as RPC requests and responses
    according to some RPC protocol.

    By default, this parser assumes that individual messages are prefixed by
    their lengths in bytes. If this is not suitable for you, you may
    specify an alternative splitter in the keyword arguments.

    All keyword arguments not explicitly mentioned here are forwarded to
    `create_parser()`.

    Keyword arguments:
        protocol: the RPC protocol to parse
        splitter: the splitter to use to determine the boundaries between
            RPC messages.
    """
    if splitter is None:
        splitter = split_using_length_prefix(header_length=2)

    decoder = partial(_parse_rpc_message, protocol)

    return create_parser(splitter=splitter, decoder=decoder, **kwds)
