import pytest

from ffurf import FfurfConfig
from .test_ffurf import fill_ffurf, test_config_root, test_config_default


def test_key_to_envkey():
    assert FfurfConfig.key_to_envkey("my-str") == "MY_STR"
    assert FfurfConfig.key_to_envkey("my_str") == "MY_STR"
    assert FfurfConfig.key_to_envkey("MY_str") == "MY_STR"


# Use monkeypatch to safely fiddle with env
# Only test root env as we don't support anything more clever
def test_values_from_env(fill_ffurf, test_config_root, monkeypatch):

    for k, v in test_config_root.items():
        monkeypatch.setenv(FfurfConfig.key_to_envkey(k), str(v))

    fill_ffurf.from_env()
    for k, v in test_config_root.items():
        assert fill_ffurf[k] == v
        assert fill_ffurf.config[k]["source"] == "env:%s" % FfurfConfig.key_to_envkey(k)
    assert fill_ffurf.is_valid()
