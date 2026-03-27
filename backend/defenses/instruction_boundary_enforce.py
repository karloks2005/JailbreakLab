from typing import Optional, AsyncGenerator
from fastapi.responses import StreamingResponse
import re
from ..attacks.system_prompt_helper import load_defense_prompt

FORBIDDEN_STRUCTURES = [
    r"^system\s*:",
    r"^assistant\s*:",
    r"^developer\s*:",
    r"###\s*instruction",
    r"###\s*system",
    r"<\s*system\s*>",
    r"<\s*assistant\s*>",
]

async def run(prompt: str) -> Optional[StreamingResponse]:
    for pattern in FORBIDDEN_STRUCTURES:
        if re.search(pattern, prompt, flags=re.IGNORECASE | re.MULTILINE):
            return _blocked("Instruction boundary violation", prompt)
    return None

def _blocked(reason: str, prompt: str) -> StreamingResponse:
    async def stream() -> AsyncGenerator[bytes, None]:
        yield f"BLOCKED_STRUCTURE:\nReason: {reason}\n\n".encode()
        yield prompt.encode()
    return StreamingResponse(stream(), media_type="text/plain")
