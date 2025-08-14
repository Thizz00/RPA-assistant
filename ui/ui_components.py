import streamlit as st
from typing import Dict

def render_header():
    """Render application header"""
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='color: #667eea; font-size: 3rem; margin-bottom: 0;'>🤖 RPA Code Assistant</h1>
        <p style='color: #666; font-size: 1.2rem; margin-top: 0;'>
            Your expert in automation and RPA
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar with options"""
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        if st.session_state.get('api_key'):
            st.success("🔑 API Key loaded from .env")
        else:
            st.error("🔑 No API Key found in .env")
        
        st.markdown("---")
        st.markdown("## 🧹 Cleaning")

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
 
        render_model_info()

def render_model_info():
    """Render model information"""
    st.markdown("## 🧠 Model")
    st.info("Specializing in coding and automation")

def render_chat_message(message: Dict[str, str], is_user: bool = True):
    """Render single chat message"""
    
    if is_user:
        with st.chat_message("user"):
            st.markdown(message['content'])
    else:
        with st.chat_message("assistant"):
            if '```' in message['content']:
                format_code_response(message['content'])
            else:
                st.markdown(message['content'])

def format_code_response(content: str):
    """Format response with code"""
    parts = content.split('```')
    
    for i, part in enumerate(parts):
        if i % 2 == 0: 
            if part.strip():
                st.markdown(part)
        else: 
            lines = part.split('\n')
            language = lines[0] if lines[0] in ['python', 'javascript', 'bash', 'sql'] else 'python'
            code = '\n'.join(lines[1:]) if lines[0] in ['python', 'javascript', 'bash', 'sql'] else part
            
            st.code(code, language=language)

def render_loading_spinner(message: str = "Generating code..."):
    """Render loading spinner"""
    return st.spinner(f"🤖 {message}")

def render_success_message(message: str):
    """Render success message"""
    st.success(f"✅ {message}")

def render_error_message(message: str):
    """Render error message"""
    st.error(f"❌ {message}")

def render_info_message(message: str):
    """Render info message"""
    st.info(f"ℹ️ {message}")

def render_warning_message(message: str):
    """Render warning message"""
    st.warning(f"⚠️ {message}")

def render_code_block(code: str, language: str = "python", title: str = None):
    """Render a formatted code block with optional copy button"""
    if title:
        st.markdown(f"**{title}**")
    
    col1, col2 = st.columns([10, 1])
    with col1:
        st.code(code, language=language)
    with col2:
        if st.button("📋", key=f"copy_{hash(code)}", help="Copy code"):
            st.success("Copied!")

def render_metric_card(title: str, value: str, delta: str = None):
    """Render a metric card with optional delta"""
    st.markdown(f"""
    <div class="metric-card">
        <h4>{title}</h4>
        <h2>{value}</h2>
        {f'<p>{delta}</p>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

def render_rpa_tip(tip: str, category: str = "💡 Tip"):
    """Render an RPA tip or best practice"""
    st.markdown(f"""
    <div class="rpa-card">
        <h4>{category}</h4>
        <p>{tip}</p>
    </div>
    """, unsafe_allow_html=True)