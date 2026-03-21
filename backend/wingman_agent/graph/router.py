from typing import  Literal, Optional

from graph.graph_data_models import ReActState, ConversationState
import logging


from agents.router_agents import RouterAgents
from utils.logger import OrchestratorLogger

logger = logging.getLogger("graph.router")

# Routers should never modify the state
class Router:
    def __init__(self, logger: Optional[OrchestratorLogger] = None, provider: str = 'ollama'):

        self.router_agents = RouterAgents(provider=provider)
        self.orchestrator_logger = logger

    def router(self, state: ConversationState) -> str:
        logger.info("--- ENTERING ROUTER ---")
        print("the state messages are ", state["messages"])
        query = state["messages"][-1].content

        print(f"The router input query: {query}")

        route = self.router_agents.planner_router_llm_f(query, state["context"])

        # if "route_taken" not in state or state["route_taken"] is None:
        #     state["route_taken"] = []
        
        # state["route_taken"].append(route.route)
        
        if self.orchestrator_logger:
            self.orchestrator_logger.log_state("ROUTER", state, is_router=True)
            
        logger.info(f"--- ROUTER DECISION: {route.route} ---")
        return route.route

    def react_agent_router(self, state: ReActState) -> Literal["tools", "__end__"]:
        """
        Conditional router for the ReAct agent.
        """
        logger.info("--- ENTERING ROUTER: react_agent_router ---")
        messages = state["messages"]
        last_message = messages[-1]
        
        if state.get("iterations", 0) >= state.get("max_iterations", 10):
            logger.info("--- ROUTER DECISION: max iterations reached ---")
            return "__end__"
            
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            logger.info("--- ROUTER DECISION: tools ---")
            return "tools"
            
        logger.info("--- ROUTER DECISION: end ---")
        return "__end__"

    def edit_files_router(self, state: ConversationState) -> str:
        logger.info("--- ENTERING EDIT FILES ROUTER ---")
        query = f"""
        User query: {state["messages"][0].content}
        Agent context: {state["agent_context"]}
        Agent final goal: {state["final_goal"]}
        Agent objectives: {state["objectives"]}
        """

        print(f"The edit files router input query: {query}")

        route = self.router_agents.edit_files_router_llm_f(query)
        
        if self.orchestrator_logger:
            self.orchestrator_logger.log_state("EDIT FILES ROUTER", state, is_router=True)
            
        logger.info(f"--- EDIT FILES ROUTER DECISION: {route.route} ---")
        return route.route

    def chat_router(self, state: ConversationState) -> str:
        logger.info("--- ENTERING CHAT ROUTER ---")
        user_query = state["messages"][-1].content
        chat_history = state["context"]

        route = self.router_agents.chat_router_llm_f(user_query, chat_history)
        
        if self.orchestrator_logger:
            self.orchestrator_logger.log_state("CHAT ROUTER", state, is_router=True)
            
        logger.info(f"--- CHAT ROUTER DECISION: {route.route} ---")
        return route.route