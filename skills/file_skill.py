"""
File management skill
"""
from jarvis.skills.base import BaseSkill
import os
from pathlib import Path
class FileSkill(BaseSkill):
    """Handle file operations"""
    
    name = "file_manager"
    description = "Manage files and directories"
    triggers = ["list files", "show files", "directory", "folder", "create folder"]
    
    def can_handle(self, command: str) -> bool:
        command = command.lower()
        return any(trigger in command for trigger in self.triggers)
    
    def execute(self, command: str, context) -> str:
        command = command.lower()
        
        if "list" in command or "show" in command:
            # Try to extract path
            words = command.split()
            path = "."
            
            for i, word in enumerate(words):
                if word in ["in", "from", "of"] and i + 1 < len(words):
                    potential_path = words[i + 1]
                    if os.path.exists(potential_path):
                        path = potential_path
                        break
            
            return self._list_directory(path)
        
        if "create" in command and ("folder" in command or "directory" in command):
            # Extract folder name
            words = command.split()
            for word in words:
                if word not in ["create", "folder", "directory", "named", "called", "make", "new", "a"]:
                    try:
                        Path(word).mkdir(parents=True, exist_ok=True)
                        return f"Created directory: {word}"
                    except:
                        continue
            
            return "I couldn't determine which folder to create."
        
        return "I'm not sure what file operation you want."
    
    def _list_directory(self, path: str) -> str:
        """List contents of a directory"""
        try:
            p = Path(path)
            if not p.exists():
                return f"Path not found: {path}"
            
            if p.is_file():
                return f"{path} is a file, not a directory."
            
            entries = list(p.iterdir())
            
            if not entries:
                return f"Directory '{path}' is empty."
            
            dirs = [e for e in entries if e.is_dir()]
            files = [e for e in entries if e.is_file()]
            
            result = f"Contents of {path}:\n\n"
            
            if dirs:
                result += "Directories:\n"
                for d in sorted(dirs):
                    result += f"  📁 {d.name}\n"
                result += "\n"
            
            if files:
                result += "Files:\n"
                for f in sorted(files):
                    size = f.stat().st_size
                    size_str = self._format_size(size)
                    result += f"  📄 {f.name} ({size_str})\n"
            
            return result
            
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    def _format_size(self, size: int) -> str:
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
