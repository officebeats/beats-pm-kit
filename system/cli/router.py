from litellm import completion
from config import get_active_model
import os

def execute_prompt(prompt: str) -> str:
    """Executes a prompt using litellm with BYOK config."""
    model = get_active_model()
    try:
        response = completion(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"\n[Error executing {model}]: {e}\nPlease check your API keys in config/.env"
