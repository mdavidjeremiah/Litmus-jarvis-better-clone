"""
Speech-to-Text module using SpeechRecognition library
"""
import speech_recognition as sr
from typing import Optional
from jarvis.config.settings import VoiceSettings
class SpeechRecognizer:
    """Offline-capable speech recognition"""
    
    def __init__(self, settings: VoiceSettings):
        self.settings = settings
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Configure recognizer
        self.recognizer.energy_threshold = settings.energy_threshold
        self.recognizer.pause_threshold = settings.pause_threshold
        self.recognizer.phrase_threshold = settings.phrase_threshold
        
        # Calibrate for ambient noise
        self._calibrate()
    
    def _calibrate(self):
        """Calibrate microphone for ambient noise"""
        print("🎤 Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Calibration complete")
    
    def listen(self, timeout: Optional[int] = None, phrase_time_limit: Optional[int] = None) -> Optional[str]:
        """
        Listen for speech and return transcribed text.
        
        Args:
            timeout: Maximum time to wait for speech (seconds)
            phrase_time_limit: Maximum duration of phrase (seconds)
        
        Returns:
            Transcribed text or None if no speech detected
        """
        try:
            with self.microphone as source:
                print("👂 Listening...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
            
            print("🧠 Processing speech...")
            
            # Try offline recognition first (CMU Sphinx - requires pocketsphinx)
            try:
                text = self.recognizer.recognize_sphinx(audio)
                print(f"📝 Heard (offline): {text}")
                return text
            except sr.UnknownValueError:
                # Fall back to online Google recognition if available
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"📝 Heard: {text}")
                    return text
                except sr.RequestError:
                    print("❌ Speech recognition unavailable")
                    return None
            except Exception as e:
                print(f"❌ Recognition error: {e}")
                return None
                
        except sr.WaitTimeoutError:
            print("⏱️ Listening timeout")
            return None
        except Exception as e:
            print(f"❌ Microphone error: {e}")
            return None
    
    def stop(self):
        """Cleanup resources"""
        pass
