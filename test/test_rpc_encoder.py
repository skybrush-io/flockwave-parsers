from flockwave.encoders.rpc import create_rpc_encoder
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol

import pytest


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        (
            JSONRPCProtocol().create_request(method="subtract", args=[42, 23]),
            b'\x00\x45{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}',
        ),
        (
            JSONRPCProtocol()
            .create_request(method="subtract", args=[42, 23])
            .respond(19),
            b'\x00\x29{"jsonrpc": "2.0", "id": 1, "result": 19}',
        ),
    ],
)
def test_json_rpc_encoding(message, expected):
    encoder = create_rpc_encoder(protocol=JSONRPCProtocol())
    observed = encoder(message)
    assert expected == observed
