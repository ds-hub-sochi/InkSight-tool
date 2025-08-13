import os
from typing import Optional
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager


def setup_tracing(
    langsmith_api_key: Optional[str] = None,
    langsmith_project: Optional[str] = None,
) -> list:
    """
    Set up tracing for LangChain calls using LangSmith.

    Args:
        langsmith_api_key: Optional LangSmith API key
        langsmith_project: Optional LangSmith project name

    Returns:
        A list of callback handlers
    """
    callbacks = []

    if langsmith_api_key:
        # Set environment variables for LangSmith
        os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        
        if langsmith_project:
            os.environ["LANGCHAIN_PROJECT"] = langsmith_project
            
        # Add LangSmith tracer
        callbacks.append(LangChainTracer(project_name=langsmith_project))
        print(f"✅ LangSmith tracing enabled for project: {langsmith_project}")

    return callbacks
