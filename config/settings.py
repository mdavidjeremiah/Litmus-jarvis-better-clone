"""
Configuration management for JARVIS
"""
import yaml
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path
@dataclass
class VoiceSettings:
    enabled: bool = True
    wake_word: str = "jarvis"
    language: str = "en-US"
    voice_id: Optional[str] = None
    speech_rate: int = 150
    energy_threshold: int = 300
    pause_threshold: float = 0.8
    phrase_threshold: float = 0.3
@dataclass
class LLMSettings:
    model: str = "llama2"
    host: str = "http://localhost:11434"
    temperature: float = 0.7
    max_tokens: int = 2000
    context_window: int = 4096
    system_prompt: str = """You are JARVIS, an AI assistant inspired by Iron Man's AI. 
You are helpful, intelligent, and slightly witty. You can help with coding, 
system tasks, and answering questions. You work offline using local models."""
@dataclass
class WebSettings:
    cache_path: str = "data/web_cache.db"
    cache_ttl_days: int = 30
    max_cache_size_mb: int = 500
    auto_fetch: bool = True
@dataclass
class AutomationSettings:
    allowed_apps: List[str] = field(default_factory=lambda: [
        "chrome", "firefox", "code", "terminal", "calculator", "notepad"
    ])
    code_sandbox_path: str = "data/sandbox"
    confirm_destructive: bool = True
@dataclass
class Settings:
    voice: VoiceSettings = field(default_factory=VoiceSettings)
    llm: LLMSettings = field(default_factory=LLMSettings)
    web: WebSettings = field(default_factory=WebSettings)
    automation: AutomationSettings = field(default_factory=AutomationSettings)
    data_dir: str = "data"
    log_level: str = "INFO"
    
    @classmethod
    def from_yaml(cls, path: str) -> "Settings":
        """Load settings from YAML file"""
        path = Path(path)
        
        if not path.exists():
            # Return defaults
            return cls()
        
        with open(path, 'r') as f:
            data = yaml.safe_load(f) or {}
        
        return cls(
            voice=VoiceSettings(**data.get('voice', {})),
            llm=LLMSettings(**data.get('llm', {})),
            web=WebSettings(**data.get('web', {})),
            automation=AutomationSettings(**data.get('automation', {})),
            data_dir=data.get('data_dir', 'data'),
            log_level=data.get('log_level', 'INFO')
        )
    
    def to_yaml(self, path: str):
        """Save settings to YAML file"""
        import yaml
        
        data = {
            'voice': self.voice.__dict__,
            'llm': self.llm.__dict__,
            'web': self.web.__dict__,
            'automation': self.automation.__dict__,
            'data_dir': self.data_dir,
            'log_level': self.log_level
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
