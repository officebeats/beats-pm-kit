import yaml
import os
from pathlib import Path
from rich.console import Console
from dotenv import load_dotenv

console = Console()

CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
PROFILE_PATH = CONFIG_DIR / "profile.yml"
ENV_PATH = CONFIG_DIR / ".env"

def load_config():
    """Load user profile and API keys for BYOK integration."""
    if not PROFILE_PATH.exists():
        return {}

    try:
        with open(PROFILE_PATH, "r") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        console.print(f"[bold red]Failed to load config: {e}[/bold red]")
        return {}

def get_active_model():
    """Retrieve the designated model from config."""
    config = load_config()
    model = config.get("model", "gemini/gemini-1.5-pro-002")
    
    # Load env vars
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)
        
    return model

if __name__ == "__main__":
    print(f"Active model: {get_active_model()}")
