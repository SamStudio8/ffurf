import pytest
import toml

from .test_ffurf import (
    tiered_ffurf,
    test_config_tiers,
    _assert_config_values,
)


@pytest.fixture
def toml_config(tmpdir_factory, test_config_tiers):
    toml_fp = str(tmpdir_factory.mktemp("test_data").join("myconf.toml"))
    with open(toml_fp, "w") as fh:
        toml.dump(test_config_tiers[0], fh)
    return toml_fp


def test_exception_from_missing_toml(tiered_ffurf):
    with pytest.raises(OSError):
        tiered_ffurf.from_toml("missing.toml")


def test_values_from_profile_toml(tiered_ffurf, test_config_tiers, toml_config):
    tiered_ffurf.from_toml(toml_config, profile="sam")
    _assert_config_values(tiered_ffurf, test_config_tiers[1])
    assert tiered_ffurf.is_valid()
