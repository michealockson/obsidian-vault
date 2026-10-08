"""
Chunking for the ingestion pipeline (Phase 2).
Splits a note body on paragraph boundaries. A paragraph is only cut
(on sentences, then hard-sliced) if it alone exceeds max_chars.
"""

import re

# Rough size target: about 1500 tokens at roughly 4 characters per token.
# This is an estimate, not a measured value; tune it after real tests.
MAX_CHARS = 6000


def split_frontmatter(text):
    """Return (frontmatter, body). frontmatter is '' if there is none."""
    m = re.match(r"\A---\n(.*?)\n---\n?", text, re.DOTALL)
    if m:
        return m.group(1), text[m.end():]
    return "", text


def _split_long(par, max_chars):
    parts = []
    current = ""
    for sent in re.split(r"(?<=[.!?])\s+", par):
        while len(sent) > max_chars:
            if current:
                parts.append(current)
                current = ""
            parts.append(sent[:max_chars])
            sent = sent[max_chars:]
        if current and len(current) + 1 + len(sent) > max_chars:
            parts.append(current)
            current = sent
        else:
            current = f"{current} {sent}" if current else sent
    if current:
        parts.append(current)
    return parts


def chunk_text(body, max_chars=MAX_CHARS):
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    chunks = []
    current = ""
    for par in paragraphs:
        pieces = _split_long(par, max_chars) if len(par) > max_chars else [par]
        for piece in pieces:
            if current and len(current) + 2 + len(piece) > max_chars:
                chunks.append(current)
                current = piece
            else:
                current = f"{current}\n\n{piece}" if current else piece
    if current:
        chunks.append(current)
    return chunks


if __name__ == "__main__":
    import sys
    from pathlib import Path

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    chunks = chunk_text(body)
    print(f"frontmatter chars: {len(fm)}")
    print(f"chunks: {len(chunks)}")
    print(f"chunk sizes: {[len(c) for c in chunks]}")
