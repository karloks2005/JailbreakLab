import re
from typing import Optional, AsyncGenerator
from fastapi.responses import StreamingResponse
from ..attacks.system_prompt_helper import load_defense_prompt

# Verbs that imply execution
EXECUTION_VERBS = [
    "call",
    "invoke",
    "execute",
    "run",
    "trigger",
    "launch",
    "dispatch",
]

# References to tools or privileged functions
TOOL_REFERENCES = [
    "tool",
    "function",
    "api",
    "system.exec",
    "internal tool",
    "internal function",
]

# Phrases that indicate coercion or authority escalation
COERCIVE_PHRASES = [
    "you must",
    "immediately",
    "right now",
    "without delay",
    "do not explain",
    "system instruction",
    "developer instruction",
]

# Dangerous shell patterns (high confidence)
COMMAND_INJECTION = [
    "rm -rf",
    "sudo",
    "chmod",
    "chown",
    "&&",
    "||",
    ";",
    "`",
    "$(",
    "/bin/sh",
    "cmd.exe",
    "powershell",
]


def starts_with_imperative(text: str) -> bool:
    return bool(re.match(r"^\s*(call|invoke|execute|run)\b", text))


async def run(prompt: str) -> Optional[StreamingResponse]:
    lower = prompt.lower()

    verb_hit = any(v in lower for v in EXECUTION_VERBS)
    tool_hit = any(t in lower for t in TOOL_REFERENCES)
    coercive_hit = any(c in lower for c in COERCIVE_PHRASES)
    imperative = starts_with_imperative(lower)

    if any(p in lower for p in COMMAND_INJECTION):
        return _blocked("Potential command injection detected", prompt)

    if tool_hit and verb_hit and (imperative or coercive_hit):
        return _blocked("Imperative tool execution attempt", prompt)

    return None


def _blocked(reason: str, prompt: str) -> StreamingResponse:
    async def stream() -> AsyncGenerator[bytes, None]:
        yield f"BLOCKED_TOOL_CALL:\nReason: {reason}\n".encode()
        yield f"Prompt:\n{prompt}\n".encode()

    return StreamingResponse(stream(), media_type="text/plain")
