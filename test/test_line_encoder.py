from flockwave.encoders import create_line_encoder

import pytest


@pytest.mark.parametrize(
    ("data", "expected"), [(b"", b"\n"), (b"abcd", b"abcd\n"), (b"ab\ncd", b"ab\ncd\n")]
)
def test_line_encoder(data, expected):
    encoder = create_line_encoder(encoder=lambda x: x)
    assert expected == encoder(data)
