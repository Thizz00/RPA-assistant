import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from ui.ui_components import (
        render_header, 
        render_sidebar, 
        render_loading_spinner,
        render_error_message,
        render_warning_message
    )
    from chat.chat_logic import (
        initialize_chat,
        send_message,
        display_chat_history,
    )
except ImportError as e:
    st.error(f"❌ Import error: {e}")
    st.stop()

def main():
    """Main application function"""
    
    try:
        st.set_page_config(
            page_title="RPA Code Assistant",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
      
        with render_loading_spinner("Initializing chat..."):
            initialize_chat()

        if not st.session_state.get('api_key'):
            render_warning_message("API key not found in .env file")
        
        render_header()
        render_sidebar()
        
        chat_container = st.container()
        
        with chat_container:
            if st.session_state.messages:
                display_chat_history()
            else:
                st.markdown("""
                <div style='text-align: center; padding: 2rem; margin: 2rem 0;'>
                    <h3>👋 Welcome to RPA Code Assistant!</h3>
                    <p>I'm your expert in automation and RPA. Ask me anything about:</p>
                    <p>🐍 Python automation • 🌐 Web scraping • 📊 Data processing • 📧 Email automation • 🛢️ Multi-database support</p>
                    <p><strong>What would you like to automate today?</strong></p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if prompt := st.chat_input("Ask me about RPA and automation..."):
            send_message(prompt)
            st.rerun()
        
    except Exception as e:
        render_error_message(f"Error in main function: {str(e)}")
        st.write("**Stack trace:**")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()