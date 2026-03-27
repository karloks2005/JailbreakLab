import re
import unicodedata
from typing import Optional, AsyncGenerator
from fastapi.responses import StreamingResponse
from ..attacks.system_prompt_helper import load_defense_prompt

ZERO_WIDTH = {
    "\u200b", "\u200c", "\u200d", "\u2060", "\ufeff"
}

DIRECTIONAL = {
    "\u202a", "\u202b", "\u202d", "\u202e", "\u202c"
}

def has_mixed_scripts(text: str) -> bool:
    scripts = set()

    for ch in text:
        if ch.isascii() or ch.isspace() or ch.isdigit():
            continue

        try:
            name = unicodedata.name(ch)
        except ValueError:
            continue

        if "LATIN" in name:
            scripts.add("LATIN")
        elif "CYRILLIC" in name:
            scripts.add("CYRILLIC")
        elif "GREEK" in name:
            scripts.add("GREEK")
        else:
            scripts.add("OTHER")

    return len(scripts) > 1
def has_format_unicode(text: str) -> bool:
    return any(unicodedata.category(ch) == "Cf" for ch in text)


async def run(prompt: str) -> Optional[StreamingResponse]:
    original = prompt
    if has_format_unicode(original):
        return _blocked("Invisible Unicode format characters detected", original)

    # 1️ Zero-width characters
    if any(ch in ZERO_WIDTH for ch in original):
        return _blocked("Zero-width Unicode characters detected", original)

    # 2️ Directional overrides
    if any(ch in DIRECTIONAL for ch in original):
        return _blocked("Unicode direction override detected", original)

    # 3️ Excessive combining marks
    combining = sum(
        1 for ch in original
        if unicodedata.combining(ch)
    )
    if combining > 3:
        return _blocked("Excessive Unicode combining characters", original)

    # 4️ Mixed scripts (REAL obfuscation)
    if has_mixed_scripts(original):
        return _blocked("Mixed Unicode scripts detected", original)

    return None


def _blocked(reason: str, prompt: str) -> StreamingResponse:
    async def stream() -> AsyncGenerator[bytes, None]:
        yield f"BLOCKED_UNICODE:\nReason: {reason}\n".encode()
        yield f"Prompt:\n{prompt}\n".encode()

    return StreamingResponse(stream(), media_type="text/plain")
