import pytest

from ffurf import FfurfConfig


@pytest.fixture
def basic_ffurf():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-str")
    ffurf.add_config_key("my-int", key_type=int)
    ffurf.add_config_key("my-unset-key")
    ffurf.add_config_key("my-zero", key_type=int, default_value=0)
    ffurf.add_config_key("one-to-zero", key_type=int, default_value=1)

    ffurf.set_config_key("my-str", "hoot")
    ffurf.set_config_key("my-int", 800)
    return ffurf


@pytest.fixture
def tiered_ffurf():
    ffurf = FfurfConfig()
    ffurf.add_config_key("root-key", key_type=int)
    ffurf.add_config_key("default-key", key_type=int)
    ffurf.add_config_key("profile-key", key_type=int)
    return ffurf


@pytest.fixture
def fill_ffurf():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-str")
    ffurf.add_config_key("my-int", key_type=int)
    return ffurf


@pytest.fixture
def test_config_root():
    return {
        "my-str": "hoot",
        "my-int": 100,
    }


@pytest.fixture
def test_config_default():
    return {
        "my-str": "meow",
        "default": {
            "my-str": "hoot",
            "my-int": 100,
        },
    }


@pytest.fixture
def test_config_profile():
    return {
        "my-str": "meow",
        "default": {
            "my-str": "meow",
            "my-int": -100,
        },
        "profile": {
            "sam": {
                "my-str": "hoot",
                "my-int": 100,
            },
        },
    }


@pytest.fixture
def test_config_tiers():
    in_d = {
        "root-key": 1,
        "default-key": 1,
        "profile-key": 1,
        "default": {
            "default-key": 2,
            "profile-key": 2,
        },
        "profile": {
            "sam": {
                "profile-key": 3,
            },
        },
    }

    out_d = {
        "root-key": 1,
        "default-key": 2,
        "profile-key": 3,
    }
    return in_d, out_d


def _assert_config(ffurf, key, key_type, value, source=None, source_contains=None):
    assert key in ffurf.config
    assert key in ffurf.config_keys
    assert ffurf.config[key]["value"] == value
    assert ffurf.config[key]["type"] is key_type

    if source:
        assert ffurf.config[key]["source"] == source
    if source_contains:
        assert source_contains in ffurf.config[key]["source"]


def _assert_config_values(ffurf, source_d, source_contains_l=None):
    for key, value in source_d.items():
        assert ffurf.config[key]["value"] == value
        if not source_contains_l:
            source_contains_l = []

        for source_str in source_contains_l:
            assert source_str in ffurf.config[key]["source"]


def test_init_ffurf():
    FfurfConfig()


def test_add_config_key():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-key")

    assert len(ffurf.config_keys) == 1
    assert len(ffurf.config) == 1

    _assert_config(ffurf, key="my-key", key_type=str, value=None, source=None)
    assert not ffurf.config["my-key"]["secret"]
    assert not ffurf.config["my-key"]["partial_secret"]
    assert not ffurf.config["my-key"]["optional"]


def test_add_config_key_default_value():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-key", default_value="hoot")
    _assert_config(
        ffurf, key="my-key", key_type=str, value="hoot", source="ffurf:default"
    )


def test_add_config_key_type_int():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-key", int, default_value="100")
    _assert_config(ffurf, key="my-key", key_type=int, value=100, source="ffurf:default")


def test_add_config_key_zero_ok(basic_ffurf):
    _assert_config(
        basic_ffurf, key="my-zero", key_type=int, value=0, source="ffurf:default"
    )


def test_contains(basic_ffurf):
    assert "my-str" in basic_ffurf
    assert "no-key" not in basic_ffurf


def test_iter():
    ffurf = FfurfConfig()
    ffurf.add_config_key("c")
    ffurf.add_config_key("b")
    ffurf.add_config_key("a")

    it = iter(ffurf)
    assert next(it) == "a"
    assert next(it) == "b"
    assert next(it) == "c"
    with pytest.raises(StopIteration):
        next(it)


def test_set_config(basic_ffurf):
    basic_ffurf.set_config_key("my-unset-key", "hoot")
    _assert_config(
        basic_ffurf,
        key="my-unset-key",
        key_type=str,
        value="hoot",
        source_contains="src:",
    )


def test_setitem(basic_ffurf):
    basic_ffurf["my-unset-key"] = "hoot"
    _assert_config(
        basic_ffurf,
        key="my-unset-key",
        key_type=str,
        value="hoot",
        source_contains="src:",
    )


def test_set_config_keyerror(basic_ffurf):
    with pytest.raises(KeyError):
        basic_ffurf.set_config_key("no-key", 1)
    assert "no-key" not in basic_ffurf.config
    assert "no-key" not in basic_ffurf.config_keys


def test_setitem_keyerror(basic_ffurf):
    with pytest.raises(KeyError):
        basic_ffurf["no-key"] = 1
    assert "no-key" not in basic_ffurf.config
    assert "no-key" not in basic_ffurf.config_keys


def test_setitem_required_exception(basic_ffurf):
    with pytest.raises(TypeError):
        basic_ffurf["my-str"] = None


def test_can_set_nonoptional_key_to_untruth(basic_ffurf):
    basic_ffurf["my-zero"] = 0


def test_can_set_key_to_untruth(basic_ffurf):
    basic_ffurf["one-to-zero"] = 0
    assert basic_ffurf["one-to-zero"] == 0


def test_getitem(basic_ffurf):
    assert basic_ffurf["my-str"] == "hoot"
    assert basic_ffurf["my-int"] == 800


def test_default_zero_getitem(basic_ffurf):
    assert basic_ffurf["my-zero"] == 0
    assert basic_ffurf["my-zero"] == 0


def test_default_zero_not_overwritten_by_getclean_default(basic_ffurf):
    assert basic_ffurf.get_clean("my-zero") == "0"


def test_unset_key_is_empty_string_for_getclean(basic_ffurf):
    assert basic_ffurf.get_clean("my-unset-key") == ""


def test_default_zero_not_overwritten_by_get_default(basic_ffurf):
    assert basic_ffurf.get("my-zero", default=1) == 0


def test_getitem_keyerror(basic_ffurf):
    with pytest.raises(KeyError):
        basic_ffurf["no-key"]


def test_get_clean_keyerror(basic_ffurf):
    with pytest.raises(KeyError):
        basic_ffurf.get_clean("no-key")


def test_get_keyconf_keyerror(basic_ffurf):
    with pytest.raises(KeyError):
        basic_ffurf.get_keyconf("no-key")


def test_getitem(basic_ffurf):
    assert basic_ffurf["my-str"] == "hoot"
    assert basic_ffurf["my-int"] == 800


def test_get(basic_ffurf):
    assert basic_ffurf.get("my-str") == "hoot"


def test_get_keyconf(basic_ffurf):
    keyconf = basic_ffurf.get_keyconf("my-str")
    assert keyconf["name"] == "my-str"
    assert not keyconf["optional"]
    assert not keyconf["partial_secret"]
    assert not keyconf["secret"]
    assert "src" in keyconf["source"]
    assert keyconf["value"] == "hoot"
    assert keyconf["type"] == str


def test_get_keyconf(basic_ffurf):
    keyconf = basic_ffurf.get_keyconf("my-int")
    assert keyconf["name"] == "my-int"
    assert not keyconf["optional"]
    assert not keyconf["partial_secret"]
    assert not keyconf["secret"]
    assert "src" in keyconf["source"]
    assert keyconf["value"] == 800
    assert keyconf["type"] == int


def test_get_key_not_overwritten_by_default(basic_ffurf):
    assert basic_ffurf.get("my-str", default="meow") == "hoot"


def test_get_nokey_returns_default(basic_ffurf):
    assert basic_ffurf.get("no-key", default="hoot") == "hoot"


def test_invalid_blank_ffurf():
    # Empty config technically valid
    ffurf = FfurfConfig()
    assert ffurf.is_valid()


def test_invalid_unset_required_ffurf():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-key")
    assert not ffurf.is_valid()


def test_valid_unset_optional_ffurf():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-key", optional=True)
    assert ffurf.is_valid()


def test_valid_with_untruthy():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-int", key_type=int, default_value=0)
    assert ffurf.is_valid()


def test_values_from_root_dict(fill_ffurf, test_config_root):
    fill_ffurf.from_dict(test_config_root)

    for k, v in test_config_root.items():
        assert fill_ffurf[k] == v
        assert "src" in fill_ffurf.config[k]["source"]
    assert fill_ffurf.is_valid()


def test_values_from_default_dict_override_root(fill_ffurf, test_config_default):
    fill_ffurf.from_dict(test_config_default)

    for k, v in test_config_default["default"].items():
        assert fill_ffurf[k] == v
        assert "src" in fill_ffurf.config[k]["source"]
        assert "default" in fill_ffurf.config[k]["source"]
    assert fill_ffurf.is_valid()


def test_values_from_profile_dict_override_default_and_root(
    fill_ffurf, test_config_profile
):
    fill_ffurf.from_dict(test_config_profile, profile="sam")

    for k, v in test_config_profile["profile"]["sam"].items():
        assert fill_ffurf[k] == v
        assert "src" in fill_ffurf.config[k]["source"]
        assert "profile.sam" in fill_ffurf.config[k]["source"]
    assert fill_ffurf.is_valid()


def test_values_are_correctly_overriden_better_than_before(
    tiered_ffurf, test_config_tiers
):
    tiered_ffurf.from_dict(test_config_tiers[0], profile="sam")
    _assert_config_values(tiered_ffurf, test_config_tiers[1])


def test_update_key_append_source(basic_ffurf):
    basic_ffurf.set_config_key("my-unset-key", "hoot", source="hoot")
    basic_ffurf.set_config_key(
        "my-unset-key", "hoot", source="meow", append_source=True
    )
    assert basic_ffurf.config["my-unset-key"]["source"] == "hoot,meow"


def test_empty_string_is_invalid(basic_ffurf):
    basic_ffurf.set_config_key("my-unset-key", "", source="hoot")
    assert not basic_ffurf.is_valid()

def test_table(basic_ffurf, capfd):
    basic_ffurf.print_table()
    out, err = capfd.readouterr()
    assert out == (
        "Key           Value     Source                                                       Valid\n"
        "============  ========  ===========================================================  =====\n"
        "my-int        800       src:/mnt/c/Users/Sam/Projects/ffurf/tests/test_ffurf.py@L16  O\n"
        "my-str        hoot      src:/mnt/c/Users/Sam/Projects/ffurf/tests/test_ffurf.py@L15  O\n"
        "my-unset-key  --------  unset                                                        X\n"
        "my-zero       0         ffurf:default                                                O\n"
        "one-to-zero   1         ffurf:default                                                O\n"
    )

def test_validate(basic_ffurf, capfd):
    with pytest.raises(SystemExit) as e:
        basic_ffurf.validate()
    out, err = capfd.readouterr()
    assert "Key           Value     Source                                                       Valid\n" in out
    assert e.value.code == 78