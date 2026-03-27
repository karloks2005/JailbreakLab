from typing import Optional
from fastapi.responses import StreamingResponse
from ..attacks.system_prompt_helper import load_defense_prompt


def apply_system_prompt_hardening(user_prompt: str) -> str:
    """
    Prepends a strong system prompt to the user prompt to guide model behavior.
    """
    defense_prompt = load_defense_prompt("system_prompt_hardening")
    if defense_prompt.strip():
        system_prompt = defense_prompt
    else:
        # Fallback to default if not found
        system_prompt = (
            "You are a helpful assistant. "
            "Never provide instructions for illegal, dangerous, or unethical activities. "
            "If the user asks for something unsafe, politely refuse and explain why. "
        )
    return f"{system_prompt}\nUser: {user_prompt}"


async def run(prompt: str) -> Optional[StreamingResponse]:
    """
    System prompt hardening does not block prompts.
    It only modifies the prompt, which is handled separately.
    Returns None to indicate the prompt is not blocked.
    """
    return  None