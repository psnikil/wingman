"""Tools for executing shell commands using LangChain Community's ShellTool."""
from typing import Union, List
from langchain_community.tools.shell import ShellTool
from langchain.tools import tool

from .data_models import ExecuteCommandArgs

# Instantiate the ShellTool
_shell_tool = ShellTool()

@tool(
    parse_docstring=True, 
    args_schema=ExecuteCommandArgs,
    description="""Executes a shell command or a list of sequential commands in a bash-like environment.
    This tool is essential for system administration, file management tasks that require 
    complex chaining (like pipes or redirects), and running external utilities.
    
    Examples:
    - Single command: 'ls -R'
    - List of commands: ['cd project', 'npm install', 'npm run build']
    - Chained commands: 'grep -r "TODO" . | wc -l'
    
    When to use: Use this when standard file tools are insufficient or when direct CLI access is needed."""
)
def execute_command(commands: Union[str, List[str]]) -> str:
    """Executes shell commands in a bash-like environment."""
    args = ExecuteCommandArgs(commands=commands)
    try:
        # ShellTool expects 'commands' in input dict
        return _shell_tool.run({"commands": args.commands})
    except Exception as e:
        return f"Error executing command: {str(e)}"

__all__ = ["execute_command"]
