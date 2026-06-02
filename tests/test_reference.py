"""Parity with the reference pipeline: arabic_reshaper + python-bidi (RTL base)."""
import pytest

import arabic_rt as ar

arabic_reshaper = pytest.importorskip("arabic_reshaper")
bidi = pytest.importorskip("bidi.algorithm")
from bidi.algorithm import get_display  # noqa: E402

PHRASES = [
    "مرحبا", "سلام", "كتاب", "بيت", "مدرسة", "شمس", "قلم", "عربية",
    "السلام عليكم", "كيف حالك", "أهلا وسهلا", "صباح الخير",
    "مرحبا بالعالم", "هذا اختبار", "نص عربي طويل للتجربة",
    "Hello مرحبا", "مرحبا World", "عام 2026", "رقم 100",
]


def reference(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text), base_dir="R")


@pytest.mark.parametrize("text", PHRASES)
def test_matches_reference(text):
    # combine_allah=True mirrors arabic_reshaper's default ligature behaviour
    assert ar.fix(text, combine_allah=True) == reference(text)
