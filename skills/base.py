"""
Base class for JARVIS skills
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
class BaseSkill(ABC):
    """Base class for all JARVIS skills"""
    
    # Skill metadata
    name: str = "base_skill"
    description: str = "Base skill class"
    triggers: list[str] = []  # Keywords that trigger this skill
    
    def __init__(self):
        self.enabled = True
    
    @abstractmethod
    def can_handle(self, command: str) -> bool:
        """
        Check if this skill can handle the command.
        
        Args:
            command: The user's command
        
        Returns:
            True if this skill should handle it
        """
        pass
    
    @abstractmethod
    def execute(self, command: str, context: Any) -> Optional[str]:
        """
        Execute the skill.
        
        Args:
            command: The user's command
            context: Conversation context
        
        Returns:
            Response string or None
        """
        pass
    
    def get_help(self) -> str:
        """Return help text for this skill"""
        return f"{self.name}: {self.description}"
