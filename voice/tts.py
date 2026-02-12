"""
Text-to-Speech module using pyttsx3 (fully offline)
"""
import pyttsx3
import threading
import queue
from jarvis.config.settings import VoiceSettings
class TextToSpeech:
    """Offline text-to-speech using system voices"""
    
    def __init__(self, settings: VoiceSettings):
        self.settings = settings
        self.engine = pyttsx3.init()
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        
        # Configure voice
        self._configure_voice()
        
        # Start speech thread
        self.running = True
        self.speech_thread = threading.Thread(target=self._speech_loop, daemon=True)
        self.speech_thread.start()
    
    def _configure_voice(self):
        """Configure voice properties"""
        # Set speech rate
        self.engine.setProperty('rate', self.settings.speech_rate)
        
        # Try to set preferred voice
        voices = self.engine.getProperty('voices')
        
        if self.settings.voice_id:
            for voice in voices:
                if self.settings.voice_id in voice.id:
                    self.engine.setProperty('voice', voice.id)
                    break
        else:
            # Try to find a good English voice
            for voice in voices:
                if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
    
    def _speech_loop(self):
        """Background thread for speech synthesis"""
        while self.running:
            try:
                text = self.speech_queue.get(timeout=0.1)
                self.is_speaking = True
                self.engine.say(text)
                self.engine.runAndWait()
                self.is_speaking = False
            except queue.Empty:
                continue
            except Exception as e:
                print(f"TTS Error: {e}")
                self.is_speaking = False
    
    def speak(self, text: str, block: bool = False):
        """
        Queue text to be spoken.
        
        Args:
            text: Text to speak
            block: If True, wait until speech completes
        """
        if not text:
            return
        
        self.speech_queue.put(text)
        
        if block:
            while self.is_speaking or not self.speech_queue.empty():
                import time
                time.sleep(0.1)
    
    def stop(self):
        """Stop speaking and cleanup"""
        self.running = False
        
        # Clear queue
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break
        
        self.engine.stop()
        self.speech_thread.join(timeout=1)
    
    def list_voices(self):
        """List available voices"""
        voices = self.engine.getProperty('voices')
        for i, voice in enumerate(voices):
            print(f"{i}: {voice.name} ({voice.id}) - {voice.languages if hasattr(voice, 'languages') else 'N/A'}")
        return voices
