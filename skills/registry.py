"""
Skill registry for managing and executing skills
"""
from typing import List, Optional, Type
import importlib
import pkgutil
from jarvis.skills.base import BaseSkill
class SkillRegistry:
    """Registry for all JARVIS skills"""
    
    def __init__(self):
        self.skills: List[BaseSkill] = []
    
    def register(self, skill: BaseSkill):
        """Register a skill"""
        self.skills.append(skill)
        print(f"  ✓ Loaded skill: {skill.name}")
    
    def load_builtin_skills(self):
        """Load all built-in skills"""
        # Import and register built-in skills
        from jarvis.skills.time_skill import TimeSkill
        from jarvis.skills.calculator_skill import CalculatorSkill
        from jarvis.skills.file_skill import FileSkill
        
        self.register(TimeSkill())
        self.register(CalculatorSkill())
        self.register(FileSkill())
    
    def execute(self, command: str, context) -> Optional[str]:
        """
        Try to execute a skill for the given command.
        
        Args:
            command: User's command
            context: Conversation context
        
        Returns:
            Skill response or None if no skill handled it
        """
        for skill in self.skills:
            if skill.enabled and skill.can_handle(command):
                try:
                    return skill.execute(command, context)
                except Exception as e:
                    print(f"Skill {skill.name} error: {e}")
                    return f"Error in {skill.name}: {str(e)}"
        
        return None  # No skill handled it
    
    def list_skills(self) -> List[str]:
        """List all registered skills"""
        return [f"{s.name}: {s.description}" for s in self.skills]
