"""
Code management - write, edit, execute code
"""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple
class CodeManager:
    """Manage code files and execution"""
    
    def __init__(self, sandbox_path: str = "data/sandbox"):
        self.sandbox_path = Path(sandbox_path)
        self.sandbox_path.mkdir(parents=True, exist_ok=True)
        
        # Track created files
        self.recent_files: list[Path] = []
    
    def create_file(self, filename: str, content: str, language: Optional[str] = None) -> Tuple[bool, str]:
        """
        Create a new code file.
        
        Args:
            filename: Name of the file
            content: File content
            language: Programming language (optional)
        
        Returns:
            (success, message)
        """
        try:
            # Determine path
            if os.path.isabs(filename):
                filepath = Path(filename)
            else:
                filepath = self.sandbox_path / filename
            
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.recent_files.append(filepath)
            
            return True, f"Created file: {filepath}"
            
        except Exception as e:
            return False, f"Error creating file: {str(e)}"
    
    def read_file(self, filename: str) -> str:
        """Read a file's contents"""
        try:
            if os.path.isabs(filename):
                filepath = Path(filename)
            else:
                filepath = self.sandbox_path / filename
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def edit_file(self, filename: str, old_text: str, new_text: str) -> Tuple[bool, str]:
        """
        Edit a file by replacing text.
        
        Args:
            filename: File to edit
            old_text: Text to find
            new_text: Text to replace with
        
        Returns:
            (success, message)
        """
        try:
            if os.path.isabs(filename):
                filepath = Path(filename)
            else:
                filepath = self.sandbox_path / filename
            
            content = filepath.read_text(encoding='utf-8')
            
            if old_text not in content:
                return False, "Text not found in file"
            
            new_content = content.replace(old_text, new_text, 1)
            filepath.write_text(new_content, encoding='utf-8')
            
            return True, f"Updated {filepath}"
            
        except Exception as e:
            return False, f"Error editing file: {str(e)}"
    
    def execute_python(self, code: str) -> Tuple[bool, str]:
        """
        Execute Python code safely.
        
        Args:
            code: Python code to execute
        
        Returns:
            (success, output)
        """
        # Create temporary file
        temp_file = self.sandbox_path / "temp_script.py"
        temp_file.write_text(code, encoding='utf-8')
        
        try:
            # Execute in subprocess with timeout
            result = subprocess.run(
                ["python", str(temp_file)],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(self.sandbox_path)
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nErrors:\n{result.stderr}"
            
            return result.returncode == 0, output
            
        except subprocess.TimeoutExpired:
            return False, "Execution timed out (10s limit)"
        except Exception as e:
            return False, f"Execution error: {str(e)}"
        finally:
            # Cleanup
            if temp_file.exists():
                temp_file.unlink()
    
    def list_files(self) -> str:
        """List files in sandbox"""
        files = list(self.sandbox_path.glob("**/*"))
        if not files:
            return "No files in sandbox"
        
        output = "Files in sandbox:\n"
        for f in files:
            if f.is_file():
                rel_path = f.relative_to(self.sandbox_path)
                size = f.stat().st_size
                output += f"  {rel_path} ({size} bytes)\n"
        
        return output
