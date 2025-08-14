# 🤖 RPA Code Assistant

An intelligent assistant specializing in Robotic Process Automation (RPA) and coding. Built with Streamlit and integrated with OpenRouter API.

## ✨ Features

- 🔧 **RPA Expert**: UiPath, Power Automate, Python
- 🐍 **Python Automation**: Web scraping, GUI automation, Excel file processing
- 💾 **Database Support**: SQL Server, MySQL, PostgreSQL, Oracle
- 📊 **Business Processes**: Report automation, document processing
- 💬 **Interactive Chat**: Streaming responses with ready-to-use code

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/Thizz00/RPA-assistant
cd RPA-assistant
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API**
Create a `.env` file in the root directory:
```env
OPENROUTER_API_KEY=your_api_key_here
```

4. **Run the application**
```bash
streamlit run main.py
```

## 📋 Requirements

- Python 3.8+
- OpenRouter API Key
- Dependencies from `requirements.txt`:
  - streamlit==1.35.0
  - python-dotenv==1.1.1
  - requests==2.32.4

## 🏗️ Project Structure

```
RPA-assistant/
├── main.py                 # Main application file
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
├── chat/
│   └── chat_logic.py      # Chat logic
├── core/
│   ├── api_client.py      # API client
│   └── config.py          # Configuration
└── ui/
│   └── ui_components.py   # UI components
└── prompts/
    └── system_prompt.txt   # Prompts
```

## 💡 Usage Examples

- "Write a Python script for automatic website login"
- "How to automate Excel file processing?"
- "Create a bot for web data scraping"
- "Automate email sending with reports"

## 🔧 Configuration

The application uses **Qwen3 Coder** model through OpenRouter API. You can customize settings in `core/config.py`:

- `MODEL_NAME`: Language model
- `MAX_TOKENS`: Maximum response length
- `TEMPERATURE`: Response creativity

## 📝 License

This project is licensed under the MIT License.