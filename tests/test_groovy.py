import pytest
import json

from .test_ffurf import (
    basic_ffurf,
    _assert_config_values,
)


@pytest.fixture
def basic_ffurf_res():
    return """params {
    my-int = 800
    my-str = "hoot"
    my-unset-key = ""
    my-zero = 0
    one-to-zero = 1
}"""


def test_to_groovy(basic_ffurf, basic_ffurf_res):
    assert basic_ffurf.to_groovy() == basic_ffurf_res
