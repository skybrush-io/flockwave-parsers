from flockwave.parsers import create_line_parser

import pytest


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ([b""], []),
        ([b"abcde\nfgh\nijkl\n"], [b"abcde", b"fgh", b"ijkl"]),
        ([b"abcde\nfgh\nij", b"kl\n"], [b"abcde", b"fgh", b"ijkl"]),
        ([b"abcde\rfgh\r", b"\r\nij", b"kl\n"], [b"abcde", b"fgh", b"ijkl"]),
        (
            [b"abcd", b"e\r\r\r\nfgh", b"\n\rxx", b"\nijkl\n"],
            [b"abcde", b"fgh", b"ijkl"],
        ),
    ],
)
def test_line_parser_with_min_length(data, expected):
    parser = create_line_parser(min_length=3)

    result = []
    for part in data:
        result.extend(parser(part))

    assert expected == result
