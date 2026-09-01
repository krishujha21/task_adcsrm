"""
groq_client.py
--------------
Handles all communication with the Groq API.
Exposes a single function `query_groq` that sends a system + user prompt
pair to the specified model and returns the assistant's response as a string.
"""

from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def query_groq(
    system_prompt: str,
    user_prompt: str,
    model: str = "llama-3.3-70b-versatile",
) -> str:
    """Send a prompt pair to the Groq chat-completion endpoint.

    Args:
        system_prompt: The system-level instruction that sets the LLM's role.
        user_prompt: The user-facing message containing the code and context.
        model: Groq model identifier. Defaults to ``llama3-70b-8192``.

    Returns:
        The assistant's response text.

    Raises:
        RuntimeError: If the Groq API call fails for any reason.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=model,
            temperature=0.4,
            max_tokens=2048,
        )
        return chat_completion.choices[0].message.content
    except Exception as exc:
        raise RuntimeError(f"Groq API Error: {exc}") from exc
