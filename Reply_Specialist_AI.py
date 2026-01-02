import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import hashlib
from datetime import datetime, timedelta
import requests
import json
import base64
import io

# Page configuration
st.set_page_config(
    page_title="TextWiz AI",
    page_icon="✨",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .agent-status {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for caching and rate limiting
if 'request_cache' not in st.session_state:
    st.session_state.request_cache = {}
if 'request_history' not in st.session_state:
    st.session_state.request_history = []
if 'retry_count' not in st.session_state:
    st.session_state.retry_count = 0

# Function to encode image to base64
def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Function to call Ollama API
def generate_with_ollama(model, prompt, image_base64=None):
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    if image_base64:
        payload["images"] = [image_base64]
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to Ollama. Make sure Ollama is running (ollama serve)")
    except Exception as e:
        raise Exception(f"Ollama error: {str(e)}")

# Function to check Ollama availability
def check_ollama():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return True, [model["name"] for model in models]
        return False, []
    except:
        return False, []

# AI Agent System Class
class GeminiAgentSystem:
    def __init__(self):
        self.primary_model = "gemini-2.0-flash-exp"
        self.max_retries = 3
        self.base_delay = 3
        self.use_ollama_fallback = False
        self.ollama_model = None
        
    def get_cache_key(self, prompt, mood, length):
        """Generate cache key for request"""
        content = f"{prompt}_{mood}_{length}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def check_cache(self, cache_key):
        """Check if response exists in cache"""
        if cache_key in st.session_state.request_cache:
            cached_data = st.session_state.request_cache[cache_key]
            # Cache valid for 1 hour
            if datetime.now() - cached_data['timestamp'] < timedelta(hours=1):
                return cached_data['response']
        return None
    
    def save_to_cache(self, cache_key, response):
        """Save response to cache"""
        st.session_state.request_cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now()
        }
    
    def rate_limit_check(self):
        """Check if we're making too many requests"""
        now = datetime.now()
        # Keep only requests from last minute
        st.session_state.request_history = [
            req_time for req_time in st.session_state.request_history 
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Gemini free tier: 15 RPM for flash, 60 RPM for 2.0-flash-exp
        # Set conservative limit at 50 to stay safe
        if len(st.session_state.request_history) >= 50:
            return False, 60 - (now - st.session_state.request_history[0]).seconds
        return True, 0
    
    def log_request(self):
        """Log request timestamp"""
        st.session_state.request_history.append(datetime.now())
    
    def optimize_prompt(self, prompt, num_suggestions):
        """Optimize prompt to reduce token usage"""
        # Reduce prompt length for quota efficiency
        if num_suggestions > 3:
            optimized = prompt.replace("Add a brief explanation (1 line) after each suggestion about why it works", 
                                     "Add very brief reason")
        else:
            optimized = prompt
        return optimized
    
    def fallback_to_next_model(self):
        """Enable Ollama fallback"""
        self.use_ollama_fallback = True
        return "Ollama"
    
    def exponential_backoff(self, attempt):
        """Calculate wait time with exponential backoff"""
        return min(self.base_delay * (2 ** attempt), 60)
    
    def generate_with_retry(self, prompt, image=None, num_suggestions=3):
        """Main agent function with intelligent retry logic"""
        
        # Step 1: Check cache first
        cache_key = self.get_cache_key(prompt, self.primary_model, num_suggestions)
        cached_response = self.check_cache(cache_key)
        if cached_response:
            st.info("✨ Using cached response")
            return cached_response, "cache"
        
        # Step 2: Rate limit check (silent)
        can_proceed, wait_time = self.rate_limit_check()
        if not can_proceed:
            time.sleep(wait_time)
        
        # Step 3: Optimize prompt
        optimized_prompt = self.optimize_prompt(prompt, num_suggestions)
        
        last_error = None
        
        # Step 4: Try Gemini 2.0 Flash
        for attempt in range(self.max_retries):
            try:
                st.info(f"🤖 Generating with Gemini 2.0 Flash...")
                
                # Configure model with safety settings
                genai.configure(api_key=st.session_state.api_key)
                
                generation_config = {
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "max_output_tokens": 2048,
                }
                
                model = genai.GenerativeModel(
                    model_name=self.primary_model,
                    generation_config=generation_config
                )
                
                # Generate response
                if image:
                    response = model.generate_content([optimized_prompt, image])
                else:
                    response = model.generate_content(optimized_prompt)
                
                # Check if response was blocked
                if not response.text:
                    raise Exception("Response was blocked or empty")
                
                result = response.text
                
                # Log successful request
                self.log_request()
                
                # Save to cache
                self.save_to_cache(cache_key, result)
                
                st.success(f"✅ Success!")
                return result, self.primary_model
                
            except Exception as e:
                error_msg = str(e)
                last_error = error_msg
                
                # Handle different error types silently for first attempts
                if attempt < self.max_retries - 1:
                    if "429" in error_msg or "quota" in error_msg.lower() or "resource_exhausted" in error_msg.lower():
                        wait_time = self.exponential_backoff(attempt)
                        time.sleep(wait_time)
                    elif "rate" in error_msg.lower() or "limit" in error_msg.lower():
                        wait_time = self.exponential_backoff(attempt)
                        time.sleep(wait_time)
                    else:
                        wait_time = self.exponential_backoff(attempt)
                        time.sleep(wait_time)
                else:
                    # Last attempt - check for fallback
                    if "429" in error_msg or "quota" in error_msg.lower():
                        if self.ollama_model:
                            st.info("🔄 Switching to Ollama fallback...")
                            break
                    elif "blocked" in error_msg.lower() or "safety" in error_msg.lower():
                        st.error("🛡️ Content was blocked by safety filters")
                        if self.ollama_model:
                            st.info("🔄 Trying with Ollama...")
                            break
                        raise Exception("Content blocked by safety filters")
                    elif "api" in error_msg.lower() and "key" in error_msg.lower():
                        raise Exception("Invalid API key. Please check your Gemini API key.")
        
        # Step 5: Try Ollama as fallback
        if self.ollama_model:
            try:
                st.info(f"🦙 Using Ollama ({self.ollama_model})...")
                
                # Encode image if present
                image_base64 = None
                if image:
                    image_base64 = encode_image(image)
                
                result = generate_with_ollama(self.ollama_model, optimized_prompt, image_base64)
                
                if result:
                    result_with_note = result + "\n\n*Generated using Ollama (local)*"
                    self.save_to_cache(cache_key, result_with_note)
                    st.success("✅ Success with Ollama!")
                    return result_with_note, f"Ollama ({self.ollama_model})"
            except Exception as e:
                st.error(f"❌ Fallback failed: {str(e)}")
        
        # If everything fails
        error_details = f"""
**Unable to generate replies.**

**Last error:** {last_error[:200] if last_error else 'Unknown error'}

**Suggestions:**
1. Wait a moment and try again
2. Check your API key at: https://aistudio.google.com/apikey
3. Reduce the number of suggestions
4. Install Ollama for offline mode: https://ollama.com
"""
        raise Exception(error_details)

# Initialize agent system
agent = GeminiAgentSystem()

# Header
st.markdown('<h1 class="main-header">✨ TextWiz AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your AI-powered reply expert for every conversation</p>', unsafe_allow_html=True)

# Sidebar for API Key and Settings
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password", help="Get your API key from Google AI Studio")
    
    if api_key:
        st.session_state.api_key = api_key
        st.success("✅ Gemini API Key configured")
    
    # Check Ollama availability
    ollama_available, ollama_models = check_ollama()
    
    if ollama_available and ollama_models:
        st.success("✅ Ollama is available (fallback)")
        agent.ollama_model = st.selectbox(
            "Ollama Fallback Model",
            options=ollama_models,
            help="Used when Gemini quota is exceeded"
        )
    else:
        st.info("💡 Install Ollama for offline fallback")
        agent.ollama_model = None
    
    st.divider()
    
    st.header("🤖 AI Agent Status")
    if 'request_history' in st.session_state:
        recent_requests = len([t for t in st.session_state.request_history 
                              if datetime.now() - t < timedelta(minutes=1)])
        st.metric("Requests (last min)", f"{recent_requests}/50")
        
        # Show rate limit warning
        if recent_requests > 40:
            st.warning("⚠️ Approaching rate limit!")
        elif recent_requests > 30:
            st.info("ℹ️ Moderate usage")
        else:
            st.success("✅ Good quota health")
    
    cached_items = len(st.session_state.request_cache)
    st.metric("Cached Responses", cached_items)
    
    if st.button("🗑️ Clear Cache"):
        st.session_state.request_cache = {}
        st.session_state.request_history = []
        st.success("Cache cleared!")
    
    st.divider()
    
    st.header("📊 Reply Style")
    mood = st.selectbox(
        "Select Mood/Tone",
        [
            "🔥 Flirty & Playful",
            "❤️ Romantic & Sweet",
            "😎 Casual & Friendly",
            "💼 Professional & Formal",
            "🤝 Business Networking",
            "😂 Humorous & Witty",
            "🧊 Cold & Detached",
            "🔥 Bold & Confident",
            "🤔 Thoughtful & Deep",
            "😌 Supportive & Caring"
        ]
    )
    
    reply_length = st.select_slider(
        "Reply Length",
        options=["Short", "Medium", "Long"],
        value="Medium"
    )
    
    num_suggestions = st.slider(
        "Number of Suggestions",
        min_value=1,
        max_value=5,
        value=3,
        help="Agent will auto-reduce if quota limited"
    )
    
    st.divider()
    st.markdown("**✨ Features:**")
    st.markdown("- 🎯 Smart caching")
    st.markdown("- 🤖 Gemini 2.0 Flash")
    st.markdown("- 🦙 Ollama fallback")
    st.markdown("- 🔄 Auto-retry on errors")

# Main content area
tab1, tab2 = st.tabs(["📸 Upload Screenshot", "✍️ Enter Text"])

conversation_text = None
uploaded_image = None

with tab1:
    st.subheader("Upload Chat Screenshot")
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a screenshot of your conversation"
    )
    
    if uploaded_file:
        uploaded_image = Image.open(uploaded_file)
        st.image(uploaded_image, caption="Uploaded Screenshot", use_container_width=True)

with tab2:
    st.subheader("Enter Conversation Text")
    conversation_text = st.text_area(
        "Paste your conversation here",
        height=200,
        placeholder="Example:\nThem: Hey! How was your day?\nYou: It was good, how about yours?\nThem: Pretty busy but good!"
    )

# Additional context
with st.expander("➕ Add Additional Context (Optional)"):
    additional_context = st.text_area(
        "Any specific details or context?",
        placeholder="E.g., This is my boss, we're discussing a project deadline...",
        height=100
    )

if not additional_context:
    additional_context = ""

# Generate replies button
if st.button("✨ Generate Replies", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please configure your Gemini API key first!")
    elif not uploaded_image and not conversation_text:
        st.warning("Please upload a screenshot or enter conversation text!")
    else:
        with st.spinner("✨ Creating perfect replies..."):
            try:
                # Prepare the prompt
                mood_instructions = {
                    "🔥 Flirty & Playful": "Generate flirty, playful, and charming replies with subtle teasing and romantic undertones. Be confident and engaging.",
                    "❤️ Romantic & Sweet": "Generate sweet, romantic, and heartfelt replies that show genuine affection and care.",
                    "😎 Casual & Friendly": "Generate casual, friendly, and relaxed replies as if talking to a good friend.",
                    "💼 Professional & Formal": "Generate professional, formal, and polished replies suitable for work environments.",
                    "🤝 Business Networking": "Generate professional networking replies that build rapport and maintain business relationships.",
                    "😂 Humorous & Witty": "Generate funny, witty, and clever replies that will make them laugh.",
                    "🧊 Cold & Detached": "Generate brief, distant, and emotionally detached replies.",
                    "🔥 Bold & Confident": "Generate bold, assertive, and confident replies that command respect.",
                    "🤔 Thoughtful & Deep": "Generate thoughtful, introspective, and meaningful replies.",
                    "😌 Supportive & Caring": "Generate supportive, empathetic, and caring replies that show understanding."
                }
                
                length_guide = {
                    "Short": "Keep replies brief (1-2 sentences)",
                    "Medium": "Make replies moderate length (2-3 sentences)",
                    "Long": "Create detailed, expressive replies (3-5 sentences)"
                }
                
                prompt = f"""You are an expert communication specialist. Analyze the conversation and generate {num_suggestions} different reply suggestions.

Mood/Tone: {mood_instructions[mood]}
Reply Length: {length_guide[reply_length]}

Additional Context: {additional_context if additional_context else "None"}

Instructions:
1. Read the conversation carefully
2. Generate {num_suggestions} unique replies matching the mood and length
3. Make replies natural and contextually appropriate
4. Number each suggestion
5. Add brief reason after each

Format:
**Reply 1:**
[Your reply]
*Why it works: [Brief explanation]*

**Reply 2:**
[Your reply]
*Why it works: [Brief explanation]*

"""
                
                # Add conversation context
                if uploaded_image:
                    prompt += "\n\nAnalyze the conversation in the image."
                    if conversation_text:
                        prompt += f"\n\nAdditional text:\n{conversation_text}"
                else:
                    prompt += f"\n\nConversation:\n{conversation_text}"
                
                # Use agent system to generate
                response_text, used_model = agent.generate_with_retry(
                    prompt,
                    uploaded_image,
                    num_suggestions
                )
                
                # Display results
                st.success("✅ Replies generated successfully!")
                st.divider()
                
                st.markdown("### 💬 Suggested Replies")
                st.markdown(response_text)
                
                # Tips
                st.divider()
                st.markdown("**👆 Tip:** Copy any reply and personalize it to match your style!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("""
                **Quick fixes:**
                - Wait a moment and try again
                - Reduce number of suggestions
                - Use shorter text
                - Check your API key
                """)

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>✨ <strong>TextWiz AI</strong></p>
        <p>🤖 Powered by Gemini 2.0 Flash | 🦙 Ollama fallback available</p>
        <p>Smart caching • Auto-retry • Multiple moods</p>
    </div>
""", unsafe_allow_html=True)