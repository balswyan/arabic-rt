# Changelog

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
