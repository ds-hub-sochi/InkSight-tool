import os
from typing import Optional
from dotenv import load_dotenv
from langchain_core.utils.utils import secret_from_env
from langchain_openai import ChatOpenAI
from pydantic import Field, SecretStr

load_dotenv()


class ChatOpenRouter(ChatOpenAI):
    """Custom ChatOpenAI class for OpenRouter API integration."""

    openai_api_key: Optional[SecretStr] = Field(
        alias="api_key",
        default_factory=secret_from_env("OPENROUTER_API_KEY", default=None),
    )

    @property
    def lc_secrets(self) -> dict[str, str]:
        return {"openai_api_key": "OPENROUTER_API_KEY"}

    def __init__(
        self,
        model_name: str,
        openai_api_key: Optional[str] = None,
        openai_api_base: str = "https://openrouter.ai/api/v1",
        max_retries: int = 3,
        **kwargs,
    ):
        """Initialize the ChatOpenRouter with OpenRouter API settings.

        Args:
            model_name: Name of the model to use
            openai_api_key: Optional API key (will use env var if not provided)
            openai_api_base: Base URL for the OpenRouter API
            max_retries: Maximum number of retries for failed requests (default: 3)
            **kwargs: Additional arguments to pass to ChatOpenAI
        """
        openai_api_key = openai_api_key or os.environ.get("OPENROUTER_API_KEY")
        super().__init__(
            base_url=openai_api_base,
            openai_api_key=openai_api_key,
            model_name=model_name,
            max_retries=max_retries,
            **kwargs,
        )
