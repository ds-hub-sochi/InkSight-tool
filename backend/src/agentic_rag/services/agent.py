import os
from typing import List, Optional, Dict, Any
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage

from ..models.llm import ChatOpenRouter
from ..core.tracing import setup_tracing
from .retrieval import RetrievalService


class AgenticChatBot:
    """Agentic chatbot with vector retrieval capabilities."""

    def __init__(
        self,
        model_name: str = "anthropic/claude-3.5-sonnet",
        vector_store_path: str = "./vector_store",
        enable_reranker: bool = False,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        memory_window: int = 10,
        langsmith_project: Optional[str] = None,
    ):
        """Initialize the agentic chatbot.

        Args:
            model_name: OpenRouter model to use
            vector_store_path: Path to vector store
            enable_reranker: Enable semantic reranking
            temperature: LLM temperature
            max_tokens: Maximum tokens for responses
            memory_window: Conversation memory window size
            langsmith_project: LangSmith project name for tracing
        """
        # Set up tracing
        self.callbacks = setup_tracing(
            langsmith_api_key=os.getenv("LANGCHAIN_API_KEY"),
            langsmith_project=langsmith_project or os.getenv("LANGCHAIN_PROJECT"),
        )

        # Initialize LLM
        self.llm = ChatOpenRouter(
            model_name=model_name, temperature=temperature, max_tokens=max_tokens
        )

        # Initialize retrieval service
        self.retrieval_service = RetrievalService(
            vector_store_path=vector_store_path, enable_reranker=enable_reranker
        )

        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            k=memory_window, return_messages=True, memory_key="chat_history"
        )

        # Create tools and agent
        self._create_tools()
        self._create_agent()

    def _create_tools(self) -> None:
        """Create tools for the agent."""

        def vector_search_tool(query: str) -> str:
            """Search the knowledge base for relevant information."""
            if not self.retrieval_service.is_store_ready():
                return "Knowledge base is not available. Please ensure documents have been processed."

            context = self.retrieval_service.get_context_string(
                query=query, k=4, include_metadata=True
            )

            if not context.strip():
                return "No relevant information found in the knowledge base."

            return f"Retrieved context:\n{context}"

        self.tools = [
            Tool(
                name="knowledge_search",
                description="Search the knowledge base for relevant information. Use this when the user asks questions that might be answered by the stored documents.",
                func=vector_search_tool,
            )
        ]

    def _create_agent(self) -> None:
        """Create the ReAct agent."""

        # Create the prompt template
        template = """You are a helpful AI assistant with access to a knowledge base. 
You can search the knowledge base to find relevant information to answer user questions.

TOOLS:
------
You have access to the following tools:
{tools}

To use a tool, please use the following format:
```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:
```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Previous conversation:
{chat_history}

Question: {input}
{agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)

        # Create the agent
        agent = create_react_agent(llm=self.llm, tools=self.tools, prompt=prompt)

        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            callbacks=self.callbacks,
        )

    def chat(self, message: str) -> str:
        """Send a message to the chatbot and get a response.

        Args:
            message: User message

        Returns:
            Chatbot response
        """
        try:
            response = self.agent_executor.invoke({"input": message})
            return response.get("output", "I'm sorry, I couldn't generate a response.")
        except Exception as e:
            return f"Error: {str(e)}"

    def clear_memory(self) -> None:
        """Clear the conversation memory."""
        self.memory.clear()

    def get_memory_messages(self) -> List[BaseMessage]:
        """Get the current conversation memory."""
        return self.memory.chat_memory.messages

    def add_user_message(self, message: str) -> None:
        """Add a user message to memory without generating response."""
        self.memory.chat_memory.add_user_message(message)

    def add_context_to_memory(self, context: str, source: str = "system") -> None:
        """Add context information to memory."""
        self.memory.chat_memory.add_message(
            {"role": "system", "content": f"Context from {source}: {context}"}
        )

    def get_knowledge_base_info(self) -> Dict[str, Any]:
        """Get information about the knowledge base."""
        return self.retrieval_service.get_store_info()

    def search_knowledge_base(
        self, query: str, k: int = 4, include_scores: bool = False
    ) -> Dict[str, Any]:
        """Search the knowledge base directly.

        Args:
            query: Search query
            k: Number of results
            include_scores: Whether to include similarity scores

        Returns:
            Search results
        """
        if not self.retrieval_service.is_store_ready():
            return {"error": "Knowledge base not ready"}

        if include_scores:
            results = self.retrieval_service.retrieve_with_scores(query, k=k)
            return {
                "query": query,
                "results": [
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": score,
                    }
                    for doc, score in results
                ],
            }
        else:
            results = self.retrieval_service.retrieve_documents(query, k=k)
            return {
                "query": query,
                "results": [
                    {"content": doc.page_content, "metadata": doc.metadata}
                    for doc in results
                ],
            }
