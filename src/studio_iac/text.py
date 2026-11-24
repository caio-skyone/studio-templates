"""Plain text for the prose fields the Studio renders literally.

`description` is not parsed anywhere in the Studio UI: `**bold**` shows the
asterisks, `&quot;` shows the entity, `<br>` shows the tag. Markup in a
description is therefore always a defect — it is never rendered, only read.

`plain_text` sweeps text coming FROM a spec, before it reaches the worklist.
`has_markup` detects markup in text going TO the Studio, whatever wrote it.

The tag list is closed on purpose. A generic `<[^>]+>` would eat the IAC
parameter reference `<>name</>` and leave a dangling ref behind. The unescape
comes FIRST, before the tag strip: `&lt;p&gt;` is a tag the spec escaped, and
decoding it last would leave it standing in a sanitizer's output.
"""

import html
import re

_TAGS = "a|b|i|p|br|em|strong|code|pre|ul|ol|li|div|span|h[1-6]|table|tr|td|th|img"
_BLOCK_BREAK_RE = re.compile(r"(?i)</(?:p|div|li|ul|ol|tr|h[1-6])>|<br\s*/?>")
_TAG_RE = re.compile(rf"(?i)</?(?:{_TAGS})(?:\s[^<>]*)?/?>")
_MD_LINK_RE = re.compile(r"\[([^\]\n]+)\]\([^)\s]+(?:\s+\"[^\"]*\")?\)")
_MD_HEADING_RE = re.compile(r"(?m)^\s{0,3}#{1,6}\s+")
# Itálico exige borda de palavra dos dois lados: sem isso `2 * 3` e o curinga
# `a*b` de um parâmetro de filtro perdem os asteriscos, que são literais.
_MD_ITALIC_RE = re.compile(r"(?<![\w*])\*(\S|\S[^*\n]*\S)\*(?![\w*])")
_WHITESPACE_RE = re.compile(r"\s+")
_SEPARATOR_RE = re.compile(r"(?:\s*;\s*)+")

_MARKUP_RE = re.compile(
    r"(?i)&(?:[a-z]+|#\d+);"
    rf"|</?(?:{_TAGS})(?:\s[^<>]*)?/?>"
    r"|\*\*[^*\n]+\*\*"
    r"|`[^`\n]+`"
    r"|\[[^\]\n]+\]\([^)\s]+\)"
    r"|(?m:^\s{0,3}#{1,6}\s+\S)"
)


def plain_text(value: object) -> str:
    """Spec text with its markup flattened into prose. Empty when there is none."""
    if not isinstance(value, str) or not value.strip():
        return ""
    # Unescape ANTES do strip: `&lt;p&gt;` é uma tag que o spec escapou, e
    # desescapar por último a deixaria de pé na saída de um sanitizador.
    text = html.unescape(value)
    text = _BLOCK_BREAK_RE.sub(" ; ", text)
    text = _TAG_RE.sub("", text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _MD_HEADING_RE.sub("", text)
    text = text.replace("**", "").replace("`", "")
    text = _MD_ITALIC_RE.sub(r"\1", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    text = _SEPARATOR_RE.sub("; ", text)
    return text.strip("; ").strip()


def has_markup(value: object) -> bool:
    """True when the text carries markup the Studio would show as characters."""
    if not isinstance(value, str) or not value:
        return False
    return _MARKUP_RE.search(value) is not None
