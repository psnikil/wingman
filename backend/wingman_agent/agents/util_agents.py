from agents.prompts.deep_agent_prompts import DYNAMIC_DEEP_AGENT_SYS_PROMPT
from langchain_core.messages import SystemMessage
from langchain.agents import create_agent
from agents.prompts.agent_prompts import DYNAMIC_AGENT_SYS_PROMPT
from langchain_core.output_parsers import StrOutputParser
from agents.prompts.agent_prompts import PLANNER_DECOMPOSE_AGENT_SYS_PROMPT
from agents.agent_data_models import OrchDecompose
from langchain_core.prompts import ChatPromptTemplate
import os
from typing import Literal
from pydantic import BaseModel, Field
from services.llm_client.llm_client import LLMClient
from typing import Annotated, List, Union,Literal,Dict,Any

from langchain.agents.middleware import TodoListMiddleware, LLMToolSelectorMiddleware, ToolCallLimitMiddleware, ToolRetryMiddleware, ModelRetryMiddleware
from langchain.agents.middleware.tool_call_limit import ToolCallLimitState


from tools.file_tools import create_file,delete_file,write_file,rename_file, move_file,list_files,read_file
from tools.web_tools import web_search_tavily
from tools.cli_tools import execute_command
from tools.python_tools import run_python_code
from tools.os_tools import UbuntuOSTools




from dotenv import load_dotenv
load_dotenv()

class UtilAgents:

    decompose_llm =os.getenv("DECOMPOSE_LLM", 'gpt-oss:20b')
    generation_llm = os.getenv("ROUTER_LLM", 'llama3.1:8b')
    dynamic_agent_llm = os.getenv("DYNAMIC_AGENT_LLM", 'gpt-oss:20b')
    chat_llm = os.getenv("CHAT_LLM", 'gpt-oss:20b')
    tool_llm = os.getenv("TOOL_LLM", 'llama3.1:8b')

    def __init__(self,provider: Literal["ollama","openai","anthropic"],**values):
        self.llm_client = LLMClient()
        self.provider = provider
        self.language_model = os.getenv("DEFAULT_OLLAMA_MODEL", 'llama3.1:8b')
        super().__init__(**values)

        # TODO: update the system prompt to decompose the task based on the tools will be used
    def planner_decompose_llm_f(self, query: str, human_edit: List[str] | None = None, previous_generation: str | None = None) -> Union[OrchDecompose, Dict[str, Any]]:

        decompose_llm = self.llm_client.init_ollama(
            provider=self.provider,
            model=self.decompose_llm,
            temperature=0,
            reasoning=True
        )

        print('The prvious generation is: ', previous_generation)
        print('The human edit is: ', human_edit)
        print('The query is: ', query)
        
        
        structured_llm_decompose = decompose_llm.with_structured_output(OrchDecompose)

        system_prompt = PLANNER_DECOMPOSE_AGENT_SYS_PROMPT

        if human_edit and previous_generation:
            human_message = (
                "Original Query: {query}\n"
                "Previous Plan: {previous_generation}\n"
                "Human Feedback: {human_edit}\n"
                "Please update the plan based on the feedback."
            )
        else:
            human_message = "User query: {query}"

        decompose_prompt = ChatPromptTemplate.from_messages(
            [
                ('system',system_prompt),
                ('human',human_message),
            ]
        )

        question_decompose = decompose_prompt | structured_llm_decompose

        result = question_decompose.invoke({
            "query": query,
            "human_edit": human_edit,
            "previous_generation": previous_generation
        })

        return result

    def planner_generation_llm_f(self, context: str, final_goal: str, objectives: List[str]) -> str:
        generation_llm = self.llm_client.init_ollama(
            provider=self.provider,
            model=self.generation_llm,
            temperature=0,
            reasoning=True
        )
        # 1. Define the System Prompt with variables
        system_template = (
            "You are an expert {role}. Your goal is to {goal}. "
            "The output must be strictly in Markdown format with sections: Context, Objective, and Task."
        )
        # 2. Define the Human Prompt with variables
        human_template = ("Please convert the following data into a Markdown report:"
                        "\n\nContext: {context}"
                        "\n\nFinal Goal: {final_goal}"
                        "\n\nObjectives: {objectives}"
                        )
        # 3. Use SystemMessage and HumanMessage inside ChatPromptTemplate
        generation_prompt = ChatPromptTemplate.from_messages([
            ('system', system_template),
            ('human', human_template),
        ])
        # 4. Chain them together
        generation = generation_prompt | generation_llm | StrOutputParser()
        # 5. Pass parameters for BOTH messages via .invoke()
        answer = generation.invoke({
            "role": "task architect",                    # For SystemMessage
            "goal": "convert subtasks into a plan",      # For SystemMessage
            "context": context,                          # For HumanMessage
            "final_goal": final_goal,                    # For HumanMessage
            "objectives": objectives                     # For HumanMessage
        })
        return answer

    #  The input messages have to be formatted
    async def dynamic_agent_llm_f(self, messages):
        def get_deep_agent_tools():
            """Returns the list of tools available to the Deep Agent."""
            tools = [web_search_tavily,create_file,write_file,list_files,read_file,run_python_code,execute_command,UbuntuOSTools.open_browser,UbuntuOSTools.open_app,UbuntuOSTools.take_screenshot]
            return tools

        
        
        dynamic_agent_llm = self.llm_client.init_ollama(
            provider=self.provider,
            model=self.dynamic_agent_llm,
            temperature=0,
            streaming=False,
            num_ctx=64000,

        )
        tool_llm = self.llm_client.init_ollama(
            provider=self.provider,
            model="llama3.1:8b",
            temperature=0,
            num_ctx=64000,
        )
        os.makedirs(".artifacts", exist_ok=True)

        tools = get_deep_agent_tools()
        # print("the tools are ",tools)
        system_prompt = DYNAMIC_AGENT_SYS_PROMPT
        accumulated_tokens = []
        tool_calls = []

        # create_agent returns a CompiledStateGraph
        agent = create_agent(
            model=dynamic_agent_llm,
            tools=tools,
            system_prompt=SystemMessage(content=system_prompt),
            middleware=[
                LLMToolSelectorMiddleware(
                    model=tool_llm,
                    max_tools=3
                ),
                ToolCallLimitMiddleware(tool_name="web_search_tavily",thread_limit=10, run_limit=10, exit_behavior="end"),
                ToolRetryMiddleware(
                    max_retries=3,
                    backoff_factor=2.0,
                    initial_delay=1.0,
                ),
                ModelRetryMiddleware(
                    max_retries=2,
                ),
            ]
        )

        # Invoke the agent with the task
    # Stream events from the deep agent
        async for event in agent.astream_events(
            {"messages": messages},
            version="v2",
            # You can optionally narrow this:
            # include_names=["agent", "tools"],
            # include_types={"on_chat_model_stream", "on_tool_start", "on_tool_end"},
        ):
            etype = event["event"]

            # 1) LLM token streaming
            if etype == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    token = chunk.content
                    accumulated_tokens.append(token)

            # 2) Tool start
            elif etype == "on_tool_start":
                tool_name = event.get("name")
                tool_input = event["data"].get("input")
                tool_calls.append({"tool": tool_name, "input": tool_input})

            # 3) Tool end
            elif etype == "on_tool_end":
                tool_name = event.get("name")
                tool_output = event["data"].get("output")
        final_response = "".join(accumulated_tokens)
        
        # If streaming missed content, invoke once more
        if not final_response:
            final_state = await agent.ainvoke({"messages": messages})
            final_msg = final_state["messages"][-1]
            final_text = final_msg.content
        return final_response,tool_calls

    async def dynamic_deep_agent_llm_f(self, messages):
        
        def get_deep_agent_tools():
            """Returns the list of tools available to the Deep Agent."""
            tools = [web_search_tavily,run_python_code,UbuntuOSTools.open_browser,UbuntuOSTools.open_app,UbuntuOSTools.take_screenshot]
            return tools
        
        dynamic_agent_llm = self.llm_client.init_ollama(
            provider=self.provider,
            model=self.dynamic_agent_llm,
            temperature=0,
        )
        tool_llm = self.llm_client.init_ollama(
            provider=self.provider,
            model="llama3.1:8b",
            temperature=0,
        )
        os.makedirs(".artifacts", exist_ok=True)

        tools = get_deep_agent_tools()
        system_prompt = DYNAMIC_DEEP_AGENT_SYS_PROMPT
        accumulated_tokens = []
        tool_calls = []

        # create_agent returns a CompiledStateGraph
        agent = create_agent(
            model=dynamic_agent_llm,
            tools=tools,
            system_prompt=SystemMessage(content=system_prompt),
            middleware=[
                LLMToolSelectorMiddleware(
                    model=tool_llm,
                    max_tools=3
                ),
                ToolCallLimitMiddleware(tool_name="web_search_tavily",thread_limit=15, run_limit=15, exit_behavior="end"),
                ToolRetryMiddleware(
                    max_retries=3,
                    backoff_factor=2.0,
                    initial_delay=1.0,
                ),
                ModelRetryMiddleware(
                    max_retries=2,
                ),

            ]
        )

        # Invoke the agent with the task
    # Stream events from the deep agent
        async for event in agent.astream_events(
            {"messages": messages},
            version="v2",
            # You can optionally narrow this:
            # include_names=["agent", "tools"],
            # include_types={"on_chat_model_stream", "on_tool_start", "on_tool_end"},
        ):
            etype = event["event"]

            # 1) LLM token streaming
            if etype == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    token = chunk.content
                    accumulated_tokens.append(token)

            # 2) Tool start
            elif etype == "on_tool_start":
                tool_name = event.get("name")
                tool_input = event["data"].get("input")
                tool_calls.append({"tool": tool_name, "input": tool_input})

            # 3) Tool end
            elif etype == "on_tool_end":
                tool_name = event.get("name")
                tool_output = event["data"].get("output")
        final_response = "".join(accumulated_tokens)
        # final_response = event["data"].get("output")
        print(f"the event is {event}")

        
        # If streaming missed content, invoke once more
        if not final_response:
            final_state = await agent.ainvoke({"messages": messages})
            final_msg = final_state["messages"][-1]
            final_response = final_msg.content
        return final_response,tool_calls


    def chat_llm_f(self,query: str, context: str)-> str: 

        chat_llm = self.llm_client.init_ollama(
            provider=self.provider,
            model=self.chat_llm,
            temperature=0,
        )

        system_prompt = ("You are an {persona}. Your goal is {goal}."
                        "If there is no chat context, just chat with the user."
                        )
        if context:
            user_query ="Chat Context: {context}\nUserQuery: {query}"
        else:
            user_query ="UserQuery: {query}"
        
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", user_query)
            ]

        )

        chat_chain  =  (
                    prompt
                    | chat_llm
                    | StrOutputParser()
                    )
        answer = chat_chain.invoke({
            "persona": "polite and helpful assistant",
            "goal": "to chat with the user, if there is a question, answer it. Be polite and accurate",
            "context": context,
            "query": query
        })

        return answer
