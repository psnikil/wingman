"""Tools for discovering and executing modular skills located in the project's skills directory."""
import os
import subprocess
import sys
from typing import List, Optional
from langchain.tools import tool

from .data_models import RunSkillArgs

SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills"))

@tool(
    parse_docstring=True,
    description="""Lists all available modular skills within the project's 'skills' directory.
    When to use: Use this to discover specialized capabilities available via 'run_skill'."""
)
def list_skills() -> str:
    """Lists all available modular skills."""
    try:
        if not os.path.exists(SKILLS_DIR):
            return f"Skills directory not found at {SKILLS_DIR}"
            
        skills = [d for d in os.listdir(SKILLS_DIR) if os.path.isdir(os.path.join(SKILLS_DIR, d))]
        if not skills:
            return "No skills found in the skills directory."
            
        return "Available skills:\n- " + "\n- ".join(sorted(skills))
    except Exception as e:
        return f"Error listing skills: {str(e)}"

@tool(
    parse_docstring=True, 
    args_schema=RunSkillArgs,
    description="""Executes a specific modular skill from the 'skills' directory.
    Skills are standalone Python modules that perform well-defined tasks.
    
    Examples:
    - Basic run: run_skill(skill_name="data_cleanup")
    - Run with args: run_skill(skill_name="report_gen", args=["--format", "pdf"])
    
    When to use: Use to execute complex, predefined tasks formatted as skills."""
)
def run_skill(skill_name: str, args: Optional[List[str]] = None) -> str:
    """Executes a specific modular skill."""
    run_args = RunSkillArgs(skill_name=skill_name, args=args)
    try:
        skill_path = os.path.join(SKILLS_DIR, run_args.skill_name)
        if not os.path.exists(skill_path):
            return f"Skill '{run_args.skill_name}' not found."
            
        # Look for entry point
        entry_point = None
        for name in ["main.py", "run.py"]:
            if os.path.exists(os.path.join(skill_path, name)):
                entry_point = os.path.join(skill_path, name)
                break
                
        if not entry_point:
            return f"No entry point (main.py or run.py) found for skill '{run_args.skill_name}'."
            
        # Execute the skill
        cmd = [sys.executable, entry_point]
        if run_args.args:
            cmd.extend(run_args.args)
            
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode == 0:
            return f"Skill '{run_args.skill_name}' executed successfully:\n{output}"
        else:
            return f"Skill '{run_args.skill_name}' failed with return code {result.returncode}.\nError: {error}"
            
    except Exception as e:
        return f"Error running skill: {str(e)}"