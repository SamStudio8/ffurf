import pytest

from ffurf import FfurfConfig


@pytest.fixture
def secret_ffurf():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-secret", secret=True)
    ffurf.set_config_key("my-secret", "hoot")
    return ffurf


@pytest.fixture
def partial_secret_ffurf():
    ffurf = FfurfConfig()
    ffurf.add_config_key("my-secret", partial_secret=4)
    ffurf.set_config_key("my-secret", "thisisverysecrethoot")
    return ffurf


def test_secret_get_reveals_key(secret_ffurf):
    assert secret_ffurf.get("my-secret") == "hoot"


def test_secret_getitem_reveals_key(secret_ffurf):
    assert secret_ffurf["my-secret"] == "hoot"


def test_secret_print_hides_key(secret_ffurf):
    assert "hoot" not in str(secret_ffurf)
    assert "********" in str(secret_ffurf)


def test_secret_get_clean_hides_key(secret_ffurf):
    assert secret_ffurf.get_clean("my-secret") == "********"


def test_partial_secret_get_reveals_key(partial_secret_ffurf):
    assert partial_secret_ffurf.get("my-secret") == "thisisverysecrethoot"


def test_partial_secret_getitem_reveals_key(partial_secret_ffurf):
    assert partial_secret_ffurf["my-secret"] == "thisisverysecrethoot"


def test_partial_secret_print_hides_key(partial_secret_ffurf):
    assert "hoot" in str(partial_secret_ffurf)
    assert "thisisverysecret" not in str(partial_secret_ffurf)
    assert "********hoot" in str(partial_secret_ffurf)


def test_partial_secret_get_clean_hides_key(partial_secret_ffurf):
    assert partial_secret_ffurf.get_clean("my-secret") == "********hoot"
