"""Central configuration for InsightAgent."""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    chat_model: str = os.getenv("CHAT_MODEL", "gpt-4o-mini")
    temperature: float = float(os.getenv("TEMPERATURE", "0.2"))
    max_steps: int = int(os.getenv("MAX_STEPS", "8"))


settings = Settings()


def validate() -> None:
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your OpenAI API key."
        )
