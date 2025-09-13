# app.py
import streamlit as st
import groq
import os
from typing import Dict, List

# Set page configuration
st.set_page_config(
    page_title="Personality Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define available models (updated to current Groq models)
MODELS = {
    "Llama-3.1-8B-Instant": "llama-3.1-8b-instant",
    "Llama-3.1-70B-Versatile": "llama-3.1-70b-versatile", 
    "Llama-3.2-1B-Preview": "llama-3.2-1b-preview",
    "Llama-3.2-3B-Preview": "llama-3.2-3b-preview",
    "Llama-3.2-11B-Vision-Preview": "llama-3.2-11b-vision-preview",
    "Llama-3.2-90B-Vision-Preview": "llama-3.2-90b-vision-preview",
    "Mixtral-8x7B-32768": "mixtral-8x7b-32768",
    "Gemma2-9B-It": "gemma2-9b-it"
}

PERSONALITIES = {
    "Math Teacher": {
        "description": "Answers math-related questions only",
        "system_prompt": """You are a math teacher. You only answer questions related to mathematics. 
        If asked about other topics, politely decline to answer and redirect to math topics.
        You explain concepts clearly, provide examples, and help with problem-solving."""
    },
    "Doctor": {
        "description": "Answers health and medical queries only",
        "system_prompt": """You are a medical doctor. You only answer questions related to health, medicine, 
        and human biology. If asked about other topics, politely decline to answer and explain that you 
        can only provide medical information. Always include a disclaimer that you are an AI and not a 
        substitute for professional medical advice."""
    },
    "Travel Guide": {
        "description": "Provides travel advice and tips only",
        "system_prompt": """You are a travel guide. You only answer questions related to travel, destinations, 
        planning trips, cultural information, and travel tips. If asked about other topics, politely decline 
        to answer and suggest travel-related questions instead."""
    },
    "Chef": {
        "description": "Answers cooking and recipe questions only",
        "system_prompt": """You are a professional chef. You only answer questions related to cooking, recipes, 
        ingredients, techniques, and food preparation. If asked about other topics, politely decline to answer 
        and offer cooking advice instead."""
    },
    "Tech Support": {
        "description": "Answers technical troubleshooting queries only",
        "system_prompt": """You are a tech support specialist. You only answer questions related to technology, 
        software, hardware, and troubleshooting technical issues. If asked about other topics, politely decline 
        to answer and redirect to technical questions."""
    },
    "General Assistant": {
        "description": "Answers questions on various topics",
        "system_prompt": """You are a helpful AI assistant. You answer questions on a wide range of topics 
        while being informative and friendly."""
    }
}

class GroqChatbot:
    def __init__(self, api_key: str):
        self.client = groq.Client(api_key=api_key)
    
    def get_response(self, model: str, messages: List[Dict[str, str]]) -> str:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = list(MODELS.keys())[0]
    if "selected_personality" not in st.session_state:
        st.session_state.selected_personality = list(PERSONALITIES.keys())[0]
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""

def display_chat_interface():
    st.title("🤖 Personality Chatbot")
    st.caption("Chat with AI specialists in different fields")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] != "system":  # Don't display system messages
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Check if API key is provided
        if not st.session_state.api_key:
            st.error("Please enter your Groq API key in the sidebar to start chatting")
            st.stop()
            
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            # Get the system prompt for the selected personality
            system_prompt = PERSONALITIES[st.session_state.selected_personality]["system_prompt"]
            
            # Prepare messages for the API (include system prompt and conversation history)
            api_messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (excluding system messages)
            for msg in st.session_state.messages:
                if msg["role"] != "system":
                    api_messages.append(msg)
            
            # Get response from Groq API
            chatbot = GroqChatbot(st.session_state.api_key)
            full_response = chatbot.get_response(
                MODELS[st.session_state.selected_model], 
                api_messages
            )
            
            # Display the response
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

def display_sidebar():
    with st.sidebar:
        st.header("Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            value=st.session_state.api_key,
            help="Get your API key from https://console.groq.com/keys"
        )
        
        if api_key:
            st.session_state.api_key = api_key
        
        # Model selection
        st.session_state.selected_model = st.selectbox(
            "Select AI Model",
            options=list(MODELS.keys()),
            index=list(MODELS.keys()).index(st.session_state.selected_model),
            help="Choose which Groq model to use for generating responses"
        )
        
        # Personality selection
        st.session_state.selected_personality = st.selectbox(
            "Select Chatbot Personality",
            options=list(PERSONALITIES.keys()),
            index=list(PERSONALITIES.keys()).index(st.session_state.selected_personality),
            help="Choose the specialist you want to chat with"
        )
        
        # Display personality description
        st.info(PERSONALITIES[st.session_state.selected_personality]["description"])
        
        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        st.markdown("### About")
        st.markdown("""
        This chatbot uses Groq's fast AI models with specialized personalities:
        - Each personality only answers questions in its field
        - Select different AI models for varying capabilities
        - Conversation history is maintained during your session
        """)
        
        st.markdown("### Model Information")
        st.markdown("""
        - **Llama-3.1-8B-Instant**: Fast, efficient model for general use
        - **Llama-3.1-70B-Versatile**: Powerful model for complex tasks  
        - **Llama-3.2-1B/3B-Preview**: Lightweight models for quick responses
        - **Llama-3.2-11B/90B-Vision-Preview**: Models with image capabilities
        - **Mixtral-8x7B-32768**: Mixture of experts model with wide knowledge
        - **Gemma2-9B-It**: Google's efficient and capable model
        """)

def main():
    initialize_session_state()
    
    if not st.session_state.api_key:
        st.warning("⚠️ Please enter your Groq API key in the sidebar to start chatting")
    
    display_sidebar()
    display_chat_interface()

if __name__ == "__main__":
    main()