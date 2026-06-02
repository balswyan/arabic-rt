# arabic-rt

**Arabic shaping, BiDi, and *un-baking* for games, TTS, and real-time clients.**

Most Arabic libraries can turn logical Arabic into correctly *shaped, right-to-left* text. `arabic-rt` does that too — but it also does the part almost nothing else does: it can **reverse** the process, turning baked presentation-form text back into clean logical Arabic. That round-trip is what makes Arabic work in places it normally breaks: multiplayer game chat, naive text renderers, and text-to-speech.

- 🔁 **Bake and un-bake.** `fix()` → renders correctly even on clients that do *zero* Arabic processing. `unfix()` → recovers logical Arabic for TTS, search, or logging.
- 🎮 **Built for real-time clients.** A `GAME` preset handles word-by-word chat readers (joins words so they aren't split, keeps the first words on top when wrapping).
- 🧩 **Zero dependencies.** Pure Python. Drop it in anywhere.
- ✅ **Validated.** Forward output matches `arabic_reshaper` + `python-bidi` byte-for-byte; `unfix(fix(x)) == x` is covered by tests.

> Pure shaping/BiDi is well served by existing tools. `arabic-rt`'s reason to exist is the **real-time / game** niche and the **un-baking** capability built for it.

## Install

```bash
pip install arabic-rt
```

## Quick start

```python
import arabic_rt as ar

baked = ar.fix("مرحبا بالعالم")     # visual-order presentation forms (renders anywhere)
ar.unfix(baked)                      # -> "مرحبا بالعالم"  (back to logical, for TTS/search)
ar.shape("سلم")                      # -> "ﺳﻠﻢ"  (contextual shaping only, no reorder)

ar.contains_arabic("hi مرحبا")       # True
ar.is_shaped(baked)                  # True
```

### Game chat (word-by-word readers)

```python
ar.fix("مرحبا بالعالم", ar.GAME)     # words joined so a naive reader shows the whole phrase
```

### Tune it yourself

```python
from arabic_rt import Options, fix

opts = Options(
    combine_allah=True,      # collapse الله -> ﷲ
    reverse_word_order=True, # full RTL line (False = shape per word, keep typed order)
    word_joiner="\u00A0",    # separator for naive word-by-word readers
    prevent_word_split=True,
    max_line_chars=18,       # wrap long lines ourselves (first words on top, each line RTL)
)
fix("نص عربي طويل", opts)
```

## Why "un-baking" matters

To make Arabic show up correctly on a client that does no shaping, you "bake" it into final presentation glyphs in visual (reversed) order. The catch: once baked, the text is no longer real Arabic letters — so a text-to-speech engine reads gibberish, and search/logging break. `unfix()` reverses the bake (presentation forms → base letters, ligatures expanded, order restored) so the *display* can stay baked while the *voice* and *data* see clean Arabic.

## API

| Function | Purpose |
| --- | --- |
| `fix(text, opts=None, **overrides)` | Logical Arabic → baked visual presentation forms. No-op on non-Arabic or already-shaped text. |
| `unfix(text)` | Baked Arabic → logical Arabic. No-op on text that isn't baked. |
| `shape(text, *, combine_allah=False)` | Contextual shaping only; order preserved. |
| `contains_arabic(text)` / `is_shaped(text)` | Fast checks. |
| `Options` / `GAME` | Config dataclass and a ready preset for game chat. |

## A note on display fonts

`arabic-rt` produces correct *text*; how it *looks* is your font's job. For rendering shaped Arabic (e.g. in the demo or a UI), a quality **Naskh** face such as **Noto Naskh Arabic** or **Amiri** (both SIL OFL) looks far better than a generic system font.

## Validation

Run the suite (installs the reference libraries as dev extras):

```bash
pip install -e ".[dev]"
pytest -q
```

## License & author

Licensed under the **Mozilla Public License 2.0 (MPL-2.0)** — see [`LICENSE`](LICENSE). Use it freely, including in closed-source games and apps; modifications to `arabic-rt`'s own files stay open.

Created by **Bandar AlSwyan** (AlCool).

---

<div dir="rtl" align="right">

<h2>عربي — نظرة سريعة</h2>

<p><b>arabic-rt</b> مكتبة لمعالجة النص العربي: تشكيل الحروف (وصلها بأشكالها الصحيحة)، وترتيبها من اليمين إلى اليسار، <b>والأهم</b> القدرة على عكس العملية — أي تحويل النص «المخبوز» (أشكال العرض المقلوبة) مرة أخرى إلى عربية منطقية سليمة.</p>

<p>هذه القدرة على «فك الخبز» (<code>unfix</code>) هي ما يجعل العربية تعمل في أماكن تتعطّل فيها عادةً: دردشة الألعاب الجماعية، والمحرّكات التي لا تعالج العربية، وأنظمة النطق (TTS). فالنص يظهر صحيحاً للجميع، بينما يقرأ محرّك الصوت أو البحث نسخة منطقية نظيفة.</p>

<ul>
<li><b>fix()</b>: عربية منطقية ← أشكال عرض جاهزة تظهر بشكل صحيح على أي عميل حتى بدون معالجة.</li>
<li><b>unfix()</b>: عكس العملية لاستعادة العربية المنطقية (للنطق والبحث والسجلات).</li>
<li><b>GAME</b>: إعداد جاهز لدردشة الألعاب التي تقرأ الكلمات واحدة تلو الأخرى.</li>
<li>بدون أي اعتماديات، ومُتحقَّق منها مقابل arabic_reshaper و python-bidi حرفاً بحرف.</li>
</ul>

<p>برخصة MPL-2.0. من إعداد <b>بندر الصويان</b>.</p>

</div>
