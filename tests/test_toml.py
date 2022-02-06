import pytest
import toml

from .test_ffurf import (
    fill_ffurf,
    test_config_root,
    test_config_default,
    test_config_profile,
    _assert_config_values,
)


@pytest.fixture
def toml_config_root(tmpdir_factory, test_config_root):
    toml_fp = str(tmpdir_factory.mktemp("test_data").join("myconf.toml"))
    with open(toml_fp, "w") as fh:
        toml.dump(test_config_root, fh)
    return toml_fp


@pytest.fixture
def toml_config_default(tmpdir_factory, test_config_default):
    toml_fp = str(tmpdir_factory.mktemp("test_data").join("myconf.toml"))
    with open(toml_fp, "w") as fh:
        toml.dump(test_config_default, fh)
    return toml_fp


@pytest.fixture
def toml_config_profile(tmpdir_factory, test_config_profile):
    toml_fp = str(tmpdir_factory.mktemp("test_data").join("myconf.toml"))
    with open(toml_fp, "w") as fh:
        toml.dump(test_config_profile, fh)
    return toml_fp


def test_exception_from_missing_toml(fill_ffurf):
    with pytest.raises(OSError):
        fill_ffurf.from_toml("missing.toml")


def test_values_from_root_toml(fill_ffurf, toml_config_root, test_config_root):
    fill_ffurf.from_toml(toml_config_root)
    _assert_config_values(fill_ffurf, test_config_root)
    assert fill_ffurf.is_valid()


def test_values_from_default_toml(fill_ffurf, test_config_default, toml_config_default):
    fill_ffurf.from_toml(toml_config_default)
    _assert_config_values(fill_ffurf, test_config_default["default"])
    assert fill_ffurf.is_valid()


def test_values_from_profile_toml(fill_ffurf, test_config_profile, toml_config_profile):
    fill_ffurf.from_toml(toml_config_profile, profile="sam")
    _assert_config_values(
        fill_ffurf,
        test_config_profile["profile"]["sam"],
        source_contains_l=["toml", "profile.sam"],
    )
    assert fill_ffurf.is_valid()
