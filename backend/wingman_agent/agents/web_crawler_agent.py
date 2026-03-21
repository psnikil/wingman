import sys
from agents.prompts.web_crawler_prompt import GENERATION_LLM_SYS_PROMPT
from langchain.agents import create_agent
from langchain_core.messages import AnyMessage
from agents.prompts.web_crawler_prompt import CRAWLER_LLM_SYS_PROMPT, ORCHESTRATOR_LLM_SYS_PROMPT
from pydantic import BaseModel, Field
import os
import time
from typing import List, Literal, Annotated, Optional, Dict, Any
from datetime import datetime

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents.middleware import ToolRetryMiddleware, ModelRetryMiddleware
from langchain.tools import tool
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import (
    create_sync_playwright_browser,  # A synchronous browser is available, though it isn't compatible with jupyter.\n",   },
    create_async_playwright_browser,
)

from services.llm_client.llm_client import LLMClient
from tools.think_tools import think_tool
from tools.python_tools import run_python_code
from tools.web_tools import web_search_duckduckgo

from agents.prompts.web_crawler_prompt import (
    WEB_CRAWLER_SYS_PROMPT,
    CRAWLER_SUBAGENT_INSTRUCTIONS,
    ANALYZER_SUBAGENT_INSTRUCTIONS,
    SUBAGENT_DELEGATION_INSTRUCTIONS,
    CRAWLER_LLM_SYS_PROMPT, ORCHESTRATOR_LLM_SYS_PROMPT
)

class WebCrawlerState(BaseModel):
    """
    State shared across all RLM graph nodes using Pydantic BaseModel.
    """

    pii_input: str

    # web URL handling
    seen_urls: List[str] = Field(default_factory=list)

    # agent dicts
    messages: Annotated[List[AnyMessage], add_messages] = Field(default_factory=list)
    crawler_messages: Annotated[List[AnyMessage], add_messages] = Field(default_factory=list)
    analyzer_messages: Annotated[List[AnyMessage], add_messages] = Field(default_factory=list)

    # web crawl stats
    turns: int = Field(default=0)
    max_turns: int = Field(default=10)
    
    # results
    results: str = Field(default="")

    terminated: bool = Field(default=False)

# Custom tools for the orchestrator
@tool
def sleep_tool(seconds: int) -> str:
    """Sleeps for a specified number of seconds to respect rate limits."""
    time.sleep(seconds)
    return f"Slept for {seconds} seconds."

class WebCrawlerAgent:

    browser_llm: str = os.getenv("DEEP_RESEARCHER_LLM", 'qwen3:14b')
    tool_llm: str = os.getenv("TOOL_LLM", 'qwen3:14b')

    def __init__(self, provider: Literal["ollama", "openai", "anthropic"], **values):
        self.llm_client = LLMClient()
        self.provider = provider
        self.mcp_client = MultiServerMCPClient({
            "playwright": {
                "transport": "stdio",
                "command": "npx",
                "args": ["@playwright/mcp@latest"]
            }
        })

    async def run(self, pii_input: str) -> str:
        mcp_tools = await self.mcp_client.get_tools()
        
        # Catch MCP tool exceptions gracefully and send error back to the agent
        for t in mcp_tools:
            t.handle_tool_error = True
            
        print(f'Browser LLM: {self.browser_llm}')
        browser_llm = self.llm_client.init_ollama(
            model=self.browser_llm,
            temperature=0,
            reasoning=False,
            num_ctx=55000,
            stream=False,
        )

        tool_llm = self.llm_client.init_ollama(
            model=self.tool_llm,
            temperature=0,
            reasoning=True,
            num_ctx=20000,
            stream=False,
        )

        system_prompt = (
            WEB_CRAWLER_SYS_PROMPT
            + "\n\n"
            + "=" * 80
            + "\n\n"
            + SUBAGENT_DELEGATION_INSTRUCTIONS
        )

        crawler_sub_agent = {
            "name": "crawler-agent",
            "description": "Delegate web search and web page navigation tasks to this sub-agent. Returns raw text from web pages.",
            "system_prompt": CRAWLER_SUBAGENT_INSTRUCTIONS,
            "tools": mcp_tools + [web_search_duckduckgo, think_tool, sleep_tool],
            "middleware":[
                ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
                ModelRetryMiddleware(max_retries=2),
            ]
        }
        
        analyzer_sub_agent = {
            "name": "analyzer-agent",
            "description": "Delegate content analysis tasks to this sub-agent. Extracts and verifies if PII is present in a block of text.",
            "system_prompt": ANALYZER_SUBAGENT_INSTRUCTIONS,
            "tools": [run_python_code, think_tool],
            "middleware":[
                ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
                ModelRetryMiddleware(max_retries=2),
            ]
        }

        root = os.path.abspath("./")

        orchestrator_agent = create_deep_agent(
            model=browser_llm,
            system_prompt=system_prompt,
            tools=[sleep_tool, think_tool],
            subagents=[crawler_sub_agent, analyzer_sub_agent],
            backend=FilesystemBackend(
                root_dir=root,
                virtual_mode=False
            ),
            middleware=[
                ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
                ModelRetryMiddleware(max_retries=2),
            ],
        )

        initial_message = (
            f"User PII to search for: {pii_input}\n\n"
            "Please begin your search strategy. "
            "Make sure to save updates to .artifacts/journey.md and successes to .artifacts/web_crawl_res.md. "
            "Be mindful of rate limits!"
        )

        response = await orchestrator_agent.ainvoke({
            "messages": [
                {
                    "role": "user",
                    "content": initial_message,
                }
            ],
        })
        return response['messages'][-1].content

def orchestrator_node(state: WebCrawlerState) -> Dict[str, Any]:
    """
    ORCHESTRATOR NODE
    
    Responsible for:
    1. Analyzing current state and previous execution
    2. Deciding next stratergy for web crawl
    
    The result should:
    - Create a TODO list for the crawler sub-agent
    - Update the TODOs and results with the findings
    
    Input state: user query, previous execution results
    Output state: updated TODOs
    """
    print("_____________in orchestrator node_____________", flush=True)
    
    llm_client = LLMClient()
    llm = llm_client.init_ollama(
        model="hf.co/mradermacher/kappa-20b-131k-GGUF:Q4_K_S",
        temperature=0.4,
        reasoning=False,
        num_ctx=40000
    )
    system_prompt = ORCHESTRATOR_LLM_SYS_PROMPT + "\n" + "The current number of turns is " + str(state.turns) + "\n" + "The maximum number of turns is " + str(state.max_turns)
    orchestrator_prompt = (
        f"The users provided PII is {state.pii_input}. "
        "Your task is to observe previous results and create the next set of search queries or URLs "
        "to assist the web crawler in discovering instances of this PII. "
        "Do not attempt to search or browse yourself."
    )
    prompt_messages = [
        ("human", orchestrator_prompt),
    ]
    
    # Add message history from state
    for msg in state.messages:
        content = msg.content
        if isinstance(content, list):
            content = " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in content])
        
        if isinstance(msg, AIMessage):
             prompt_messages.append(("ai", str(content)))
        elif isinstance(msg, HumanMessage):
             prompt_messages.append(("human", str(content)))
    root = os.path.abspath("./")

    orchestrator_agent = create_deep_agent(
                model=llm,
                system_prompt=system_prompt,
                tools=[think_tool],
                # backend=FilesystemBackend(
                #     root_dir=root,
                #     virtual_mode=False
                # ),
                middleware=[
                    ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
                    ModelRetryMiddleware(max_retries=2),
                ],
            )
    response = orchestrator_agent.invoke({
        "messages": prompt_messages,
    })

    if state.turns == state.max_turns:
        state.terminated = True
    print('The task is ', response['messages'][-1].content, flush=True)
    print("_____________END orchestrator node_____________", flush=True)
    return {
        "messages": response['messages'],
        "turns": state.turns + 1,
        "terminated": state.terminated
    }
def crawling_node(state: WebCrawlerState) -> Dict[str, Any]:
    """
    CRAWLING NODE
    
    Responsible for:
    1. Crawling the URL for users PII and analysing it 
    2. Deciding next stratergy for web crawl
    
    The result should:
    - analyse provide a summary of finding
    - Update the TODOs and results with the findings
    
    Input state: user query, previous execution results
    Output state: updated TODOs
    """
    print("_____________in crawling node_____________", flush=True)
    browser = create_sync_playwright_browser()
    toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=browser)
    browser_tools = toolkit.get_tools()
    
    llm_client = LLMClient()
    llm = llm_client.init_ollama(
        model="hf.co/mradermacher/kappa-20b-131k-GGUF:Q4_K_S",
        temperature=0,
        reasoning=False,
        num_ctx=40000
    )
    system_prompt = CRAWLER_LLM_SYS_PROMPT + "\n" + "The current number of turns is " + str(state.turns) + "\n" + "The maximum number of turns is " + str(state.max_turns)
    orchestrator_prompt = "your task is " + state.messages[-1].content + "\n" + "The seen URL are " + str(state.seen_urls)
    prompt_messages = [("human", orchestrator_prompt)]
    # Add message history from state
    # for msg in state.messages:
    #     if isinstance(msg, AIMessage):
    #          prompt_messages.append(("ai", msg.content))
    #     elif isinstance(msg, HumanMessage):
    #          # Avoid duplicating the original prompt if it's the first human message
    #          if msg.content != state.original_prompt:
    #             prompt_messages.append(("human", msg.content))
    # root = os.path.abspath("./")

    crawler_agent = create_agent(
                model=llm,
                system_prompt=system_prompt,
                tools=[think_tool, web_search_duckduckgo, sleep_tool]+browser_tools,
                middleware=[
                    ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
                    ModelRetryMiddleware(max_retries=2),
                ],
            )
    response = crawler_agent.invoke({
        "messages": prompt_messages,
    })
    print('The crawler response is ', response['messages'][-1].content, flush=True)
    print("_____________END crawling node_____________", flush=True)
    return {
        "messages": response['messages'][-1],
        "crawler_messages": response['messages'],
    }

def generation_node(state: WebCrawlerState) -> Dict[str, Any]:
    """
    GENERATION NODE
    
    Responsible for:
    1. Generating the final response
    
    Input state: user query, previous execution results
    Output state: final response
    """
    print("_____________in generation node_____________")

    # if not terminated do not ddo anythign
    if not state.terminated:
        return state

    
    llm_client = LLMClient()
    llm = llm_client.init_ollama(
        model="hf.co/mradermacher/kappa-20b-131k-GGUF:Q4_K_S",
        temperature=0,
        reasoning=False,
        num_ctx=40000
    )
    system_prompt = GENERATION_LLM_SYS_PROMPT
    generation_prompt = "The history of the crawl is " + str(state.messages) + "\n" + "The seen URL are " + str(state.seen_urls)
    prompt_messages = [
        ("system", system_prompt)
        ]
    # Add message history from state
    for msg in state.messages:
        content = msg.content
        if isinstance(content, list):
            content = " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in content])
        
        if isinstance(msg, AIMessage):
             prompt_messages.append(("ai", str(content)))
        elif isinstance(msg, HumanMessage):
             prompt_messages.append(("human", str(content)))
    message_prompt = ChatPromptTemplate.from_messages(prompt_messages)

    generation_llm = message_prompt | llm | StrOutputParser()

    # generation_agent = create_agent(
    #             model=llm,
    #             system_prompt=system_prompt,
    #             tools=[think_tool, web_search_duckduckgo],
    #             middleware=[
    #                 ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
    #                 ModelRetryMiddleware(max_retries=2),
    #             ],
    #         )
    response = generation_llm.invoke({})

    print('the final response is ', len(response))

    print("_____________END generation node_____________")
    return {
        "messages": response['messages'][-1],
        "generation_messages": response['messages'],
        "result": response['messages'][-1].content
    }

def create_web_crawler_graph() -> StateGraph:
    """
    Create the Web Crawler Agent graph
    """
    builder = StateGraph(WebCrawlerState)
    def should_continue(state: WebCrawlerState) -> Literal["crawling", "end"]:
        return "end" if state.terminated else "crawling"

    # nodes
    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("crawling", crawling_node)
    builder.add_node("generation", generation_node)
    # edges
    builder.add_edge(START, "orchestrator")
    # builder.add_edge("orchestrator", "crawling")  # Handled by conditional edges below
    builder.add_edge("crawling", "orchestrator")
    builder.add_edge("generation", END)
    builder.add_conditional_edges(
        "orchestrator",
        should_continue,
        {
            "end": "generation",
            "crawling": "crawling"
        }
    )

    return builder.compile()

def create_initial_state(
    prompt: str,
    context: str | List[str],
    max_iterations: int = 10
    ) -> WebCrawlerState:
        """Create initial RLMState for graph execution"""
        return WebCrawlerState(
            pii_input=prompt,
            max_turns=max_iterations,
            turns=0,
            terminated=False,
            messages=[],
            seen_urls=[],
            results="",
        )

def execute_web_crawler_graph():
    graph = create_web_crawler_graph()
    state = create_initial_state(
        prompt="nikilps36@gmail.com",
        context="",
        max_iterations=10
    )

    print('The init state is ', state, flush=True)
    res = graph.invoke(state)
    
    return res

if __name__ == "__main__":
    import asyncio
    # agent = WebCrawlerAgent("ollama")
    # res = asyncio.run(agent.run("test.email@example.com"))
    res = execute_web_crawler_graph()
    print(res, flush=True)
