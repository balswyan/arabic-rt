# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Core Arabic shaping + simplified BiDi + un-baking engine.

Pure Python, no dependencies. Validated against arabic_reshaper + python-bidi.
"""
from __future__ import annotations

from dataclasses import dataclass

from ._tables import (
    FORMS, LAM_ALEF, ALLAH, ALLAH_GLYPH, to_base, lam_alef_inverse,
)


@dataclass(frozen=True)
class Options:
    """Behaviour switches for :func:`fix`.

    The defaults produce standard, correct Arabic (contextual shaping + RTL
    reordering) and match the arabic_reshaper + python-bidi reference output.
    The remaining switches are opt-in tricks for *real-time clients* such as
    game chat boxes that render naively or read text word-by-word.
    """
    combine_allah: bool = False        # collapse the word الله into the single glyph ﷲ
    keep_ltr_runs: bool = True         # keep Latin / number / URL runs in reading order
    reverse_word_order: bool = True    # True: full RTL line; False: shape per-word, keep typed order
    word_joiner: str = " "             # char placed between words (e.g. " " for word-by-word readers)
    prevent_word_split: bool = False   # replace spaces with word_joiner so naive readers see one token
    max_line_chars: int = 0            # >0: wrap into lines of N chars (first words on top), each RTL


GAME = Options(
    combine_allah=True,
    word_joiner=" ",
    prevent_word_split=True,
)
"""Preset tuned for game chat (R.E.P.O.-style word-by-word readers)."""


_TRANSPARENT_RANGES = (
    (0x064B, 0x065F), (0x0670, 0x0670), (0x06D6, 0x06DC),
    (0x06DF, 0x06E4), (0x06E7, 0x06E8), (0x06EA, 0x06ED),
)


def _jtype(cp: int) -> str:
    g = FORMS.get(cp)
    if g is not None:
        return g[0]
    for lo, hi in _TRANSPARENT_RANGES:
        if lo <= cp <= hi:
            return "T"
    return "U"


def is_arabic_letter(cp: int) -> bool:
    return (0x0600 <= cp <= 0x06FF) or (0x0750 <= cp <= 0x077F)


def contains_arabic(s: str) -> bool:
    """True if *s* holds any raw (un-shaped) Arabic letter."""
    return any(is_arabic_letter(ord(c)) for c in s) if s else False


def is_shaped(s: str) -> bool:
    """True if *s* already holds shaped presentation forms (already baked)."""
    return any(0xFB50 <= ord(c) <= 0xFDFF or 0xFE70 <= ord(c) <= 0xFEFF for c in s) if s else False


def _prev_non_transparent(cps: list[int], idx: int) -> int:
    j = idx - 1
    while j >= 0 and _jtype(cps[j]) == "T":
        j -= 1
    return j


def _next_non_transparent(cps: list[int], n: int, idx: int) -> int:
    j = idx + 1
    while j < n and _jtype(cps[j]) == "T":
        j += 1
    return j


def _collapse_allah(text: str) -> str:
    if ALLAH not in text:
        return text
    out: list[str] = []
    pos = 0
    idx = text.find(ALLAH)
    while idx >= 0:
        before = idx == 0 or not is_arabic_letter(ord(text[idx - 1]))
        after_i = idx + len(ALLAH)
        after = after_i >= len(text) or not is_arabic_letter(ord(text[after_i]))
        out.append(text[pos:idx])
        out.append(ALLAH_GLYPH if (before and after) else ALLAH)
        pos = after_i
        idx = text.find(ALLAH, pos)
    out.append(text[pos:])
    return "".join(out)


def shape(text: str, *, combine_allah: bool = False) -> str:
    """Contextual shaping only: logical Arabic -> presentation forms, same order.

    Handles initial/medial/final/isolated selection, lam-alef ligatures, and
    (optionally) the الله ligature. Does **not** reorder the text.
    """
    if not text:
        return text
    if combine_allah:
        text = _collapse_allah(text)
    cps = [ord(c) for c in text]
    n = len(cps)
    out: list[str] = []
    i = 0
    while i < n:
        cp = cps[i]
        jt = _jtype(cp)

        if cp == 0x0644:  # lam: maybe lam-alef ligature
            ni = _next_non_transparent(cps, n, i)
            if ni < n and cps[ni] in LAM_ALEF:
                pj = _prev_non_transparent(cps, i)
                prev_j = _jtype(cps[pj]) if pj >= 0 else "U"
                lam_joins_prev = prev_j in ("D", "C")
                iso, fin = LAM_ALEF[cps[ni]]
                out.append(chr(fin if lam_joins_prev else iso))
                for k in range(i + 1, ni):
                    out.append(chr(cps[k]))  # carry transparent marks
                i = ni + 1
                continue

        g = FORMS.get(cp)
        if g is None:
            out.append(chr(cp))
            i += 1
            continue

        _, iso, ini, med, fin = g
        pj = _prev_non_transparent(cps, i)
        nj = _next_non_transparent(cps, n, i)
        prev_t = _jtype(cps[pj]) if pj >= 0 else "U"
        next_t = _jtype(cps[nj]) if nj < n else "U"

        join_prev = jt in ("D", "R") and prev_t in ("D", "C")
        join_next = jt in ("D", "C") and next_t in ("D", "R", "C")

        if join_prev and join_next:
            form = med or fin or iso
        elif join_prev:
            form = fin or iso
        elif join_next:
            form = ini or iso
        else:
            form = iso
        out.append(chr(form))
        i += 1
    return "".join(out)


def _is_ltr(cp: int) -> bool:
    return (0x41 <= cp <= 0x5A) or (0x61 <= cp <= 0x7A) or (0xC0 <= cp <= 0x24F) or cp == 0x200E


def _is_digit(cp: int) -> bool:
    return (0x30 <= cp <= 0x39) or (0x0660 <= cp <= 0x0669) or (0x06F0 <= cp <= 0x06F9)


_LTR_GLUE = set(".@:/_-+%#&=?,")


def _is_ltr_glue(cp: int) -> bool:
    return chr(cp) in _LTR_GLUE


def _bidi_line(s: str, keep_ltr_runs: bool = True) -> str:
    n = len(s)
    rev = [ord(s[n - 1 - k]) for k in range(n)]
    out: list[str] = []
    i = 0
    while i < n:
        cp = rev[i]
        if keep_ltr_runs and (_is_ltr(cp) or _is_digit(cp)):
            j = i
            while j < n:
                c = rev[j]
                if _is_ltr(c) or _is_digit(c):
                    j += 1
                elif (c == 0x20 or _is_ltr_glue(c)) and j + 1 < n and (_is_ltr(rev[j + 1]) or _is_digit(rev[j + 1])):
                    j += 1
                else:
                    break
            for k in range(j - 1, i - 1, -1):
                out.append(chr(rev[k]))  # restore reading order
            i = j
        else:
            out.append(chr(cp))
            i += 1
    return "".join(out)


def _wrap_logical(line: str, max_line_chars: int):
    if max_line_chars <= 0 or len(line) <= max_line_chars:
        yield line
        return
    sb = ""
    for w in line.split(" "):
        if not w:
            continue
        if not sb:
            sb = w
        elif len(sb) + 1 + len(w) <= max_line_chars:
            sb += " " + w
        else:
            yield sb
            sb = w
    if sb:
        yield sb


def _process_line(line: str, o: Options) -> str:
    line = line.strip(" \t")
    if not line:
        return line
    if o.reverse_word_order:
        result = _bidi_line(shape(line, combine_allah=o.combine_allah), o.keep_ltr_runs).strip(" \t")
    else:
        parts = line.split(" ")
        parts = [
            _bidi_line(shape(p, combine_allah=o.combine_allah), o.keep_ltr_runs) if contains_arabic(p) else p
            for p in parts
        ]
        result = " ".join(parts)
    if o.prevent_word_split and o.word_joiner != " ":
        result = result.replace(" ", o.word_joiner)
    return result


def fix(text: str, opts: Options | None = None, **kwargs) -> str:
    """Bake logical Arabic into visual-order presentation forms.

    The result renders correctly even on clients that do **no** Arabic shaping
    or BiDi (the whole point for multiplayer / naive renderers). No-op when
    there is no Arabic, or when the text is already shaped.

    Pass an :class:`Options` instance or individual keyword overrides.
    """
    if not text:
        return text
    o = (opts or Options())
    if kwargs:
        o = Options(**{**o.__dict__, **kwargs})
    if not contains_arabic(text):
        return text
    if is_shaped(text):
        return text
    out_lines: list[str] = []
    for raw in text.replace("\r", "").split("\n"):
        for chunk in _wrap_logical(raw, o.max_line_chars):
            out_lines.append(_process_line(chunk, o))
    return "\n".join(out_lines)


# ---------------------------------------------------------------------------
# unfix helpers
# ---------------------------------------------------------------------------

def _dechar(ch: str) -> str:
    """Map one character from presentation form back to its logical base."""
    cp = ord(ch)
    if cp == 0xFDF2:                    # ﷲ -> الله
        return ALLAH
    la = lam_alef_inverse(cp)           # lam-alef ligature -> lam + alef
    if la is not None:
        return la
    base = to_base(cp)                  # any other presentation form -> base letter
    if base is not None:
        return chr(base)
    if cp == 0x00A0:                    # nbsp word-joiner -> space
        return " "
    return ch


def _is_arabic_cp(cp: int) -> bool:
    """True for any Arabic codepoint: base letters or presentation forms."""
    return (
        is_arabic_letter(cp)
        or 0xFB50 <= cp <= 0xFDFF
        or 0xFE70 <= cp <= 0xFEFF
    )


def _line_is_fully_shaped(line: str) -> bool:
    """True when every Arabic-containing token in *line* is in presentation form.

    A line produced by fix() has ALL Arabic words shaped + the whole line
    reversed, so unfix() must reverse the full line.

    A partially-shaped line (OCR artefact, mixed legacy source) has some words
    with presentation forms and some with raw base letters.  Reversing the full
    line would scramble the raw words, so we detect this and de-shape in place.
    """
    # Split on both regular space and nbsp (GAME preset uses nbsp as joiner)
    tokens = line.replace(" ", " ").split(" ")
    arabic_tokens = [
        t for t in tokens
        if any(_is_arabic_cp(ord(c)) for c in t)
    ]
    if not arabic_tokens:
        return True   # no Arabic — full-line path is safe (it's a no-op)
    return all(is_shaped(t) for t in arabic_tokens)


def unfix(text: str) -> str:
    """Reverse :func:`fix`: baked visual Arabic -> normal logical Arabic.

    Use this to recover readable Arabic for text-to-speech, search, logging,
    or any further processing. No-op on text that is not baked.

    Handles **partial shaping** (OCR / legacy sources where only some words
    carry presentation forms): shaped words are de-shaped in place without
    disturbing surrounding unshaped text.
    """
    if not text or not is_shaped(text):
        return text
    out_lines: list[str] = []
    for line in text.replace("\r", "").split("\n"):
        if _line_is_fully_shaped(line):
            # Fully baked (fix() output): reverse whole line then de-shape.
            logical = _bidi_line(line, keep_ltr_runs=True)
            out_lines.append("".join(_dechar(ch) for ch in logical))
        else:
            # Partially shaped: de-shape presentation forms in place, no reversal.
            out_lines.append("".join(_dechar(ch) for ch in line))
    return " ".join(ln.strip() for ln in out_lines).strip()
