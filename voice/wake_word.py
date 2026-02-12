"""
Wake word detection for JARVIS
"""
import threading
import time
from typing import Callable, Optional
class WakeWordDetector:
    """
    Wake word detection using Porcupine or simple audio detection.
    Falls back to push-to-talk mode if Porcupine is not available.
    """
    
    def __init__(self, wake_word: str = "jarvis"):
        self.wake_word = wake_word.lower()
        self.porcupine = None
        self.pa = None
        self.audio_stream = None
        self.callback: Optional[Callable] = None
        
        self._try_init_porcupine()
    
    def _try_init_porcupine(self):
        """Try to initialize Porcupine for wake word detection"""
        try:
            import pvporcupine
            import pyaudio
            
            # Use built-in keywords or custom model
            self.porcupine = pvporcupine.create(
                keywords=["jarvis", "computer", "hey google"],
                sensitivities=[0.5, 0.5, 0.5]
            )
            
            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
            print("✅ Porcupine wake word detection active")
            
        except ImportError:
            print("⚠️ Porcupine not available, using push-to-talk mode")
        except Exception as e:
            print(f"⚠️ Wake word init error: {e}")
            self.porcupine = None
    
    def listen(self, timeout: Optional[int] = None) -> bool:
        """
        Listen for wake word.
        
        Returns:
            True if wake word detected, False otherwise
        """
        if self.porcupine and self.audio_stream:
            return self._listen_porcupine(timeout)
        else:
            return self._listen_fallback()
    
    def _listen_porcupine(self, timeout: Optional[int]) -> bool:
        """Listen using Porcupine"""
        start_time = time.time()
        
        while True:
            if timeout and (time.time() - start_time) > timeout:
                return False
            
            try:
                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = [int.from_bytes(pcm[i:i+2], byteorder='little', signed=True) 
                       for i in range(0, len(pcm), 2)]
                
                keyword_index = self.porcupine.process(pcm)
                
                if keyword_index >= 0:
                    print(f"🔔 Wake word detected!")
                    return True
                    
            except Exception as e:
                print(f"Wake word error: {e}")
                return False
    
    def _listen_fallback(self) -> bool:
        """
        Fallback: Just wait for any audio input (push-to-talk style)
        or return True immediately for testing.
        """
        print(f"⚠️ Push-to-talk mode: Press Enter to activate...")
        input()
        return True
    
    def set_callback(self, callback: Callable):
        """Set callback for wake word detection"""
        self.callback = callback
    
    def stop(self):
        """Cleanup resources"""
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if self.pa:
            self.pa.terminate()
        if self.porcupine:
            self.porcupine.delete()
