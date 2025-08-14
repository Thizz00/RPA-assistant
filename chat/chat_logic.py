import streamlit as st
from typing import List, Dict
import os

try:
    from core.api_client import get_api_client
    from core.config import load_config
except ImportError as e:
    st.error(f"Import error in chat_logic: {e}")
    def get_api_client():
        return None
    def load_config():
        return None

def initialize_chat():
    """Initialize chat and session state"""
    config = load_config()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'api_key' not in st.session_state:
        api_key = os.getenv("OPENROUTER_API_KEY") or ""
        st.session_state.api_key = api_key
    
    if 'pending_prompt' not in st.session_state:
        st.session_state.pending_prompt = None

def prepare_messages() -> List[Dict[str, str]]:
    """Prepare messages for API sending"""
    config = load_config()
    
    messages = [
        {
            "role": "system",
            "content": config.SYSTEM_PROMPT
        }
    ]
    
    recent_messages = st.session_state.messages[-10:] if len(st.session_state.messages) > 10 else st.session_state.messages
    messages.extend(recent_messages)
    
    return messages

def send_message(user_input: str) -> None:
    """Send message and handle response"""
    from ui.ui_components import render_error_message
    
    if not st.session_state.get('api_key'):
        render_error_message("Please add OPENROUTER_API_KEY to your .env file")
        return
    
    st.session_state.messages.append({
        "role": "user", 
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)
    
    messages = prepare_messages()
    
    try:
        client = get_api_client()
        
        if not client.validate_api_key():
            render_error_message("Invalid API key in .env file")
            st.session_state.messages.pop()
            return
        
    except Exception as e:
        render_error_message(f"API connection error: {str(e)}")
        st.session_state.messages.pop()
        return
    
    try:
        with st.chat_message("assistant"):
            with st.spinner("🤖 Generating response..."):
                message_placeholder = st.empty()
                full_response = ""
                
                for chunk in client.create_chat_completion(messages, stream=True):
                    if chunk:
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▊")
                
                message_placeholder.markdown(full_response)
        
        if full_response.strip():
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })
        else:
            render_error_message("Received empty response from API")
            st.session_state.messages.pop()
            
    except Exception as e:
        render_error_message(f"Error generating response: {str(e)}")
        st.session_state.messages.pop()

def handle_quick_prompt():
    """Handle quick prompts from UI"""
    if st.session_state.get('pending_prompt'):
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None
        send_message(prompt)

def display_chat_history():
    """Display chat history"""
    for message in st.session_state.messages:
        if message['role'] == 'user':
            with st.chat_message("user"):
                st.markdown(message['content'])
        else:
            with st.chat_message("assistant"):
                if '```' in message['content']:
                    parts = message['content'].split('```')
                    for i, part in enumerate(parts):
                        if i % 2 == 0:  # Text parts
                            if part.strip():
                                st.markdown(part)
                        else:  # Code parts
                            lines = part.split('\n')
                            language = lines[0] if lines[0] in ['python', 'javascript', 'bash', 'sql'] else 'python'
                            code = '\n'.join(lines[1:]) if lines[0] in ['python', 'javascript', 'bash', 'sql'] else part
                            st.code(code, language=language)
                else:
                    st.markdown(message['content'])