from flockwave.encoders import create_length_prefixed_encoder

import pytest


@pytest.mark.parametrize(("data", "expected"), [(b"foobar", b"\x06foobar")])
def test_length_prefixed_encoder_with_max_length(data, expected):
    encoder = create_length_prefixed_encoder(max_length=42)
    assert expected == encoder(data)


@pytest.mark.parametrize(
    ("header_length", "endianness", "data", "expected"),
    [
        (1, "big", b"foobar", b"\x06foobar"),
        (2, "big", b"foobarbaz", b"\x00\x09foobarbaz"),
        (3, "big", b"foo", b"\x00\x00\x03foo"),
        (4, "big", b"spam spam spam", b"\x00\x00\x00\x0espam spam spam"),
        (5, "big", b"foobar--", b"\x00\x00\x00\x00\x08foobar--"),
        (1, "little", b"foobar", b"\x06foobar"),
        (2, "little", b"foobarbaz", b"\x09\x00foobarbaz"),
        (3, "little", b"foo", b"\x03\x00\x00foo"),
        (4, "little", b"spam spam spam", b"\x0e\x00\x00\x00spam spam spam"),
        (5, "little", b"foobar--", b"\x08\x00\x00\x00\x00foobar--"),
    ],
)
def test_length_prefixed_encoder_with_header_length(
    header_length, endianness, data, expected
):
    encoder = create_length_prefixed_encoder(
        header_length=header_length, endianness=endianness
    )
    assert expected == encoder(data)
