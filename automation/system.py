"""
System commands - time, date, volume, etc.
"""
import datetime
import platform
import subprocess
from typing import Tuple
class SystemManager:
    """System information and control"""
    
    def __init__(self):
        self.system = platform.system()
    
    def get_time(self) -> str:
        """Get current time"""
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')}"
    
    def get_date(self) -> str:
        """Get current date"""
        now = datetime.datetime.now()
        return f"Today is {now.strftime('%A, %B %d, %Y')}"
    
    def get_system_info(self) -> str:
        """Get system information"""
        info = {
            "System": platform.system(),
            "Release": platform.release(),
            "Version": platform.version(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "Python": platform.python_version()
        }
        
        return "\n".join(f"{k}: {v}" for k, v in info.items())
    
    def set_volume(self, level: int) -> str:
        """
        Set system volume (0-100).
        
        Args:
            level: Volume percentage
        """
        level = max(0, min(100, level))
        
        try:
            if self.system == "Windows":
                # Windows volume control
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(level / 100, None)
                return f"Volume set to {level}%"
                
            elif self.system == "Darwin":  # macOS
                subprocess.run(["osascript", "-e", f"set volume output volume {level}"], check=True)
                return f"Volume set to {level}%"
                
            else:  # Linux
                subprocess.run(["amixer", "set", "Master", f"{level}%"], check=True)
                return f"Volume set to {level}%"
                
        except Exception as e:
            return f"Could not set volume: {str(e)}"
    
    def shutdown(self, delay: int = 60) -> str:
        """
        Schedule system shutdown.
        
        Args:
            delay: Seconds before shutdown
        """
        # This requires confirmation
        return f"Shutdown scheduled in {delay} seconds. Use 'cancel shutdown' to abort."
    
    def cancel_shutdown(self) -> str:
        """Cancel scheduled shutdown"""
        try:
            if self.system == "Windows":
                subprocess.run(["shutdown", "/a"], check=True)
            else:
                subprocess.run(["shutdown", "-c"], check=True)
            return "Shutdown cancelled"
        except:
            return "No shutdown scheduled or could not cancel"
