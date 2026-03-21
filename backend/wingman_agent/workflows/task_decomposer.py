import openai.types.beta.chatkit.chat_session_workflow_param
import os
from typing import Literal, Union
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from graph.graph_data_models import GraphState,ConversationState
from graph.nodes import Nodes
from graph.router import Router
from utils.logger import OrchestratorLogger

def create_graph(logger: OrchestratorLogger = None, provider: str = 'ollama'):
    # Initialize components
    node_handler = Nodes(provider=provider)
    router_handler = Router(logger=logger, provider=provider)

    # Define the graph
    workflow = StateGraph(ConversationState)

    # Add nodes
    workflow.add_node("decompose_query", node_handler.decompose_query)
    workflow.add_node("generation", node_handler.generation)
    workflow.add_node("more_info", node_handler.ask_more_info)
    workflow.add_node("human_approval", node_handler.human_approval)
    workflow.add_node("dynamic_agent", node_handler.dynamic_agent)
    workflow.add_node("langchain_deep_agent", node_handler.langchain_deep_agent)
    workflow.add_node("workflow_choice", node_handler.workflow_choice)
    workflow.add_node("chat", node_handler.chat)

    # Conditional edge for human approval
    def route_human_approval(state: ConversationState) -> Literal["generation", "decompose_query"]:
        if state["status"] == "plan_ready":
            return "generation"
        return "decompose_query"

    def workflow_choice(state: ConversationState) -> str:
        if state["workflow"] == "Retry":
            print('Please enter an correct choice')
            return "workflow_choice"
        elif state["workflow"] == "custom_agent":
            return "decompose_query"
        elif state["workflow"] == "langchain_deep_agent":
            return "langchain_deep_agent"
        print('Please enter an correct choice')
        return "workflow_choice"

    # route after select_objective: if no current_objective -> END; else -> executor
    def route_after_select(state: ConversationState) -> Literal["dynamic_agent", "__end__"]:
        if state.get("current_objective") is None:
            return "__end__"
        return "dynamic_agent"


    # Add edges
    workflow.add_conditional_edges(
    START,
    router_handler.chat_router,
    {
        "chat": "chat",
        "agentic": "workflow_choice"
    }
   )
    workflow.add_edge("chat", END)

    # Conditional edges from START using the router
    workflow.add_conditional_edges(
        "workflow_choice",
        workflow_choice,
        {
            "workflow_choice": "workflow_choice",
            "decompose_query": "decompose_query",
            "langchain_deep_agent": "langchain_deep_agent"
        }
    )
    workflow.add_edge("decompose_query", "human_approval")
    workflow.add_edge("generation", "dynamic_agent")
    workflow.add_edge("more_info", END)

    workflow.add_conditional_edges(
        "human_approval",
        route_human_approval,
        {
            "generation": "generation",
            "decompose_query": "decompose_query"
        }
    )

    workflow.add_conditional_edges(
        "dynamic_agent",
        lambda state: "agent" if len(state["completed_objectives"]) < len(state["objectives"]) else 'over',
        {
            "agent": "dynamic_agent",
            'over': END
        }
    )

    # Initialize memory saver
    memory = MemorySaver()

    # Compile the graph with memory
    app = workflow.compile(checkpointer=memory)
    
    # Print the graph
    print("\n--- Compiled Graph ---")
    try:
        app.get_graph().print_ascii()
    except Exception as e:
        print(f"Could not print ASCII graph: {e}")
    print("----------------------\n")
    
    return app
