# Changelog

## 0.1.0
- Initial release.
- `shape()` — contextual Arabic shaping (isolated/initial/medial/final, lam-alef + optional الله ligature).
- `fix()` — bake logical Arabic into visual-order presentation forms that render correctly on naive clients.
- `unfix()` — reverse the bake back to logical Arabic (for TTS, search, logging).
- `GAME` preset for word-by-word chat readers; `contains_arabic()`, `is_shaped()` helpers.
- Forward output validated byte-for-byte against `arabic_reshaper` + `python-bidi`; `unfix(fix(x)) == x` round-trip tests.
