"""RPC protocol encoder."""

from .factories import create_encoder
from .wrappers import prefix_with_length
from .types import Encoder, Wrapper

from typing import Union

try:
    from tinyrpc.protocols import RPCProtocol, RPCRequest, RPCResponse
except ImportError:
    raise ImportError("install 'tinyrpc' to use RPC-related encoders") from None


RPCMessage = Union[RPCRequest, RPCResponse]


def _encode_rpc_message(message: RPCMessage) -> bytes:
    return message.serialize()


def create_rpc_encoder(
    *, protocol: RPCProtocol, wrapper: Wrapper | None = None, **kwds
) -> Encoder[RPCMessage]:
    """Creates an encoder that encodes outgoing RPC messages according to some
    RPC protocol.

    By default, this encoder assumes that individual messages should be prefixed
    by their lengths in bytes. If this is not suitable for you, you may
    specify an alternative wrapper in the keyword arguments.

    All keyword arguments not explicitly mentioned here are forwarded to
    `create_encoder()`.

    Keyword arguments:
        protocol: the RPC protocol to encode
        wrapper: the wrapper to use to augment the encoded messages to help the
            parser separate the individual messages
    """
    if wrapper is None:
        wrapper = prefix_with_length(header_length=2)

    return create_encoder(wrapper=wrapper, encoder=_encode_rpc_message, **kwds)
