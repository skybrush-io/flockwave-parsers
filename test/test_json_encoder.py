from json import JSONEncoder
from flockwave.encoders.json import create_json_encoder, object_to_jsonable

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
        (["list\nwith\nnewlines"], b'["list\\nwith\\nnewlines"]\n'),
    ],
)
def test_json_encoding_orjson(message, expected):
    import orjson  # to ensure that orjson is available

    assert orjson is not None, "orjson should be installed in the test environment"
    encoder = create_json_encoder()
    observed = encoder(message)
    assert expected == observed


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ([123, "spam", {"a": 42}], b'[123,"spam",{"a":42}]\n'),
        (datetime.datetime(year=2004, month=4, day=17), b'"2004-04-17T00:00:00"\n'),
        (CustomObject(), b'["lovely spam!"]\n'),
        (["list\nwith\nnewlines"], b'["list\\nwith\\nnewlines"]\n'),
    ],
)
def test_json_encoding_builtin(message, expected):
    # This should be the built-in JSON encoder
    encoder = create_json_encoder("builtin")
    observed = encoder(message)
    assert expected == observed


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ([123, "spam", {"a": 42}], b'[\n  123,\n  "spam",\n  {\n    "a": 42\n  }\n]\n'),
        (datetime.datetime(year=2004, month=4, day=17), b'"2004-04-17T00:00:00"\n'),
        (CustomObject(), b'[\n  "lovely spam!"\n]\n'),
        (["list\nwith\nnewlines"], b'[\n  "list\\nwith\\nnewlines"\n]\n'),
    ],
)
def test_json_encoding_custom_builtin_encoder(message, expected):
    encoder = create_json_encoder(
        JSONEncoder(
            sort_keys=False,
            indent=2,
            default=object_to_jsonable,
        )
    )
    observed = encoder(message)
    assert expected == observed


@pytest.mark.parametrize(
    ("message",),
    [
        ([123, "spam", {"a": 42}],),
        (datetime.datetime(year=2004, month=4, day=17),),
        (CustomObject(),),
        (["list\nwith\nnewlines"],),
    ],
)
def test_json_encoding_custom_encoder_func(message):
    encoder = create_json_encoder(
        lambda x: repr(x).encode("utf-8"), wrapper=lambda x: b"[" + x + b"]"
    )
    observed = encoder(message)
    assert b"[" + repr(message).encode("utf-8") + b"]" == observed
