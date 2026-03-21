import os
from typing import Literal, Optional
from datetime import datetime

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents.middleware import ToolRetryMiddleware, ModelRetryMiddleware,LLMToolSelectorMiddleware
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from services.llm_client.llm_client import LLMClient
from tools.think_tools import think_tool
from agents.prompts.browser_agent_prompt import (
    BROWSER_AGENT_SYS_PROMPT,
    BROWSER_EXPLORE_INSTRUCTIONS,
    BROWSER_SUBAGENT_DELEGATION_INSTRUCTIONS
)

from rag.middleware import RAGToolSelectorMiddleware

class BrowserAgent:

    browser_llm: str = os.getenv("DEEP_RESEARCHER_LLM", 'gpt-oss:20b')
    generation_llm: str = os.getenv("ROUTER_LLM", 'llama3.1:8b')
    tool_llm: str = os.getenv("TOOL_LLM", 'llama3.1:8b')

    def __init__(self, provider: Literal["ollama", "openai", "anthropic"], **values):
        self.llm_client = LLMClient()
        self.provider = provider
        self.language_model = os.getenv("DEFAULT_OLLAMA_MODEL", 'gpt-oss:20b')
        self.max_browser_iterations = 5
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.mcp_client = MultiServerMCPClient({
            "playwright": {
                "transport": "stdio",
                "command": "npx",
                "args": [
                    "@playwright/mcp@latest"
                ]
            }
        })

    async def browser_agent_llm_f(self, query: str, context: Optional[str] = None) -> str:
        mcp_tools = await self.mcp_client.get_tools()

        # Catch MCP tool exceptions gracefully and send error back to the agent
        for tool in mcp_tools:
            tool.handle_tool_error = True
        print(f'Browser LLM: {self.browser_llm}')
        browser_llm = self.llm_client.init_ollama(
            model=self.browser_llm,
            temperature=0,
            reasoning=False,
            num_ctx=75000,
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
            BROWSER_AGENT_SYS_PROMPT
            + "\n\n"
            + "=" * 80
            + "\n\n"
            + BROWSER_SUBAGENT_DELEGATION_INSTRUCTIONS.format(
                max_browser_iterations=self.max_browser_iterations,
            )
        )

        # Create explore sub-agent
        explore_sub_agent = {
            "name": "explore-agent",
            "description": "Delegate precise web exploration tasks to this browser sub-agent. Keep the task atomic. Use it to navigate the web, extract accessibility trees, and interact with web elements.",
            "system_prompt": BROWSER_EXPLORE_INSTRUCTIONS.format(date=self.current_date),
            "tools": mcp_tools + [think_tool],
            "middleware":[
                ToolRetryMiddleware(
                    max_retries=3,
                    backoff_factor=2.0,
                    initial_delay=1.0,
                ),
                ModelRetryMiddleware(
                    max_retries=2,
                ),
            ]
        }

        root = os.path.abspath("./")

        # Create the agent
        browser_agent = create_deep_agent(
            model=browser_llm,
            system_prompt=system_prompt,
            tools=[think_tool],
            subagents=[explore_sub_agent],
            backend=FilesystemBackend(
                root_dir=root,
                virtual_mode=True
            ),
            middleware=[
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

        response = await browser_agent.ainvoke({
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ],
        })
        return response['messages'][-1].content

if __name__ == "__main__":
    browser_agent = BrowserAgent("ollama")
    response = browser_agent.browser_agent_llm_f("can you browser through https://www.uniqlo.com/uk/en/ and tell me what are the new arrivals for men?", "")
    print(response)
    


        