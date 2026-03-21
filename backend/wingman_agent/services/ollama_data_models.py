from pydantic import BaseModel, Field
from typing import Annotated, List, Union, TypedDict,Literal


class OrchRouteQuery(BaseModel):
    """Orchestrator Router
    Route a user query to the most relevant Option out of the given:
        * more_info
        * decompose
    """

    route: Literal["more_info", "decompose"] = Field(
        ...,
        description="Decide whether to require more information based on the user query ('more_info'), or to 'decompose' if the query contains enough information to proceed with the task.",
    )

class EditFilesRouteQuery(BaseModel):
    """EditFiles Router
    Route a response from a plan creation agent to the most relevant Option out of the given:
        * edit_files
        * no_edit_files
    """

    route: Literal["edit_files", "no_edit_files"] = Field(
        ...,
        description="Decide whether to edit files based on the response from a plan creation agent ('edit_files'), or to 'no_edit_files' if the response does not require any file editing.",
    )

class OrchDecompose(BaseModel):
    """Orchestrator Decompose
    Decompose a user query into a list of objectives , inlclude the context and final goal"""

    query:str
    objectives:List[str]
    context:str
    final_goal:str

class ChatRouterQuery(BaseModel):
    """Chat Router
    Route a user query to the most relevant Option out of the given:
        * chat
        * agentic
    """

    route: Literal["chat", "agentic"] = Field(
        ...,
        description="""Decide whether to require more information based on the user query ('chat'), 
        or to 'agentic' if the query is not single shot and requires a plan to be created """,
    )