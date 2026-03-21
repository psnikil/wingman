import IPython.core.debugger_backport
from deepagents.middleware.summarization import SummarizationMiddleware
from deepagents import create_deep_agent
from services.llm_client.llm_client import LLMClient
import os
import shutil
from typing import Optional, Literal
from langchain.tools import tool
from datetime import datetime
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Literal, List
from langchain_core.messages import SystemMessage, HumanMessage,AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.documents import Document
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_agent
from tools.file_tools import create_file, delete_file, write_file, rename_file, move_file, list_files
from tools.web_tools import web_search_duckduckgo, web_search_tavily
import os
from deepagents.backends import FilesystemBackend
from langchain_tavily import TavilySearch
from langchain.chat_models import init_chat_model
from langchain.agents.middleware import TodoListMiddleware, LLMToolSelectorMiddleware, ToolCallLimitMiddleware, ToolRetryMiddleware, ModelRetryMiddleware
from rag.middleware import RAGToolSelectorMiddleware
from agents.prompts.researcher_prompts import (
    RESEARCHER_INSTRUCTIONS,
    RESEARCH_WORKFLOW_INSTRUCTIONS,
    SUBAGENT_DELEGATION_INSTRUCTIONS,
)
from tools.think_tools import think_tool

from dotenv import load_dotenv
load_dotenv()

class DeepResearchAgent:
    
    researcher_llm: str = os.getenv("DEEP_RESEARCHER_LLM", 'gpt-oss:20b')
    generation_llm: str = os.getenv("ROUTER_LLM", 'llama3.1:8b')
    tool_llm: str = os.getenv("TOOL_LLM", 'llama3.1:8b')

    def __init__(self,provider: Literal["ollama","openai","anthropic"],**values):
        self.llm_client = LLMClient()
        self.provider = provider
        self.language_model = os.getenv("DEFAULT_OLLAMA_MODEL", 'llama3.1:8b')
        self.max_concurrent_research_units = 3
        self.max_researcher_iterations = 3
        # Get current date
        self.current_date = datetime.now().strftime("%Y-%m-%d")

        super().__init__(**values)

    def deep_researcher_llm_f(self, query: str, context: Optional[str] = None):

        researcher_llm = self.llm_client.init_ollama(
            model=self.researcher_llm,
            temperature=0,
            reasoning=True,
            num_ctx=96000
        )
        tavily_search = TavilySearch(include_raw_content=True,max_results=5,search_depth="basic")

        tool_llm = self.llm_client.init_ollama(
            model=self.tool_llm,
            temperature=0,
            reasoning=None,
            num_ctx=48000
        )

        system_prompt = (
            RESEARCH_WORKFLOW_INSTRUCTIONS
            + "\n\n"
            + "=" * 80
            + "\n\n"
            + SUBAGENT_DELEGATION_INSTRUCTIONS.format(
                max_concurrent_research_units=self.max_concurrent_research_units,
                max_researcher_iterations=self.max_researcher_iterations,
            )
        )

        # Create research sub-agent
        research_sub_agent = {
            "name": "research-agent",
            "description": "Delegate research to the sub-agent researcher. Only give this researcher one topic at a time.",
            "system_prompt": RESEARCHER_INSTRUCTIONS.format(date=self.current_date),
            "tools": [tavily_search, think_tool],
        }
        root = os.path.abspath("./")
        print(f'the root dir is {root}')
        # Create the agent
        agent = create_deep_agent(
            model=researcher_llm,
            system_prompt=system_prompt,
            tools=[tavily_search, think_tool],
            subagents=[research_sub_agent],
            backend=FilesystemBackend(
                root_dir=root,
                virtual_mode=True
            ),
            middleware=[
                # RAGToolSelectorMiddleware(
                # LLMToolSelectorMiddleware(
                #     model=tool_llm,
                #     max_tools=5,
                # ),
                ToolCallLimitMiddleware(tool_name="tavily_search",thread_limit=15, run_limit=15, exit_behavior="end"),
                ToolRetryMiddleware(
                    max_retries=3,
                    backoff_factor=2.0,
                    initial_delay=1.0,
                ),
                ModelRetryMiddleware(
                    max_retries=2,
                ),
            ],
        )
        
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": query,
                    }
                ],
            }, 
        )
        return result


@tool(parse_docstring = True)
def web_research_agent(query: str, context: Optional[str] = None):
    """
    Spawns a specialized web research agent to search the web, collect ideas in a scratchpad,
    and draft a comprehensive report or article based on the findings.
    
    Args:
        query (str): The research query or topic.
        context (Optional[str]): Background context or previous conversation history.
    """
    

    llm = ChatOllama(
        model=os.getenv("SUBAGENT_OLLAMA_MODEL", "llama3.1:8b"),
        temperature=0.3,
    )
    
    os.makedirs(".artifacts", exist_ok=True)
    
    system_prompt = f"""
    Background Information: {context}

    You are a specialized Web Research Agent. Your goal is to gather information and build a comprehensive research scratchpad at `.artifacts/scratchpad.md` before providing a final answer.

    ### MANDATORY WORKFLOW run for 3 iterations:
    1. **Search**: Call `web_search_duckduckgo(query=...)`.
    2. **Collect**: Review search results and call `create_file` or `modify_file` to save your findings.
       - **Tool Arguments**: Use `file_path=".artifacts/scratchpad.md"` and `content="..."`.
       - **NO EMPTY CONTENT**: You MUST have actual research findings to write.
    3. **Finalize**: Provide the final synthesis as a report.

    ### RULES:
    - NEVER call multiple tools in one turn.
    - NEVER use an empty string for content.
    ### DETAIL LEVELS (Default to 2):
    If the user specifies a detail level or if one is inferred, use the following scale:
    - **Level 1**: A concise summary of the key findings.
    - **Level 2 (Default)**: A well-structured report with short details for each key point.
    - **Level 3**: A comprehensive, one-page article discussing each key point thoroughly.

    """

    tools = [TavilySearch,create_file,write_file,think_tool]    
    
    web_researcher = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )
    
    print(f"Executing web research agent for: {query}")
    result = web_researcher.invoke({
        "messages": [("user", f"Research the following: {query}. \n\nIMPORTANT: Use the `create_file` tool to save findings to the scratchpad before answering.")]
    })

    return result