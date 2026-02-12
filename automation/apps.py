"""
Application management - open/close apps
"""
import subprocess
import platform
import webbrowser
from typing import Dict, Optional
class AppManager:
    """Manage opening and closing applications"""
    
    def __init__(self):
        self.system = platform.system()
        self.known_apps = ["chrome", "firefox", "code", "terminal", "calculator", "notepad", "files"]
        
        # App command mappings
        self.app_commands: Dict[str, Dict[str, str]] = {
            "chrome": {
                "Windows": "start chrome",
                "Darwin": "open -a 'Google Chrome'",
                "Linux": "google-chrome"
            },
            "firefox": {
                "Windows": "start firefox",
                "Darwin": "open -a Firefox",
                "Linux": "firefox"
            },
            "code": {
                "Windows": "code",
                "Darwin": "code",
                "Linux": "code"
            },
            "terminal": {
                "Windows": "start cmd",
                "Darwin": "open -a Terminal",
                "Linux": "gnome-terminal || xterm || konsole"
            },
            "calculator": {
                "Windows": "calc",
                "Darwin": "open -a Calculator",
                "Linux": "gnome-calculator || kcalc"
            },
            "notepad": {
                "Windows": "notepad",
                "Darwin": "open -a TextEdit",
                "Linux": "gedit || mousepad || nano"
            },
            "files": {
                "Windows": "explorer",
                "Darwin": "open .",
                "Linux": "nautilus || dolphin || thunar"
            }
        }
    
    def open_app(self, app_name: str) -> str:
        """
        Open an application by name.
        
        Args:
            app_name: Name of the app to open
        
        Returns:
            Status message
        """
        app_name = app_name.lower()
        
        # Check if it's a URL
        if app_name.startswith(("http://", "https://", "www.")):
            webbrowser.open(app_name)
            return f"opened {app_name} in browser"
        
        # Get command for this OS
        if app_name in self.app_commands:
            command = self.app_commands[app_name].get(self.system, "")
            
            if command:
                try:
                    # Handle alternatives (command1 || command2)
                    if "||" in command:
                        commands = [c.strip() for c in command.split("||")]
                        for cmd in commands:
                            try:
                                subprocess.Popen(cmd, shell=True)
                                return f"opened {app_name}"
                            except:
                                continue
                        return f"could not open {app_name}"
                    else:
                        subprocess.Popen(command, shell=True)
                        return f"opened {app_name}"
                        
                except Exception as e:
                    return f"error opening {app_name}: {str(e)}"
        
        # Try to open directly as a command
        try:
            subprocess.Popen(app_name, shell=True)
            return f"opened {app_name}"
        except:
            return f"could not find application '{app_name}'"
    
    def close_app(self, app_name: str) -> str:
        """
        Close an application.
        
        Args:
            app_name: Name of the app to close
        
        Returns:
            Status message
        """
        app_name = app_name.lower()
        
        # Platform-specific kill commands
        kill_commands = {
            "Windows": f"taskkill /f /im {app_name}.exe",
            "Darwin": f"pkill -i {app_name}",
            "Linux": f"pkill -i {app_name}"
        }
        
        command = kill_commands.get(self.system, f"pkill -i {app_name}")
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return f"closed {app_name}"
            else:
                return f"could not close {app_name} (may not be running)"
        except Exception as e:
            return f"error closing {app_name}: {str(e)}"
    
    def open_url(self, url: str) -> str:
        """Open a URL in default browser"""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)
        return f"opened {url}"
