import requests
import json
from typing import Iterator
import os
from dotenv import load_dotenv

load_dotenv()

class APIClient:
    """OpenRouter API client for RPA Code Assistant"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = config.OPENROUTER_BASE_URL
        self.model = config.MODEL_NAME
        self.headers = {
            "HTTP-Referer": "https://localhost",
            "X-Title": "RPA Code Assistant",  
            "Content-Type": "application/json"
        }
        self.api_key = os.getenv("OPENROUTER_API_KEY")
    
    def _update_headers(self):
        """Update headers with API key from environment"""
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def validate_api_key(self) -> bool:
        """Validate if the API key is working"""
        try:
            self._update_headers()
            
            if "Authorization" not in self.headers:
                return False
            
            test_data = {
                "model": self.model,
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 10
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=test_data,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"API validation error: {e}")
            return False
    
    def create_chat_completion(self, messages: list, stream: bool = False) -> Iterator[str]:
        """Create a chat completion with streaming support"""
        try:
            self._update_headers()
            
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.config.MAX_TOKENS,
                "temperature": self.config.TEMPERATURE,
                "stream": stream
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                stream=stream,
                timeout=60
            )
            
            response.raise_for_status()
            
            if stream:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            line = line[6:]
                            
                            if line.strip() == '[DONE]':
                                break
                                
                            try:
                                chunk_data = json.loads(line)
                                if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                    delta = chunk_data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
            else:
                response_data = response.json()
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    content = response_data['choices'][0]['message']['content']
                    yield content
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

def get_api_client():
    """Get configured API client instance"""
    from core.config import load_config
    config = load_config()
    return APIClient(config)