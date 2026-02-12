from jarvis.skills.base import BaseSkill
class MySkill(BaseSkill):
    name = "my_skill"
    triggers = ["my trigger"]
    
    def can_handle(self, command: str) -> bool:
        return "my trigger" in command.lower()
    
    def execute(self, command: str, context):
        return "Skill executed!"
