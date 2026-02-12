"""
Time and date skill
"""
from jarvis.skills.base import BaseSkill
import datetime
class TimeSkill(BaseSkill):
    """Handle time and date queries"""
    
    name = "time"
    description = "Tell the current time and date"
    triggers = ["time", "date", "day", "what time", "what day"]
    
    def can_handle(self, command: str) -> bool:
        command = command.lower()
        return any(trigger in command for trigger in self.triggers)
    
    def execute(self, command: str, context) -> str:
        command = command.lower()
        now = datetime.datetime.now()
        
        if "time" in command:
            return f"The current time is {now.strftime('%I:%M %p')}"
        
        if "date" in command or "day" in command:
            return f"Today is {now.strftime('%A, %B %d, %Y')}"
        
        return f"It is currently {now.strftime('%I:%M %p on %A, %B %d, %Y')}"
