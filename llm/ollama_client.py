"""
Ollama LLM client for local inference
"""
import ollama
from typing import List, Dict, Optional, Generator
import json
from jarvis.config.settings import LLMSettings
class OllamaClient:
    """Client for Ollama local LLM inference"""
    
    def __init__(self, settings: LLMSettings):
        self.settings = settings
        self.client = ollama.Client(host=settings.host)
        self.conversation_history: List[Dict[str, str]] = []
        
        # Verify connection
        self._check_connection()
    
    def _check_connection(self):
        """Check if Ollama is running"""
        try:
            self.client.list()
            print(f"✅ Connected to Ollama at {self.settings.host}")
        except Exception as e:
            print(f"⚠️ Cannot connect to Ollama: {e}")
            print("Make sure Ollama is installed and running:")
            print("  curl -fsSL https://ollama.com/install.sh | sh")
            print(f"  ollama pull {self.settings.model}")
    
    def chat(self, message: str, context=None, stream: bool = False) -> str:
        """
        Send a chat message to the LLM.
        
        Args:
            message: User message
            context: Optional conversation context
            stream: If True, yield response chunks
        
        Returns:
            LLM response string
        """
        # Build messages
        messages = [
            {"role": "system", "content": self.settings.system_prompt}
        ]
        
        # Add conversation history
        messages.extend(self.conversation_history[-5:])  # Keep last 5 exchanges
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        try:
            if stream:
                return self._stream_chat(messages)
            else:
                response = self.client.chat(
                    model=self.settings.model,
                    messages=messages,
                    options={
                        "temperature": self.settings.temperature,
                        "num_predict": self.settings.max_tokens
                    }
                )
                
                # Extract response text
                assistant_message = response['message']['content']
                
                # Update history
                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                
                return assistant_message
                
        except Exception as e:
            return f"Error: Could not get response from LLM. {str(e)}"
    
    def _stream_chat(self, messages: List[Dict]) -> Generator[str, None, None]:
        """Stream chat response"""
        try:
            stream = self.client.chat(
                model=self.settings.model,
                messages=messages,
                stream=True,
                options={
                    "temperature": self.settings.temperature,
                    "num_predict": self.settings.max_tokens
                }
            )
            
            full_response = ""
            for chunk in stream:
                text = chunk['message']['content']
                full_response += text
                yield text
            
            # Update history after streaming
            self.conversation_history.append({"role": "user", "content": messages[-1]['content']})
            self.conversation_history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            yield f"Error: {str(e)}"
    
    def generate(self, prompt: str) -> str:
        """
        Simple text generation without conversation history.
        """
        try:
            response = self.client.generate(
                model=self.settings.model,
                prompt=prompt,
                options={
                    "temperature": self.settings.temperature,
                    "num_predict": self.settings.max_tokens
                }
            )
            return response['response']
        except Exception as e:
            return f"Error: {str(e)}"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            models = self.client.list()
            return [m['name'] for m in models['models']]
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def pull_model(self, model_name: str):
        """Download a model"""
        print(f"📥 Downloading {model_name}...")
        try:
            for progress in self.client.pull(model_name, stream=True):
                if 'completed' in progress and 'total' in progress:
                    pct = (progress['completed'] / progress['total']) * 100
                    print(f"\r  Progress: {pct:.1f}%", end='')
            print(f"\n✅ Downloaded {model_name}")
        except Exception as e:
            print(f"\n❌ Error downloading model: {e}")
