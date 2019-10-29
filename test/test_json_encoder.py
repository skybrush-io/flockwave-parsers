from flockwave.encoders.json import create_json_encoder

import datetime
import pytest


class CustomObject:
    @property
    def json(self):
        return ["lovely spam!"]


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ([123, "spam", {"a": 42}], b'[123,"spam",{"a":42}]\n'),
        (datetime.datetime(year=2004, month=4, day=17), b'"2004-04-17T00:00:00"\n'),
        (CustomObject(), b'["lovely spam!"]\n'),
    ],
)
def test_json_encoding(message, expected):
    encoder = create_json_encoder()
    observed = encoder(message)
    assert expected == observed
