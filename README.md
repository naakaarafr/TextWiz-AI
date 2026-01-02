# ✨ TextWiz AI

> Your AI-powered reply expert for every conversation

TextWiz AI is an intelligent conversation assistant that generates perfect replies for any chat scenario. Whether you're flirting, networking professionally, or just chatting with friends, TextWiz analyzes your conversations and suggests contextually appropriate responses in your desired tone.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Features

### Core Capabilities
- **📸 Screenshot Analysis**: Upload chat screenshots and get instant reply suggestions
- **✍️ Text Input**: Paste conversation text directly for analysis
- **🎭 Multiple Moods**: 10 different tones including Flirty, Professional, Humorous, and more
- **📏 Flexible Length**: Choose between Short, Medium, or Long replies
- **🎯 Smart Context**: Add additional context for more personalized suggestions

### Intelligent AI System
- **🤖 Gemini 2.0 Flash**: Powered by Google's latest AI model
- **💾 Smart Caching**: Reduces API calls and improves response times
- **🔄 Auto-Retry**: Automatic retry logic with exponential backoff
- **📊 Rate Limiting**: Built-in quota management to stay within API limits
- **🦙 Ollama Fallback**: Offline mode using local Ollama models when API limits are reached

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))
- (Optional) Ollama installed for offline fallback

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/naakaarafr/TextWiz-AI.git
cd TextWiz-AI
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run Reply_Specialist_AI.py
```

4. **Open your browser**
The app will automatically open at `http://localhost:8501`

## 📦 Dependencies

Create a `requirements.txt` file with:

```txt
streamlit>=1.28.0
google-generativeai>=0.3.0
Pillow>=10.0.0
requests>=2.31.0
```

## 🎮 Usage

### Basic Workflow

1. **Configure API Key**
   - Enter your Gemini API key in the sidebar
   - The key is stored only in your session (not saved permanently)

2. **Choose Input Method**
   - **Screenshot**: Upload a PNG/JPG image of your conversation
   - **Text**: Paste the conversation text directly

3. **Select Mood & Settings**
   - Choose from 10 different conversation tones
   - Set reply length (Short/Medium/Long)
   - Adjust number of suggestions (1-5)

4. **Add Context (Optional)**
   - Provide additional information about the conversation
   - Example: "This is my boss" or "We're discussing a date"

5. **Generate Replies**
   - Click "✨ Generate Replies"
   - Review the AI-generated suggestions
   - Copy and personalize your favorite option

### Available Moods

| Mood | Use Case |
|------|----------|
| 🔥 Flirty & Playful | Dating, romantic interests |
| ❤️ Romantic & Sweet | Partners, expressing affection |
| 😎 Casual & Friendly | Friends, casual conversations |
| 💼 Professional & Formal | Work emails, formal communication |
| 🤝 Business Networking | LinkedIn, professional connections |
| 😂 Humorous & Witty | Making people laugh |
| 🧊 Cold & Detached | Setting boundaries |
| 🔥 Bold & Confident | Assertive communication |
| 🤔 Thoughtful & Deep | Meaningful conversations |
| 😌 Supportive & Caring | Emotional support |

## 🦙 Ollama Integration (Optional)

For offline functionality and unlimited usage:

1. **Install Ollama**
   ```bash
   # Visit https://ollama.com and download for your OS
   ```

2. **Pull a model**
   ```bash
   ollama pull llama2
   # or
   ollama pull mistral
   ```

3. **Start Ollama**
   ```bash
   ollama serve
   ```

4. **Select Model in TextWiz**
   - The app will automatically detect available Ollama models
   - Select your preferred fallback model in the sidebar

TextWiz will automatically use Ollama when:
- Gemini API quota is exceeded
- Network issues occur
- You prefer offline operation

## ⚙️ Advanced Features

### Caching System
- Responses are cached for 1 hour
- Reduces API calls for repeated queries
- Clear cache anytime from the sidebar

### Rate Limiting
- Monitors requests per minute
- Visual quota health indicator
- Automatic throttling to prevent quota exhaustion

### Error Handling
- Automatic retry with exponential backoff
- Graceful fallback to Ollama
- Clear error messages and suggestions

## 🏗️ Project Structure

```
TextWiz-AI/
│
├── Reply_Specialist_AI.py    # Main application
├── requirements.txt           # Python dependencies
├── README.md                  # Documentation
└── .gitignore                # Git ignore rules
```

## 🔒 Privacy & Security

- **API Keys**: Never committed to version control, stored only in session
- **Data**: Conversations are not stored permanently
- **Cache**: Cleared automatically after 1 hour
- **Local Processing**: Option to use Ollama for fully offline operation

## 🛠️ Configuration

### Environment Variables (Optional)

You can set your API key as an environment variable:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

Then modify the code to read from environment:

```python
import os
api_key = os.getenv('GEMINI_API_KEY', '')
```

### Customization

Edit these parameters in `Reply_Specialist_AI.py`:

```python
# Model configuration
self.primary_model = "gemini-2.0-flash-exp"
self.max_retries = 3
self.base_delay = 3

# Cache duration
timedelta(hours=1)  # Change cache validity period

# Rate limits
if len(st.session_state.request_history) >= 50:  # Adjust limit
```

## 🐛 Troubleshooting

### Common Issues

**"Cannot connect to Ollama"**
- Ensure Ollama is running: `ollama serve`
- Check if port 11434 is available

**"Invalid API key"**
- Verify your key at [Google AI Studio](https://aistudio.google.com/apikey)
- Ensure no extra spaces in the key

**"Response was blocked"**
- Content triggered safety filters
- Try rephrasing or use Ollama fallback

**"Quota exceeded"**
- Wait a few minutes for quota reset
- Use Ollama as fallback
- Reduce number of suggestions

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Add comments for complex logic
- Test with both Gemini and Ollama
- Update README for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini**: For providing the powerful AI API
- **Ollama**: For enabling local AI capabilities
- **Streamlit**: For the amazing web framework
- **Community**: For feedback and contributions

<div align="center">

[Report Bug](https://github.com/naakaarafr/TextWiz-AI/issues) · [Request Feature](https://github.com/naakaarafr/TextWiz-AI/issues) · [Documentation](https://github.com/naakaarafr/TextWiz-AI)

</div>
