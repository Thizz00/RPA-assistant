import streamlit as st
from typing import List, Dict
import os
import re

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
                
                render_message_content(full_response, message_placeholder)
        
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

def render_message_content(content: str, placeholder=None):
    """Render message content with proper LaTeX and code formatting"""
    
    def render_to_target(markdown_content):
        if placeholder:
            placeholder.markdown(markdown_content, unsafe_allow_html=True)
        else:
            st.markdown(markdown_content, unsafe_allow_html=True)
    
    if '```' in content:
        parts = content.split('```')
        rendered_content = ""
        
        for i, part in enumerate(parts):
            if i % 2 == 0: 
                if part.strip():

                    processed_part = process_latex(part)
                    rendered_content += processed_part
            else:  
                lines = part.split('\n')
                language = lines[0] if lines[0] in ['python', 'javascript', 'bash', 'sql', 'html', 'css', 'json', 'xml'] else 'python'
                code = '\n'.join(lines[1:]) if lines[0] in ['python', 'javascript', 'bash', 'sql', 'html', 'css', 'json', 'xml'] else part
                

                rendered_content += f"\n```{language}\n{code}\n```\n"
        
        render_to_target(rendered_content)
    else:
        processed_content = process_latex(content)
        render_to_target(processed_content)

def process_latex(text: str) -> str:
    """Process LaTeX expressions in text"""
    
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
    
    text = re.sub(r'\\boxed\{(.*?)\}', r'\\boxed{\1}', text)
    
    return text

def display_chat_history():
    """Display chat history with proper formatting"""
    for message in st.session_state.messages:
        if message['role'] == 'user':
            with st.chat_message("user"):
                st.markdown(message['content'])
        else:
            with st.chat_message("assistant"):
                render_message_content(message['content'])

def render_message_with_katex(content: str, placeholder=None):
    """
    Alternative rendering method using streamlit-katex for better LaTeX support.
    Requires: pip install streamlit-katex
    """
    try:
        import streamlit_katex as katex
        
        def render_to_target(markdown_content):
            if placeholder:
                placeholder.markdown(markdown_content)
            else:
                st.markdown(markdown_content)
        
        
        if '```' in content:
            parts = content.split('```')
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    if part.strip():
                        if '$' in part or '\\[' in part or '\\(' in part:
                            katex.st_katex(part)
                        else:
                            render_to_target(part)
                else:
                    lines = part.split('\n')
                    language = lines[0] if lines[0] in ['python', 'javascript', 'bash', 'sql'] else 'python'
                    code = '\n'.join(lines[1:]) if lines[0] in ['python', 'javascript', 'bash', 'sql'] else part
                    st.code(code, language=language)
        else:
            if '$' in content or '\\[' in content or '\\(' in content:
                katex.st_katex(content)
            else:
                render_to_target(content)
                
    except ImportError:
        render_message_content(content, placeholder)