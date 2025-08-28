from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class AppConfig:
    """RPA Code Assistant application configuration"""
    
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    MODEL_NAME: str = "agentica-org/deepcoder-14b-preview:free"
    
    APP_TITLE: str = "🤖 RPA Code Assistant"
    APP_DESCRIPTION: str = "Intelligent assistant for RPA coding and automation"
    MAX_TOKENS: int = 6000
    TEMPERATURE: float = 0.7
    
    CUSTOM_CSS: str = """
    <style>
        .main {
            padding-top: 0rem;
        }
        
        .stApp > header {
            background-color: transparent;
        }
        
        .chat-message {
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 4px solid;
        }
        
        .user-message {
            background-color: #e3f2fd;
            border-left-color: #2196f3;
        }
        
        .assistant-message {
            background-color: #f3e5f5;
            border-left-color: #9c27b0;
        }
        
        .sidebar .sidebar-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        .rpa-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border-left: 5px solid #667eea;
            transition: transform 0.3s ease;
        }
        
        .rpa-card:hover {
            transform: translateY(-5px);
        }
        
        .metric-card {
            background: linear-gradient(135deg, #ff6b6b 0%, #ffd93d 100%);
            color: white;
            border-radius: 15px;
            padding: 1rem;
            text-align: center;
            margin: 0.5rem;
        }
        
        .code-block {
            background: #1e1e1e;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            border: 1px solid #333;
        }
    </style>
    """
    
    @property
    def SYSTEM_PROMPT(self) -> str:
        """Load system prompt from file"""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'system_prompt.txt')
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            return """You are an expert RPA assistant specializing in automation and coding. 
            Provide complete, working code with proper error handling and documentation."""

def load_config() -> AppConfig:
    """Load application configuration"""
    return AppConfig()

CONFIG = load_config()