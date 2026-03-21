import os
import json
import logging
from typing import Dict, Any

class OrchestratorLogger:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.log_dir = "log_data"
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, f"session_{session_id}.log")
        
        # Setup session logger
        self.session_logger = logging.getLogger(f"session_{session_id}")
        self.session_logger.setLevel(logging.INFO)
        
        # Setup graph logger (for node entry/exit)
        self.graph_logger = logging.getLogger("graph")
        self.graph_logger.setLevel(logging.INFO)
        
        # Setup services logger (for ollama client)
        self.services_logger = logging.getLogger("services")
        self.services_logger.setLevel(logging.INFO)
        
        # Clear handlers to avoid duplication if main.py is re-run in same process
        if self.session_logger.hasHandlers():
            self.session_logger.handlers.clear()
        if self.graph_logger.hasHandlers():
            self.graph_logger.handlers.clear()
        if self.services_logger.hasHandlers():
            self.services_logger.handlers.clear()
            
        # File handler common to all
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        
        self.session_logger.addHandler(fh)
        self.graph_logger.addHandler(fh)
        self.services_logger.addHandler(fh)

    def log_state(self, name: str, state: Dict[str, Any], is_router: bool = False):
        """Logs the pretty-printed state of a node or router."""
        label = "ROUTER" if is_router else f"NODE: {name}"
        self.session_logger.info(
            f"\n{'='*50}\n{label}\nSTATE:\n{json.dumps(state, default=str, indent=4)}\n{'='*50}\n"
        )
