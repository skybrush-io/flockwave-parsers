"""RPC protocol encoder."""

from .factories import create_encoder
from .mergers import merge_using_length_prefix
from .types import Encoder, Merger

from typing import Optional, Union

try:
    from tinyrpc.protocols import RPCProtocol, RPCRequest, RPCResponse
except ImportError:
    raise ImportError("install 'tinyrpc' to use RPC-related encoders")


RPCMessage = Union[RPCRequest, RPCResponse]


def _encode_rpc_message(message: RPCMessage) -> bytes:
    return message.serialize()


def create_rpc_encoder(
    *, protocol: RPCProtocol, merger: Optional[Merger] = None, **kwds
) -> Encoder[RPCMessage]:
    """Creates an encoder that encodes outgoing RPC messages according to some
    RPC protocol.

    By default, this encoder assumes that individual messages should be prefixed
    by their lengths in bytes. If this is not suitable for you, you may
    specify an alternative merger in the keyword arguments.

    All keyword arguments not explicitly mentioned here are forwarded to
    `create_encoder()`.

    Keyword arguments:
        protocol: the RPC protocol to encode
        merger: the merger to use to augment the encoded messages to help the
            parser separate the individual messages
    """
    if merger is None:
        merger = merge_using_length_prefix(header_length=2)

    return create_encoder(merger=merger, encoder=_encode_rpc_message, **kwds)
