# Changelog

## 0.1.4
- **Hardened `unfix()` for partial shaping** (real-world OCR / legacy input).
  Previously, any string containing even one presentation-form character caused
  the entire line to be reversed, scrambling surrounding raw Arabic words.
  Now detects per-line whether Arabic is fully shaped (fix() output) or only
  partially shaped (OCR artefact / mixed source), and chooses full-line reversal
  vs in-place de-shaping accordingly. Zero regression on existing round-trip tests.
- Extracted `_dechar()` helper (internal); no public API change.
- Added 5 new tests covering partial-shaping edge cases.

## 0.1.3
- README corrections and PyPI metadata sync. No code changes.

## 0.1.2
- Publish the updated README to PyPI (badges, live-demo link, and the .NET/Unity pointer). No code changes.

## 0.1.1
- Fix project URLs (Homepage/Repository/Issues) that pointed at a placeholder.
- README: add badges, live-demo (Hugging Face Space) link, and a pointer to the .NET/Unity package. No code changes.

## 0.1.0
- Initial release.
- `shape()` — contextual Arabic shaping (isolated/initial/medial/final, lam-alef + optional الله ligature).
- `fix()` — bake logical Arabic into visual-order presentation forms that render correctly on naive clients.
- `unfix()` — reverse the bake back to logical Arabic (for TTS, search, logging).
- `GAME` preset for word-by-word chat readers; `contains_arabic()`, `is_shaped()` helpers.
- Forward output validated byte-for-byte against `arabic_reshaper` + `python-bidi`; `unfix(fix(x)) == x` round-trip tests.
