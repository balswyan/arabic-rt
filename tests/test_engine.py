import arabic_rt as ar

ROUND_TRIP = [
    "مرحبا", "سلم", "الله", "لا", "لأ", "لإ", "لآ",
    "مرحبا بالعالم", "السلام عليكم ورحمة الله",
    "Hello مرحبا World", "اكتب 123 و user@mail.com هنا",
    "بسم الله الرحمن الرحيم",
]


def test_contains_arabic():
    assert ar.contains_arabic("مرحبا")
    assert ar.contains_arabic("hi مرحبا")
    assert not ar.contains_arabic("hello 123")
    assert not ar.contains_arabic("")


def test_is_shaped():
    assert ar.is_shaped(ar.fix("مرحبا"))
    assert not ar.is_shaped("مرحبا")
    assert not ar.is_shaped("hello")


def test_fix_noop_on_non_arabic():
    for s in ["", "hello world", "12345", "user@mail.com"]:
        assert ar.fix(s) == s


def test_fix_idempotent():
    once = ar.fix("مرحبا بالعالم")
    assert ar.fix(once) == once  # already shaped -> unchanged


def test_unfix_noop_on_logical():
    assert ar.unfix("مرحبا") == "مرحبا"
    assert ar.unfix("hello") == "hello"
    assert ar.unfix("") == ""


def test_shape_keeps_order():
    shaped = ar.shape("سلم")
    assert shaped == "ﺳﻠﻢ"  # initial-medial-final, logical order (NOT reversed)


def test_allah_ligature():
    assert ar.fix("الله", combine_allah=True) == "ﷲ"
    assert ar.unfix("ﷲ") == "الله"
    # word boundary only: اللهم must NOT collapse
    assert "ﷲ" not in ar.fix("اللهم", combine_allah=True)


def test_lam_alef_ligature():
    assert ar.fix("لا") == "ﻻ"
    assert ar.unfix("ﻻ") == "لا"


import pytest  # noqa: E402


@pytest.mark.parametrize("text", ROUND_TRIP)
def test_round_trip_game_preset(text):
    assert ar.unfix(ar.fix(text, ar.GAME)) == text


@pytest.mark.parametrize("text", ROUND_TRIP)
def test_round_trip_plain(text):
    assert ar.unfix(ar.fix(text)) == text


def test_game_preset_joins_words():
    baked = ar.fix("مرحبا بالعالم", ar.GAME)
    assert "\u00A0" in baked      # words joined by nbsp for word-by-word readers
    assert " " not in baked


def test_unfix_normalizes_newlines_to_spaces():
    # fix() may insert line breaks (wrapping); unfix() recovers a single logical
    # line suitable for TTS, so newlines collapse to spaces by design.
    baked = ar.fix("عربي\nمتعدد الأسطر", ar.GAME)
    assert ar.unfix(baked) == "عربي متعدد الأسطر"
