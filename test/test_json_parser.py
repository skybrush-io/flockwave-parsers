from flockwave.parsers.json import create_json_parser

import pytest


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ([b""], []),
        ([b"[123", b', false, "fo', b'obar"]\n'], [[123, False, "foobar"]]),
        ([b"", b'{"a":', b' "q"}', b"\n"], [dict(a="q")]),
        ([b"[123]\n\n\n", b"\n\n"], [[123]]),
    ],
)
def test_line_parser_with_min_length(data, expected):
    parser = create_json_parser()

    result = []
    for part in data:
        result.extend(parser(part))

    assert expected == result
