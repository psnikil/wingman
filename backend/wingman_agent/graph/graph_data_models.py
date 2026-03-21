from langchain_core.messages import AnyMessage
from langchain_core.messages import HumanMessage
from typing import List, TypedDict, Literal, Annotated, Optional
from services.ollama_data_models import OrchDecompose
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages,MessagesState


class GraphState(MessagesState):
    """
    Represents the state of our graph.

    Attributes:
        query: query
        generation: LLM generation
        documents: list of documents
    """

    query:str
    context:str
    generation:str
    agent_data:OrchDecompose
    agent_objective:str
    completed_objectives:List[str]
    route_taken:List[str]
    human_edits:List[str]
    status:Literal["plan_ready","human-edit_no","human-edit_yes","error",None]
    agent_loops:int #debug variable

# Shared state across all nodes, with chat history from MessagesState
class ConversationState(MessagesState):
    """Shared state for planner + executor graph with streaming support."""
    workflow: Literal["custom_agent", "langchain_deep_agent","Retry"]
    final_goal: Optional[str]
    human_edits:Annotated[List[HumanMessage], add_messages]
    objectives: List[str]
    completed_objectives: List[str]
    current_objective: Optional[str]
    agent_context: Optional[str]
    answer: Optional[str]
    status:Literal["plan_ready","human-edit","error",None]
    context:str # check if you can use annotatate type

class ReActState(MessagesState):
    """
    State for the ReAct agent.
    """
    # messages: Annotated[List[BaseMessage], add_messages]
    context: str
    task: str
    objective: str
    previous_tasks: List[str]
    tasks_completed: List[str]
    iterations: int
    max_iterations: int

