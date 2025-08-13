import os
from typing import Optional, Dict, Any
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.memory import ConversationBufferWindowMemory

from ..models.llm import ChatOpenRouter
from ..core.tracing import setup_tracing
from .retrieval import RetrievalService


class AgenticChatBot:
    """Agentic chatbot with vector retrieval capabilities."""

    def __init__(
        self,
        model_name: str = "openai/gpt-4o-mini",
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

        # Add memory for conversation history
        self.memory = ConversationBufferWindowMemory(
            k=5,  # Keep last 5 exchanges
            memory_key="chat_history",
            return_messages=True
        )

        # Create agent
        self._create_agent()

    def _create_agent(self) -> None:
        """Create the ReAct agent using standard pattern."""
        # Create tools
        def search_knowledge(query: str) -> str:
            """Поиск в базе знаний русской литературы и истории. Ищет информацию о произведениях, персонажах, сюжетах, исторических событиях и культурном контексте."""
            if not self.retrieval_service.is_store_ready():
                return "База знаний русской литературы недоступна."
            
            try:
                context = self.retrieval_service.get_context_string(
                    query=query, k=4, include_metadata=False
                )
                return context.strip() if context.strip() else "Не найдено релевантной информации о русской литературе или истории."
            except Exception as e:
                return f"Ошибка поиска в литературной базе: {str(e)}"

        tools = [Tool(
            name="search_knowledge",
            description="Поиск в базе знаний русской литературы и истории. Используй этот инструмент для поиска информации о произведениях русских писателей, персонажах, сюжетах, исторических событиях, культурном контексте эпохи. Особенно эффективен для вопросов о Пушкине, Толстом, Достоевском и других классиках.",
            func=search_knowledge,
        )]
        
        # Use standard ReAct prompt from hub with Russian context
        prompt = hub.pull("hwchase17/react")
        # Add Russian instruction to the prompt
        prompt.template = prompt.template + "\n\nОтвечайте на русском языке, особенно при анализе русской литературы и истории. Provide detailed analysis focusing on literary techniques, historical context, and cultural significance."
        
        # Create agent
        agent = create_react_agent(self.llm, tools, prompt)
        
        # Create agent executor with memory
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            max_execution_time=30,  # 30 second timeout
            callbacks=self.callbacks
        )

    def chat(self, message: str, chat_history: str = "") -> str:
        """Process chat message and return response."""
        try:
            # Use the ReAct agent with automatic memory management
            result = self.agent_executor.invoke({"input": message})
            return result.get("output", "I couldn't generate a response.")
        except Exception as e:
            # Only fallback on actual errors, not timeouts
            return f"Agent error: {str(e)}"

    def clear_memory(self) -> None:
        """Clear conversation memory."""
        self.memory.clear()
    
    def _fallback_response(self, message: str) -> str:
        """Fallback method using direct search + LLM."""
        try:
            # Check if we should search
            search_keywords = ["what", "who", "when", "where", "how", "why", "story", "stories", "document", "book", "text", "tell", "about"]
            should_search = any(keyword in message.lower() for keyword in search_keywords)
            
            if should_search and self.retrieval_service.is_store_ready():
                # Get context from knowledge base
                context = self.retrieval_service.get_context_string(message, k=3, include_metadata=False)
                
                if context.strip():
                    prompt = f"""На основе следующей информации из документов русской литературы и истории, ответь на вопрос пользователя ясно и подробно. Сосредоточься на литературном анализе, историческом контексте и культурном значении.

Контекст из русской литературы:
{context}

Вопрос: {message}

Ответ на русском языке:"""
                    # Use callbacks for tracing
                    config = {"callbacks": self.callbacks} if self.callbacks else {}
                    response = self.llm.invoke(prompt, config=config)
                    return response.content
                else:
                    return "Не удалось найти релевантную информацию в базе знаний русской литературы для вашего вопроса. Попробуйте переформулировать запрос или задать вопрос о конкретном произведении или авторе."
            else:
                # Direct LLM response with tracing
                config = {"callbacks": self.callbacks} if self.callbacks else {}
                response = self.llm.invoke(message, config=config)
                return response.content
                
        except Exception as e:
            return f"I encountered an error: {str(e)}"

    def get_knowledge_base_info(self) -> Dict[str, Any]:
        """Get knowledge base information."""
        return self.retrieval_service.get_store_info()

    def search_knowledge_base(self, query: str, k: int = 4) -> Dict[str, Any]:
        """Direct knowledge base search without agent."""
        if not self.retrieval_service.is_store_ready():
            return {"error": "Knowledge base not ready", "results": []}

        try:
            results = self.retrieval_service.retrieve_documents(query, k=k)
            return {
                "query": query,
                "results": [
                    {
                        "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in results
                ]
            }
        except Exception as e:
            return {"error": str(e), "results": []}
