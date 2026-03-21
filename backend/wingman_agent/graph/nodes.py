from agents.researcher import DeepResearchAgent
from aiohttp.web_routedef import get
import json
from typing import Dict, Any, Literal
from graph.graph_data_models import GraphState, ReActState,ConversationState
from services.ollama_data_models import OrchDecompose
from services.ollama_client import OllamaClient
from langchain_core.messages import SystemMessage, BaseMessage,HumanMessage,AIMessage, get_buffer_string
import logging
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from agents.util_agents import UtilAgents

logger = logging.getLogger("graph.nodes")

class Nodes:
    def __init__(self, state: ConversationState | None = None, provider: str = 'ollama'):
        self.provider = provider
        self.agents = UtilAgents(self.provider)
        self.deep_researcher_agent = DeepResearchAgent(self.provider)
        self.state = state

    def chat(self, state: ConversationState) -> ConversationState:
        logger.info("--- ENTERING NODE: chat ---")
        user_query = state["messages"][-1].content
        chat_history = state["context"]
        answer = self.agents.chat_llm_f(user_query, chat_history)
        updated_context = get_buffer_string([HumanMessage(content=user_query), AIMessage(content=answer)])
        # state["messages"] = [HumanMessage(content=user_query), AIMessage(content=answer)]
        state['answer'] = answer
        state['context'] += updated_context

        logger.info("--- EXITING NODE: chat ---")
        return state


    # this node decpompoes the query and generates a plan
    def decompose_query(self, state: ConversationState) -> ConversationState:
        logger.info("--- ENTERING NODE: decompose_query ---")
        user_query = state["messages"][-1].content
        human_edit = state["human_edits"]
        previous_gen = "\n".join([gen.content for gen in state["messages"] if isinstance(gen, AIMessage)])
        str_human_edit = [i.content for i in human_edit]
        decompose = self.agents.planner_decompose_llm_f(
            query=user_query, 
            human_edit=str_human_edit, 
            previous_generation=previous_gen
        )

        agent_data = decompose.model_dump()

        state["final_goal"] = agent_data["final_goal"]
        state["objectives"] = agent_data["objectives"]
        state["completed_objectives"] = []
        state["current_objective"] = None
        
        # state["generation"] = json.dumps(decompose.model_dump())
        state["status"] = None
        logger.info("--- EXITING NODE: decompose_query ---")
        return state


    def generation(self,state:ConversationState)->ConversationState:
        logger.info("--- ENTERING NODE: generation ---")
        context = state["context"]
        final_goal = state["final_goal"]
        objectives = state["objectives"]

        answer = self.agents.planner_generation_llm_f(context, final_goal, objectives)

        state["answer"] = answer
        state["context"] += get_buffer_string([AIMessage(content=answer)])
        state["status"] = None
        logger.info("--- EXITING NODE: generation ---")
        return state

    # current does not do anything
    def ask_more_info(self, state: ConversationState) -> ConversationState:
        logger.info("--- ENTERING NODE: ask_more_info ---")
        print("\n[Assistant]: I need more information to process your request.")
        # TODO: find a better way than a brite force type cast
        if state["messages"][0].content == "":
            state["context"] = "\n [User Query]: " + str(state["messages"][-1].content)
        else:
            state["context"] += "\n [User Edit]: " + str(state["messages"][-1].content)
        logger.info("--- EXITING NODE: ask_more_info ---")
        return state

    def human_approval(self, state: ConversationState) -> ConversationState:
        
        logger.info("--- ENTERING NODE: human_approval ---")
        
        # Display the current decomposition
        try:
            print("\n--- Proposed Plan ---")

            print(f"Objective: {state['final_goal']}")
            print("Objectives:")
            for task in state['objectives']:
                print(f" - {task}")
            print(f"Context: {state['messages']}")
            print("----------------------")
        except Exception as e:
            print(f"\nError parsing plan for display: {e}")
            print(f"Raw Plan: {state['objectives']}")

        # Interrupt for human input
        # The value passed to resume() in the CLI will be returned here
        human_input = interrupt("Is this plan okay? (Type 'yes' to proceed, or provide edits)")
       
        
        if human_input.lower() == 'yes':
            state["status"] = "plan_ready"
        else:
            state["status"] = "human-edit"
            state["human_edits"] = [HumanMessage(content=human_input)]
            
        logger.info(f"--- HUMAN APPROVAL STATUS: {state['status']} ---")
        logger.info("--- EXITING NODE: human_approval ---")
        return state

    def workflow_choice(self, state: ConversationState) -> ConversationState:
        logger.info("--- ENTERING NODE: workflow_choice ---")

        logger.info("--- ENTERING NODE: Checking with human for workflow choice ---")
        print("\n The choices of workflows are: ")
        print("1. Custom planner agent")
        print("2. Langchain deep agent\n")
        human_input = interrupt("Choose either 1 or 2 for the choice of your workflow")
        print('your input is ', human_input)
        if human_input.lower() == '1':
            state["workflow"] = "custom_agent"
        elif human_input.lower() == '2':
            state["workflow"] = "langchain_deep_agent"
        else:
            state["workflow"] = "Retry"
        logger.info("--- EXITING NODE: workflow_choice ---")
        return state    


    def react_agent_node(self, state: ReActState, config: RunnableConfig) -> Dict[str, Any]:

        """
        Node for the ReAct agent to call the model.
        """
        logger.info("--- ENTERING NODE: react_agent_node ---")
        llm = config.get("configurable", {}).get("llm")
        system_prompt = config.get("configurable", {}).get("system_prompt")
        
        if not llm:
            raise ValueError("LLM not found in config. Ensure it's passed via configurable.")

        messages = state["messages"]
        if system_prompt:
            # Prepend custom system prompt if provided
            messages = [SystemMessage(content=system_prompt)] + messages
        
        response = llm.invoke(messages)
        
        logger.info("--- EXITING NODE: react_agent_node ---")
        return {
            "messages": [response],
            "iterations": state.get("iterations", 0) + 1
        }

    async def dynamic_agent(self, state: ConversationState, config: RunnableConfig) -> ConversationState:
        """
        Node for the dynamic agent to call the model.
        """
        logger.info("--- ENTERING NODE: dynamic_agent_node ---")

        
        final_goal = state["final_goal"]
        agent_context = state["agent_context"]
        completed_objectives = state["completed_objectives"]
        objective = state["objectives"][len(completed_objectives)]
        # state['agent_loops'] += 1

        # logger.info(f"--- Agent Loop: {state['agent_loops']} ---")
        logger.info(f"--- Objective: {objective} ---")
        
        print("\n Objective: ", objective)
        state['current_objective'] = objective
        # brute forcing the context
        # state["context"] += "\n [AI AGENT MESSAGE]: " + agent_context
        agent_query = f"""
            context: {agent_context}
            My objective is:{final_goal}
            Previous tasks completed: {completed_objectives}
            Current task: {objective}
            follow the system prompt and save the files related to the objective in ./data
            Do not forget to save progress of objects in ./.artificats/completion.md and notes/findings in ./.artificats/scratchpad.md
            """
        messages = [
            HumanMessage(content=agent_query)
        ]

        final_response,tool_calls = await self.agents.dynamic_agent_llm_f(
            messages=messages
        )
        print("\n Tool Calls: ", tool_calls)
        state["agent_context"] += get_buffer_string([AIMessage(content=final_response)])
        state["status"] = None
        state['completed_objectives'].append(objective)

        
        logger.info(f"--- Agent Response: {final_response} ---")
        logger.info("--- EXITING NODE: dynamic_agent_node ---")

        
        return state

    async def langchain_deep_agent(self, state: ConversationState, config: RunnableConfig) -> ConversationState:
        """
        Node for the langchain deep agent to call the model.
        """
        logger.info("--- ENTERING NODE: langchain_deep_agent_node ---")

        # always get the last message as the user query
        # TODO: always get the last human message as the user query
        user_query = state["messages"][-1].content
        context = state["context"]
        # state['agent_loops'] += 1

        print("\n Context: ", context)

        # logger.info(f"--- Agent Loop: {state['agent_loops']} ---")
        logger.info(f"--- Objective: {user_query} ---")
        
        print("\n Objective: ", user_query)
        # brute forcing the context
        # state["context"] += "\n [AI AGENT MESSAGE]: " + agent_context
        agent_query = f"""
            The users query is: {user_query}
            The context is: {context}
            follow the system prompt and save the files related to the objective in ./data
            Do not forget to save progress of objects in ./.artificats/completion.md and notes/findings in ./.artificats/scratchpad.md
            """
        messages = [
            HumanMessage(content=agent_query)
        ]

        final_response,tool_calls = await self.agents.dynamic_deep_agent_llm_f(
            messages=messages
        )
        print("\n Tool Calls: ", tool_calls)
        # state["messages"] = [HumanMessage(content=user_query), AIMessage(content=final_response)]
        state["context"] += "\n" + get_buffer_string([HumanMessage(content=user_query), AIMessage(content=final_response)])
        state["status"] = None
        # state['completed_objectives'].append(objective)

        
        logger.info(f"--- Agent Response: {final_response} ---")
        logger.info("--- EXITING NODE: langchain_deep_agent_node ---")

        
        return state

    def deep_research_agent(self, state: ConversationState, config: RunnableConfig) -> ConversationState:
        """
        Node for the deep research agent to call the model.
        """
        logger.info("--- ENTERING NODE: deep_research_agent_node ---")

        # always get the last message as the user query
        # TODO: always get the last human message as the user query
        user_query = state["messages"][-1].content
        context = state["context"]
        # state['agent_loops'] += 1

        print("\n Context: ", context)

        # logger.info(f"--- Agent Loop: {state['agent_loops']} ---")
        logger.info(f"--- Objective: {user_query} ---")
        
        print("\n Objective: ", user_query)
        # brute forcing the context
        # state["context"] += "\n [AI AGENT MESSAGE]: " + agent_context
        agent_query = f"""
            The users query is: {user_query}
            The context is: {context}
            follow the system prompt and save the files related to the objective in ./data
            Do not forget to save progress of objects in ./.artificats/completion.md and notes/findings in ./.artificats/scratchpad.md
            """
        messages = [
            HumanMessage(content=agent_query)
        ]

        answer = self.deep_researcher_agent.deep_researcher_llm_f(
            query=agent_query
        )
        # state["messages"] = [HumanMessage(content=user_query), AIMessage(content=final_response)]
        state["context"] += "\n" + get_buffer_string([HumanMessage(content=user_query), AIMessage(content=answer)])
        state["status"] = None
        # state['completed_objectives'].append(objective)

        
        logger.info(f"--- Agent Response: {answer} ---")
        logger.info("--- EXITING NODE: deep_research_agent_node ---")

        
        return state