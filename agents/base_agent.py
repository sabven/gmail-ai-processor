"""Base agent class for all agents"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from config import Config

logger = logging.getLogger(__name__)

class BaseAgentClass(ABC):
    """Base class for all agents in the email processing system"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def get_available_functions(self) -> List[Dict[str, Any]]:
        """Return the functions this agent provides"""
        pass
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main functionality"""
        pass
    
    def log_action(self, action: str, data: Dict[str, Any] = None):
        """Log agent actions"""
        log_msg = f"Agent {self.__class__.__name__} - {action}"
        if data:
            log_msg += f" - Data: {data}"
        self.logger.info(log_msg)
