from flockwave.parsers.rpc import create_rpc_parser
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol

import pytest


def requests_equal(req1, req2):
    return req1._to_dict() == req2._to_dict()


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            [
                b'\x00\x45{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}'
            ],
            [[JSONRPCProtocol().create_request(method="subtract", args=[42, 23])]],
        ),
        (
            [b'\x00\x29{"jsonrpc": "2.0",', b'"result": 19, "id":', b" 1}"],
            [
                [],
                [],
                [
                    JSONRPCProtocol()
                    .create_request(method="subtract", args=[42, 23])
                    .respond(19)
                ],
            ],
        ),
    ],
)
def test_json_rpc_parsing(data, expected):
    parser = create_rpc_parser(protocol=JSONRPCProtocol())
    for part, exp in zip(data, expected):
        obs = parser(part)
        for req1, req2 in zip(exp, obs):
            assert requests_equal(req1, req2)
