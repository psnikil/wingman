import os
from typing import List, Optional, Any
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolSelectorMiddleware

# Import tools
from tools.file_tools import (
    create_file, delete_file, modify_file, rename_file, 
    move_file, list_files, read_file, copy_file, file_search
)
from tools.web_tools import web_search_duckduckgo
from tools.cli_tools import execute_command
from tools.os_tools import UbuntuOSTools
from tools.python_tools import run_python_code
from tools.skills_tools import list_skills, run_skill

from deepagents import create_deep_agent

# Configuration
DEFAULT_MODEL = os.getenv("DEEP_AGENT_MODEL", "llama3.1:8b")
SCRATCHPAD_PATH = "./.artifacts/scratchpad.md"
DATA_DIR = "./data"

def get_deep_agent_tools():
    """Returns the list of tools available to the Deep Agent."""
    tools = [
        create_file, delete_file, modify_file, rename_file, 
        move_file, list_files, read_file, copy_file, file_search,
        web_search_duckduckgo,
        execute_command,
        UbuntuOSTools.open_browser,
        UbuntuOSTools.open_app,
        UbuntuOSTools.take_screenshot,
        UbuntuOSTools.os_search_files,
        UbuntuOSTools.download_file,
        run_python_code,
        list_skills,
        run_skill
    ]
    return tools

def create_deep_agent_system_prompt(query: str):
    """Generates the detailed system prompt for the Deep Agent."""
    return f"""
You are a Deep Agent, an advanced autonomous system designed to solve complex tasks through multi-step reasoning and execution.
Your primary objective: "{query}"

### OPERATIONAL GUIDELINES
1. **PLANNING**: Start by using the `write_todos` tool to list the steps required. Update your progress frequently.
2. **CONTEXT MANAGEMENT**: Use the scratchpad at `{SCRATCHPAD_PATH}` as your research board. Write all multi-step findings there.
3. **FILE OPERATIONS**: All generated artifacts or final reports MUST be saved in the `{DATA_DIR}/` directory unless specified otherwise.

### CRITICAL RULES
- **STRICT TOOL USAGE**: You MUST call a tool when an action is required. Do not just describe what you will do.
- **ONE ACTION**: Perform exactly one tool call per response.
- **STREAMING**: Your thoughts are being streamed; provide concise reasoning before or during tool choice.
"""

async def deep_agent_invoke(query: str, context: Optional[str] = None):
    """
    Invokes the Deep Agent to process a user query with rich streaming results.
    
    Args:
        query: The user's request.
        context: Optional background context.
    """
    llm = ChatOllama(
        model=DEFAULT_MODEL,
        temperature=0.1,
    )
    
    selector_llm = ChatOllama(
        model=os.getenv("TOOL_SELECTOR_MODEL", "llama3.1:8b"),
        temperature=0,
    )

    tools = get_deep_agent_tools()
    system_prompt = create_deep_agent_system_prompt(query)
    
    if context:
        system_prompt += f"\n\n### ADDITIONAL CONTEXT\n{context}"

    # Create the agent with deep agent features (todos, filesystem, etc.)
    agent = create_deep_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        middleware=[
            LLMToolSelectorMiddleware(
                model=selector_llm,
                max_tools=5,
                always_include=["create_file", "modify_file", "read_file", "write_todos"]
            )
        ]
    )

    print(f"\n🚀 [Deep Agent] Starting task: {query}\n" + "═"*60 + "\n")
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(SCRATCHPAD_PATH), exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    final_result = None
    last_todos = []
    
    async for event in agent.astream_events(
        {"messages": [HumanMessage(content=query)]}, 
        version="v2"
    ):
        kind = event["event"]
        
        # 1. Stream content from the chat model
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                print(content, end="", flush=True)
        
        # 2. Report tool interactions
        elif kind == "on_tool_start":
            print(f"\n\n🛠️  [Tool Call]: {event['name']}")
            print(f"   Input: {event['data'].get('input')}")
            
        elif kind == "on_tool_end":
            output = event["data"].get("output")
            out_str = str(output)
            if len(out_str) > 500:
                out_str = out_str[:500] + "..."
            print(f"✅ [Tool Result]: {out_str}\n")

        # 3. Capture State Updates (Todos, Context, etc.)
        elif kind == "on_chain_end":
            output = event["data"].get("output")
            if isinstance(output, dict):
                # Monitor Todo List
                todos = output.get("todos")
                if todos and todos != last_todos:
                    last_todos = todos
                    print(f"\n📋 [Updated Todo List]:")
                    for todo in todos:
                        status = "✅" if todo.get("completed") else "⏳"
                        print(f"   {status} {todo.get('todo')}")
                
                # Monitor Context/Filesystem if possible
                if "files" in output and output["files"]:
                    print(f"📂 [Virtual Filesystem Updated]: {list(output['files'].keys())}")
                
                # Check for final result from the main graph
                if event["name"] == "LangGraph":
                    final_result = output

    print("\n" + "═"*60 + "\n🎯 [Task Completed]\n")
    return final_result

if __name__ == "__main__":
    import sys
    import asyncio
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        asyncio.run(deep_agent_invoke(query))
    else:
        print("Usage: python deep_agents.py <query>")
