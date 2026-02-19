"""
JARVIS Core Orchestrator - Main event loop and state management
"""
import asyncio
import threading
import time
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum, auto
from voice.stt import SpeechRecognizer
from voice.tts import TextToSpeech
from voice.wake_word import WakeWordDetector
from llm.ollama_client import OllamaClient
from automation.apps import AppManager
from automation.coding import CodeManager
from automation.system import SystemManager
from web.cache import WebCache
from skills.registry import SkillRegistry
class State(Enum):
    IDLE = auto()
from config.settings import Settings

LISTENING = auto()
PROCESSING = auto()
RESPONDING = auto()
ERROR = auto()
@dataclass
class Context:
    """Conversation context"""
    last_command: str = ""
    last_response: str = ""
    session_start: float = 0.0
    variables: dict = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}
        if self.session_start == 0.0:
            self.session_start = time.time()
class JarvisCore:
    """Main JARVIS orchestrator"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.state = State.IDLE
        self.context = Context()
        self.running = False
        
        # Initialize modules
        self._init_modules()
        
        # State change callbacks
        self.state_callbacks: list[Callable] = []
    
    def _init_modules(self):
        """Initialize all JARVIS modules"""
        print("🔄 Initializing JARVIS modules...")
        
        # Voice modules (if enabled)
        if self.settings.voice.enabled:
            print("🎤 Initializing voice...")
            self.stt = SpeechRecognizer(self.settings.voice)
            self.tts = TextToSpeech(self.settings.voice)
            self.wake_detector = WakeWordDetector(self.settings.voice.wake_word)
        else:
            self.stt = None
            self.tts = None
            self.wake_detector = None
        
        # LLM
        print("🧠 Initializing LLM...")
        self.llm = OllamaClient(self.settings.llm)
        
        # Automation
        print("⚙️ Initializing automation...")
        self.app_manager = AppManager()
        self.code_manager = CodeManager()
        self.system_manager = SystemManager()
        
        # Web cache
        print("🌐 Initializing web cache...")
        self.web_cache = WebCache(self.settings.web.cache_path)
        
        # Skills
        print("🔧 Loading skills...")
        self.skills = SkillRegistry()
        self.skills.load_builtin_skills()
        
        print("✅ JARVIS ready!")
    
    def set_state(self, new_state: State):
        """Change state and notify listeners"""
        old_state = self.state
        self.state = new_state
        for callback in self.state_callbacks:
            callback(old_state, new_state)
    
    def run(self):
        """Main voice-controlled loop"""
        self.running = True
        
        if not self.settings.voice.enabled:
            print("Voice disabled. Use --interactive for text mode.")
            return
        
        self.speak("JARVIS online and ready.")
        
        while self.running:
            try:
                # Wait for wake word
                self.set_state(State.IDLE)
                print("👂 Listening for wake word...")
                
                if self.wake_detector.listen():
                    self.set_state(State.LISTENING)
                    self.speak("Yes?")
                    
                    # Listen for command
                    command = self.stt.listen()
                    
                    if command:
                        self.process_command_sync(command)
                        
            except Exception as e:
                print(f"Error: {e}")
                self.set_state(State.ERROR)
                time.sleep(1)
    
    def run_interactive(self):
        """Interactive text mode"""
        self.running = True
        print("\n🤖 JARVIS Interactive Mode")
        print("Type 'exit' or 'quit' to stop")
        print("-" * 40)
        
        while self.running:
            try:
                command = input("\nYou: ").strip()
                
                if command.lower() in ["exit", "quit", "bye"]:
                    self.speak("Goodbye!")
                    break
                
                if command:
                    response = asyncio.run(self.process_command(command))
                    print(f"\nJARVIS: {response}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    async def process_command(self, command: str) -> str:
        """Process a command and return response"""
        self.set_state(State.PROCESSING)
        self.context.last_command = command
        
        # Check for skill triggers first
        skill_result = self.skills.execute(command, self.context)
        if skill_result:
            response = skill_result
        else:
            # Use LLM for general queries
            response = await self._llm_process(command)
        
        self.context.last_response = response
        self.set_state(State.RESPONDING)
        self.speak(response)
        
        return response
    
    def process_command_sync(self, command: str) -> str:
        """Synchronous wrapper for process_command"""
        return asyncio.run(self.process_command(command))
    
    async def _llm_process(self, command: str) -> str:
        """Process command through LLM with tool access"""
        # Check for automation commands
        lower_cmd = command.lower()
        
        # App management
        if any(word in lower_cmd for word in ["open", "launch", "start"]):
            for app in self.app_manager.known_apps:
                if app in lower_cmd:
                    result = self.app_manager.open_app(app)
                    return f"I've {result}"
        
        if any(word in lower_cmd for word in ["close", "quit", "exit"]) and "app" in lower_cmd:
            for app in self.app_manager.known_apps:
                if app in lower_cmd:
                    result = self.app_manager.close_app(app)
                    return f"I've {result}"
        
        # System commands
        if "time" in lower_cmd:
            return self.system_manager.get_time()
        
        if "date" in lower_cmd:
            return self.system_manager.get_date()
        
        # Web search (local cache)
        if any(word in lower_cmd for word in ["search", "find", "look up"]):
            query = command.lower().replace("search", "").replace("find", "").replace("look up", "").strip()
            results = self.web_cache.search(query)
            if results:
                return f"I found this in my cache: {results[0]['content'][:500]}..."
            return "I don't have that in my local cache. Would you like me to fetch it online?"
        
        # Code tasks
        if any(word in lower_cmd for word in ["code", "write", "create file"]):
            return "I can help with coding. What would you like me to create?"
        
        # Default to LLM
        return self.llm.chat(command, context=self.context)
    
    def speak(self, text: str):
        """Speak text or print if voice disabled"""
        if self.tts and self.settings.voice.enabled:
            self.tts.speak(text)
        else:
            print(f"JARVIS: {text}")
    
    def shutdown(self):
        """Clean shutdown"""
        self.running = False
        print("🛑 JARVIS shutting down...")
        
        if self.tts:
            self.tts.stop()
        if self.stt:
            self.stt.stop()
        if self.web_cache:
            self.web_cache.close()
            