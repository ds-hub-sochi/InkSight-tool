import os
import uuid
from typing import Optional, Dict, Any, List
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

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

        # Initialize LangGraph memory system
        self.memory = MemorySaver()
        self.thread_id = uuid.uuid4()
        self.config = {"configurable": {"thread_id": self.thread_id}}
        
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
        
        # Create agent executor without deprecated memory parameter
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            max_execution_time=30,  # 30 second timeout
            callbacks=self.callbacks
        )
        
        # Create LangGraph workflow for memory management
        def call_agent(state: MessagesState):
            # Convert messages to input format
            if state["messages"]:
                input_text = state["messages"][-1].content
                try:
                    result = self.agent_executor.invoke({"input": input_text})
                    response = AIMessage(content=result.get("output", "I couldn't generate a response."))
                except Exception as e:
                    response = AIMessage(content=f"Agent error: {str(e)}")
            else:
                response = AIMessage(content="No input provided.")
            
            return {"messages": [response]}
        
        # Define the workflow
        self.workflow = StateGraph(state_schema=MessagesState)
        self.workflow.add_edge(START, "agent")
        self.workflow.add_node("agent", call_agent)
        
        # Compile with memory
        self.app = self.workflow.compile(checkpointer=self.memory)

    def chat(self, message: str, chat_history: str = "") -> str:
        """Process chat message and return response using LangGraph with memory."""
        try:
            input_message = HumanMessage(content=message)
            # Use the LangGraph app with memory management
            for event in self.app.stream({"messages": [input_message]}, self.config, stream_mode="values"):
                if event["messages"]:
                    last_message = event["messages"][-1]
                    if isinstance(last_message, AIMessage):
                        return last_message.content
            return "I couldn't generate a response."
        except Exception as e:
            # Fallback to direct agent executor
            try:
                result = self.agent_executor.invoke({"input": message})
                return result.get("output", "I couldn't generate a response.")
            except Exception as fallback_e:
                return f"Agent error: {str(fallback_e)}"

    def clear_memory(self) -> None:
        """Clear conversation memory by creating new thread."""
        # Create a new thread ID to effectively clear memory
        self.thread_id = uuid.uuid4()
        self.config = {"configurable": {"thread_id": self.thread_id}}
    
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
