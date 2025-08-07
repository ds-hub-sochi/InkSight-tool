import os
from typing import Optional
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager


def setup_tracing(
    langsmith_api_key: Optional[str] = None,
    langsmith_project: Optional[str] = None,
) -> Optional[CallbackManager]:
    """
    Set up tracing for LangChain calls using LangSmith.

    Args:
        langsmith_api_key: Optional LangSmith API key
        langsmith_project: Optional LangSmith project name

    Returns:
        A CallbackManager instance configured with tracers or None
    """
    callbacks = []

    if langsmith_api_key:
        os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
        if langsmith_project:
            os.environ["LANGCHAIN_PROJECT"] = langsmith_project
        callbacks.append(LangChainTracer())
        return CallbackManager(callbacks)

    return None
