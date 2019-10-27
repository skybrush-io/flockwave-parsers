from flockwave.parsers import create_length_prefixed_parser, ParseError

import pytest


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ([b""], []),
        ([b"\x00\x05abcde\x00\x03fgh\x00\x04ijkl"], [b"abcde", b"fgh", b"ijkl"]),
        (
            [b"\x00\x05abcde\x00\x03fgh\x00\x00\x00\x02xx\x00\x04ijkl"],
            [b"abcde", b"fgh", b"ijkl"],
        ),
        (
            [
                b"\x00\x05abcde",
                b"\x00\x03f",
                b"gh\x00\x00",
                b"\x00",
                b"\x02x",
                b"x\x00\x04",
                b"ijkl",
            ],
            [b"abcde", b"fgh", b"ijkl"],
        ),
    ],
)
def test_big_endian_parser_with_min_length(data, expected):
    parser = create_length_prefixed_parser(header_length=2, min_length=3)

    result = []
    for part in data:
        result.extend(parser(part))

    assert expected == result


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        ([b""], []),
        ([b"\x05\x00abcde\x03\x00fgh\x04\x00ijkl"], [b"abcde", b"fgh", b"ijkl"]),
        (
            [b"\x05\x00abcde\x03\x00fgh\x00\x00\x02\x00xx\x04\x00ijkl"],
            [b"abcde", b"fgh", b"ijkl"],
        ),
        (
            [
                b"\x05\x00abcde",
                b"\x03\x00f",
                b"gh\x00\x00",
                b"\x02",
                b"\x00x",
                b"x\x04\x00",
                b"ijkl",
            ],
            [b"abcde", b"fgh", b"ijkl"],
        ),
    ],
)
def test_little_endian_parser_with_min_length(data, expected):
    parser = create_length_prefixed_parser(
        header_length=2, min_length=3, endianness="little"
    )

    result = []
    for part in data:
        result.extend(parser(part))

    assert expected == result


def test_parser_throws_error_if_packet_is_too_large():
    parser = create_length_prefixed_parser(max_length=4)
    with pytest.raises(ParseError, match="packet length exceeds limit"):
        parser(b"\x05abcde")


def test_parser_resets_after_parse_error():
    parser = create_length_prefixed_parser(max_length=4)
    with pytest.raises(ParseError, match="packet length exceeds limit"):
        parser(b"\x05abcde")
    with pytest.raises(StopIteration):
        # once a parser raised a ParseError, it cannot be used any more
        parser(b"\x04abcd\x02ef")


def test_fails_if_no_length_and_no_header_size():
    with pytest.raises(ValueError, match="at least one of"):
        create_length_prefixed_parser()
