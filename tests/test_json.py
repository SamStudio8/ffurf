import pytest
import json

from .test_ffurf import (
    tiered_ffurf,
    test_config_tiers,
    _assert_config_values,
)


@pytest.fixture
def json_config(tmpdir_factory, test_config_tiers):
    json_fp = str(tmpdir_factory.mktemp("test_data").join("myconf.json"))
    with open(json_fp, "w") as fh:
        json.dump(test_config_tiers[0], fh)
    return json_fp


def test_exception_from_missing_json(tiered_ffurf):
    with pytest.raises(OSError):
        tiered_ffurf.from_json("missing.json")


def test_values_from_profile_json(tiered_ffurf, test_config_tiers, json_config):
    tiered_ffurf.from_json(json_config, profile="sam")
    _assert_config_values(tiered_ffurf, test_config_tiers[1])
    assert tiered_ffurf.is_valid()
