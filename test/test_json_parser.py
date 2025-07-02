from flockwave.parsers.json import create_json_parser

import pytest


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ([b""], []),
        ([b"[123", b', false, "fo', b'obar"]\n'], [[123, False, "foobar"]]),
        ([b"", b'{"a":', b' "q"}', b"\n"], [{"a": "q"}]),
        ([b"[123]\n\n\n", b"\n\n"], [[123]]),
    ],
)
def test_json_parser_orjson(data, expected):
    import orjson  # to ensure that orjson is available

    assert orjson is not None, "orjson should be installed in the test environment"

    parser = create_json_parser()

    result = []
    for part in data:
        result.extend(parser(part))

    assert expected == result


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ([b""], []),
        ([b"[123", b', false, "fo', b'obar"]\n'], [[123, False, "foobar"]]),
        ([b"", b'{"a":', b' "q"}', b"\n"], [{"a": "q"}]),
        ([b"[123]\n\n\n", b"\n\n"], [[123]]),
    ],
)
def test_json_parser_builtin(data, expected):
    parser = create_json_parser("builtin")

    result = []
    for part in data:
        result.extend(parser(part))

    assert expected == result


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ([b""], []),
        ([b"[123", b', False, "fo', b'obar"]\n'], [[123, False, "foobar"]]),
        ([b"", b"dict(a=", b' "q")', b"\n"], [{"a": "q"}]),
        ([b"[123]\n\n\n", b"\n\n"], [[123]]),
    ],
)
def test_json_encoding_custom_decoder_func(data, expected):
    parser = create_json_parser(lambda x: eval(x.decode("utf-8")))

    result = []
    for part in data:
        result.extend(parser(part))

    assert expected == result
