import json
from typing import List

import pytest
import toml

from ffurf import FfurfConfig


@pytest.fixture
def list_ffurf():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-strs", key_type=list[str])
    ffurf.add_config_key("my-ints", key_type=list[int])
    ffurf.add_config_key("my-bare", key_type=list)
    return ffurf


@pytest.fixture
def list_config():
    return {
        "my-strs": ["x", "y", "z"],
        "my-ints": [1, 2, 3],
        "my-bare": ["a", "b"],
    }


def _assert_list_values(ffurf, d):
    for k, v in d.items():
        assert ffurf[k] == v


def test_list_from_dict(list_ffurf, list_config):
    list_ffurf.from_dict(list_config)
    _assert_list_values(list_ffurf, list_config)
    assert list_ffurf.is_valid()


def test_list_from_toml(list_ffurf, list_config, tmpdir_factory):
    toml_fp = str(tmpdir_factory.mktemp("test_data").join("myconf.toml"))
    with open(toml_fp, "w") as fh:
        toml.dump(list_config, fh)

    list_ffurf.from_toml(toml_fp)
    _assert_list_values(list_ffurf, list_config)


def test_list_from_json(list_ffurf, list_config, tmpdir_factory):
    json_fp = str(tmpdir_factory.mktemp("test_data").join("myconf.json"))
    with open(json_fp, "w") as fh:
        json.dump(list_config, fh)

    list_ffurf.from_json(json_fp)
    _assert_list_values(list_ffurf, list_config)


def test_list_from_env(list_ffurf, list_config, monkeypatch):
    monkeypatch.setenv("MY_STRS", "x,y,z")
    monkeypatch.setenv("MY_INTS", "1,2,3")
    monkeypatch.setenv("MY_BARE", "a,b")

    list_ffurf.from_env()
    _assert_list_values(list_ffurf, list_config)


def test_list_from_env_strips_whitespace(list_ffurf, monkeypatch):
    monkeypatch.setenv("MY_STRS", "x, y,  z")
    list_ffurf.from_env()
    assert list_ffurf["my-strs"] == ["x", "y", "z"]


def test_list_elements_are_coerced(list_ffurf):
    # ints arriving as strings become ints, and vice versa
    list_ffurf.from_dict({"my-ints": ["1", "2"], "my-strs": [1, 2]})
    assert list_ffurf["my-ints"] == [1, 2]
    assert list_ffurf["my-strs"] == ["1", "2"]


def test_bare_list_leaves_elements_alone(list_ffurf):
    list_ffurf.from_dict({"my-bare": [1, "a"]})
    assert list_ffurf["my-bare"] == [1, "a"]


def test_typing_list_is_supported():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-strs", key_type=List[str])
    ffurf.set_config_key("my-strs", ["x", "y"])
    assert ffurf["my-strs"] == ["x", "y"]


def test_scalar_becomes_single_item_list(list_ffurf):
    list_ffurf.set_config_key("my-ints", 5)
    assert list_ffurf["my-ints"] == [5]


def test_list_default_value():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-strs", key_type=list[str], default_value="a,b")
    assert ffurf["my-strs"] == ["a", "b"]
    assert ffurf.get_source("my-strs") == "ffurf:default"


def test_list_custom_separator():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-strs", key_type=list[str], separator=":")
    ffurf.set_config_key("my-strs", "a:b:c")
    assert ffurf["my-strs"] == ["a", "b", "c"]


def test_separator_on_non_list_key_raises():
    ffurf = FfurfConfig()
    with pytest.raises(ValueError):
        ffurf.add_config_key("my-str", key_type=str, separator=":")


def test_separator_on_bare_list_is_allowed():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-bare", key_type=list, separator=":")
    ffurf.set_config_key("my-bare", "a:b")
    assert ffurf["my-bare"] == ["a", "b"]


def test_default_separator_on_non_list_key_is_fine():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-str", key_type=str, separator=",")
    ffurf.set_config_key("my-str", "a,b")
    assert ffurf["my-str"] == "a,b"


def test_empty_list_is_invalid(list_ffurf):
    list_ffurf.from_dict({"my-strs": [], "my-ints": [1], "my-bare": ["a"]})
    assert list_ffurf["my-strs"] == []
    assert not list_ffurf.is_valid()


def test_empty_list_is_valid_when_optional():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-strs", key_type=list[str], optional=True)
    ffurf.set_config_key("my-strs", [])
    assert ffurf.is_valid()


def test_bad_element_type_raises(list_ffurf):
    with pytest.raises(TypeError):
        list_ffurf.set_config_key("my-ints", ["hoot"])


def test_list_get_clean_joins_elements(list_ffurf, list_config):
    list_ffurf.from_dict(list_config)
    assert list_ffurf.get_clean("my-strs") == "x,y,z"
    assert list_ffurf.get_clean("my-ints") == "1,2,3"


def test_secret_list_is_hidden():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-strs", key_type=list[str], secret=True)
    ffurf.set_config_key("my-strs", ["hoot", "meow"])
    assert ffurf.get_clean("my-strs") == "********"
    assert "hoot" not in str(ffurf)


def test_partial_secret_list_is_partially_hidden():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-strs", key_type=list[str], partial_secret=4)
    ffurf.set_config_key("my-strs", ["thisisverysecret", "hoot"])
    assert ffurf.get_clean("my-strs") == "********hoot"


def test_list_to_env(list_ffurf, list_config):
    list_ffurf.from_dict(list_config)
    env = list_ffurf.to_env()
    assert 'MY_STRS="x,y,z"' in env
    assert 'MY_INTS="1,2,3"' in env


def test_list_env_round_trip(list_ffurf, list_config, monkeypatch):
    list_ffurf.from_dict(list_config)

    # feed to_env's output back in through the environment
    for line in list_ffurf.to_env().splitlines():
        k, v = line.split("=", 1)
        monkeypatch.setenv(k, v.strip('"'))

    reloaded = FfurfConfig()
    reloaded.add_config_key("my-strs", key_type=list[str])
    reloaded.add_config_key("my-ints", key_type=list[int])
    reloaded.add_config_key("my-bare", key_type=list)
    reloaded.from_env()
    _assert_list_values(reloaded, list_config)


def test_list_to_json(list_ffurf, list_config):
    list_ffurf.from_dict(list_config)
    assert json.loads(list_ffurf.to_json())["my-strs"] == ["x", "y", "z"]


def test_list_to_toml(list_ffurf, list_config):
    list_ffurf.from_dict(list_config)
    assert toml.loads(list_ffurf.to_toml())["my-ints"] == [1, 2, 3]


def test_list_to_groovy(list_ffurf, list_config):
    list_ffurf.from_dict(list_config)
    groovy = list_ffurf.to_groovy()
    assert 'my-strs = ["x", "y", "z"]' in groovy
    assert "my-ints = [1, 2, 3]" in groovy


def test_list_to_argparse(list_ffurf):
    parser = list_ffurf.to_argparse()
    args = parser.parse_args(
        ["--my-strs", "x", "y", "--my-ints", "1", "2", "--my-bare", "a"]
    )
    # argparse turns --my-strs into the my_strs dest
    assert vars(args)["my_strs"] == ["x", "y"]
    assert vars(args)["my_ints"] == [1, 2]
