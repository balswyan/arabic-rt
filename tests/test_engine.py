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


# ---------------------------------------------------------------------------
# Partial-shaping tests (hardening for real-world OCR / legacy input)
# ---------------------------------------------------------------------------

def test_unfix_partial_shaped_first_word():
    # First word in presentation form (OCR recognised it), second word raw.
    # unfix() must de-shape the shaped word and leave the raw word alone.
    shaped_word = ar.shape("مرحبا")          # presentation forms, logical order
    raw_word    = "بالعالم"
    partial     = shaped_word + " " + raw_word
    result      = ar.unfix(partial)
    assert result == "مرحبا بالعالم"


def test_unfix_partial_shaped_last_word():
    # Raw word first, shaped word last.
    raw_word    = "مرحبا"
    shaped_word = ar.shape("بالعالم")
    partial     = raw_word + " " + shaped_word
    result      = ar.unfix(partial)
    assert result == "مرحبا بالعالم"


def test_unfix_partial_no_presentation_forms_remaining():
    # After unfix() on partial input, no presentation-form codepoints should remain.
    shaped_word = ar.shape("مرحبا")
    partial     = shaped_word + " " + "بالعالم"
    result      = ar.unfix(partial)
    has_pf = any(0xFB50 <= ord(c) <= 0xFDFF or 0xFE70 <= ord(c) <= 0xFEFF for c in result)
    assert not has_pf


def test_unfix_partial_mixed_latin():
    # Shaped Arabic word (from fix()) mixed with Latin — Latin must be untouched.
    # We use fix() not shape() here: fix() is what produces real-world baked output.
    # A line with ONE fully-shaped Arabic token is treated as fully baked (we can't
    # distinguish "shaped-logical" from "shaped-visual" with a single word).
    baked  = ar.fix("مرحبا Hello")    # -> "Hello ﺎﺒﺣﺮﻣ" (visual order)
    result = ar.unfix(baked)
    assert "Hello" in result
    assert "مرحبا" in result


def test_unfix_fully_shaped_unchanged_behaviour():
    # Fully shaped text (output of fix()) must still round-trip correctly
    # after the partial-shaping detection is added.
    for text in [
        "مرحبا بالعالم",
        "السلام عليكم ورحمة الله",
        "Hello مرحبا World",
        "اكتب 123 و user@mail.com هنا",
    ]:
        assert ar.unfix(ar.fix(text)) == text
