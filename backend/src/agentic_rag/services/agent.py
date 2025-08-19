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
            """Search ancient Arabic manuscripts from Uzbekistan. Finds information about historical texts, religious content, scientific knowledge, cultural insights, and historical context from medieval Central Asian manuscripts."""
            if not self.retrieval_service.is_store_ready():
                return "Ancient manuscripts knowledge base is not available."
            
            try:
                context = self.retrieval_service.get_context_string(
                    query=query, k=4, include_metadata=False
                )
                return context.strip() if context.strip() else "No relevant information found in the ancient Arabic manuscripts from Uzbekistan."
            except Exception as e:
                return f"Error searching ancient manuscripts database: {str(e)}"

        tools = [Tool(
            name="search_knowledge",
            description="Search ancient Arabic manuscripts from medieval Uzbekistan. Use this tool to find information about historical texts, religious and philosophical content, scientific knowledge, cultural practices, historical events, trade routes, daily life, and scholarly insights from Central Asian manuscripts. Particularly effective for questions about Islamic scholarship, Sufi texts, historical chronicles, scientific treatises, and cultural documents from medieval Uzbekistan.",
            func=search_knowledge,
        )]
        
        # Use standard ReAct prompt from hub with specialized context
        prompt = hub.pull("hwchase17/react")
        # Add specialized instruction for ancient manuscript analysis
        prompt.template = prompt.template + "\n\nYou are an expert in analyzing ancient Arabic manuscripts from medieval Uzbekistan and Central Asia. Provide detailed analysis focusing on:\n- Historical and cultural context of medieval Uzbekistan\n- Religious and philosophical content (Islamic scholarship, Sufism)\n- Scientific and mathematical knowledge preservation\n- Trade routes and economic insights\n- Daily life and social customs\n- Literary and poetic elements\n- Paleographic and codicological observations when relevant\n\nAlways contextualize findings within the broader framework of Islamic civilization and Central Asian history. Be scholarly but accessible in your explanations."
        
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
            search_keywords = ["what", "who", "when", "where", "how", "why", "manuscript", "text", "document", "religious", "historical", "cultural", "scientific", "arabic", "islamic", "uzbekistan", "central asia", "medieval"]
            should_search = any(keyword in message.lower() for keyword in search_keywords)
            
            if should_search and self.retrieval_service.is_store_ready():
                # Get context from knowledge base
                context = self.retrieval_service.get_context_string(message, k=3, include_metadata=False)
                
                if context.strip():
                    prompt = f"""Based on the following information from ancient Arabic manuscripts from medieval Uzbekistan and Central Asia, provide a detailed and scholarly analysis of the user's question. Focus on historical context, cultural significance, religious and philosophical content, and any scientific or literary insights.

Context from ancient manuscripts:
{context}

Question: {message}

Provide a comprehensive analysis that contextualizes the findings within the broader framework of Islamic civilization and Central Asian history:"""
                    # Use callbacks for tracing
                    config = {"callbacks": self.callbacks} if self.callbacks else {}
                    response = self.llm.invoke(prompt, config=config)
                    return response.content
                else:
                    return "I couldn't find relevant information in the ancient Arabic manuscripts database for your question. Please try rephrasing your question or asking about specific aspects of medieval Uzbekistan manuscripts, Islamic scholarship, or Central Asian history."
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
