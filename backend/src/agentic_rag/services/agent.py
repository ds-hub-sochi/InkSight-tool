import os
import uuid
from typing import Optional, Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from ..models.llm import ChatOpenRouter
from ..core.tracing import setup_tracing
from .retrieval import RetrievalService
from .prompts import MANUSCRIPT_ANALYSIS_SYSTEM_PROMPT



class AgenticChatBot:
    """Agentic chatbot with vector retrieval capabilities."""

    def __init__(
        self,
        model_name: str = "openai/gpt-4o",
        vector_store_path: str = "./vector_store",
        enable_reranker: bool = False,
        temperature: float = 0.1,
        max_tokens: int = 1500,
        langsmith_project: Optional[str] = None,
    ):
        """Initialize the agentic chatbot."""
        # Setup components
        self.llm = ChatOpenRouter(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )

        self.retrieval_service = RetrievalService(
            vector_store_path=vector_store_path,
            enable_reranker=enable_reranker
        )

        # Setup tracing
        self.callbacks = []
        if os.getenv("LANGCHAIN_API_KEY"):
            self.callbacks = setup_tracing(
                langsmith_api_key=os.getenv("LANGCHAIN_API_KEY"),
                langsmith_project=langsmith_project or os.getenv("LANGCHAIN_PROJECT"),
            )

        # Initialize LangGraph memory system
        self.memory = MemorySaver()
        self.thread_id = str(uuid.uuid4())
        self.config = {"configurable": {"thread_id": self.thread_id}}

        # Create tools
        self.tools = self._create_tools()

        # Create agent graph
        self.app = self._create_agent_graph()

    def _create_tools(self) -> List:
        """Create tools using modern @tool decorator."""

        @tool
        def search_knowledge(query: str) -> str:
            """Search ancient Arabic manuscripts from Uzbekistan for historical texts, religious content, scientific knowledge, cultural insights, and historical context from Central Asian manuscripts."""
            if not self.retrieval_service.is_store_ready():
                return "Ancient manuscripts knowledge base is not available."

            try:
                context = self.retrieval_service.get_context_string(
                    query=query, k=5, include_metadata=False
                )
                if context.strip():
                    return context.strip()
                else:
                    return "No relevant information found in the ancient Arabic manuscripts from Uzbekistan."
            except Exception as e:
                return f"Error searching ancient manuscripts database: {str(e)}"

        return [search_knowledge]

    def _create_agent_graph(self):
        """Create the agent graph using modern LangGraph patterns."""
        agent = create_react_agent(
            self.llm,
            self.tools,
            checkpointer=self.memory,
            prompt=MANUSCRIPT_ANALYSIS_SYSTEM_PROMPT
        )
        return agent

    def chat(self, message: str) -> str:
        """Process chat message and return response using LangGraph agent."""
        try:
            human_message = HumanMessage(content=message)

            response = self.app.invoke(
                {"messages": [human_message]},
                config=self.config
            )

            if response and "messages" in response:
                for msg in reversed(response["messages"]):
                    if isinstance(msg, AIMessage):
                        return msg.content

            return "I couldn't generate a response."

        except Exception as e:
            return f"Agent error: {str(e)}"

    def clear_memory(self) -> None:
        """Clear conversation memory by creating new thread."""
        self.thread_id = str(uuid.uuid4())
        self.config = {"configurable": {"thread_id": self.thread_id}}

    def get_knowledge_base_info(self) -> Dict[str, Any]:
        """Get knowledge base information."""
        return self.retrieval_service.get_store_info()

    def search_knowledge_base(self, query: str, k: int = 4) -> Dict[str, Any]:
        """Direct knowledge base search without agent."""
        if not self.retrieval_service.is_store_ready():
            return {"error": "Knowledge base not ready", "results": []}

        try:
            results = self.retrieval_service.retrieve_documents(query, k=k)
            content = [doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content for doc in results]
            return {
                "query": query,
                "results": [
                    {
                        "content": content,
                        "metadata": doc.metadata
                    }
                    for doc in results
                ]
            }
        except Exception as e:
            return {"error": str(e), "results": []}
