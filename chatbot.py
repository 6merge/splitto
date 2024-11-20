import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st

# Load environment variables


load_dotenv()
genai.configure(api_key=os.environ.get("GENAI_API_KEY", ""))

model_name = "gemini-1.5-flash"

# Memory file path
memory_file = "chat_memory.json"

# Define moods/styles
styles = {
    "Jaan Pehchan": "Keep responses natural and conversational. Make sure the language is Hindi and the script is Roman, without any English translation.",
    "Khadoos": "Keep responses clear and professional, almost rude but never crossing the line. Language should be Hindi in Roman script, no English translation.",
    "Dost": "Keep responses warm and supportive. Language should be Hindi in Roman script, no English translation.",
    "Yaar": "Include subtle humor where appropriate. Language should be Hindi in Roman script, no English translation.",
    "Nonchalant legend": "Keep responses brief and to the point, make it like the chatbot dont care about the user at all and give one word or one sentence responses. Language should be Hindi in Roman script, no English translation.",
}

style_names = list(styles.keys())

# Load memory
def load_memory():
    if os.path.exists(memory_file):
        with open(memory_file, "r") as file:
            memory = json.load(file)
            if "context_log" not in memory:
                memory["context_log"] = []
            return memory
    return {"context_log": []}

# Save memory
def save_memory(memory):
    with open(memory_file, "w") as file:
        json.dump(memory, file, indent=4)

# Append context to memory
def append_context(role, content):
    memory["context_log"].append({"role": role, "content": content})
    save_memory(memory)

# Generate AI response
def generate_response(current_style, context_log, user_input):
    dynamic_prompt = (
        f"System: {current_style}\n"
        "The following is a conversation between a user and Splitto, "
        "a chatbot that can communicate in different moods. "
        "Splitto is created by Mayank Raj, who can be found on Instagram and GitHub as 6merge.\n\n"
    )
    for message in context_log:
        dynamic_prompt += f"{message['role']}: {message['content']}\n"
    dynamic_prompt += f"User: {user_input}\nAssistant:"

    try:
        response = genai.generate_text(
            model=model_name,
            prompt=dynamic_prompt,
            temperature=0.7,
            max_output_tokens=100,
        )
        if response and "candidates" in response:
            return response["candidates"][0]["output"]
        return "(No response received)"
    except Exception as e:
        return f"Error: {e}"

# Load memory
memory = load_memory()

# Streamlit UI
st.set_page_config(page_title="Splitto - Mood-based Hindi Chatbot", layout="centered", initial_sidebar_state="collapsed")

# CSS for Chat and Styling
st.markdown(
    """
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f5f6fa;
        }
        .chat-container {
            max-height: 400px;
            overflow-y: auto;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 8px;
            background: #ffffff;
            margin: 0 auto;
        }
        .chat-bubble {
            margin: 10px 0;
            padding: 15px;
            border-radius: 20px;
            max-width: 75%;
            font-size: 16px;
            line-height: 1.5;
            display: inline-block;
        }
        .user-bubble {
            background-color: #4caf50;
            color: white;
            align-self: flex-end;
        }
        .bot-bubble {
            background-color: #e3f2fd;
            color: black;
        }
        .centered-input {
            margin: 0 auto;
            width: 50%;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🤖 Splitto: Mood-based Hindi Chatbot")

# Tone Selector
selected_tone = st.selectbox("Choose Chatbot Mood", style_names)
current_tone = styles[selected_tone]

# Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for message in st.session_state.chat_history:
    role_class = "user-bubble" if message["role"] == "User" else "bot-bubble"
    st.markdown(
        f"<div class='chat-bubble {role_class}'>{message['content']}</div>",
        unsafe_allow_html=True,
    )
st.markdown("</div>", unsafe_allow_html=True)

# Chat Input
st.markdown("<div class='centered-input'>", unsafe_allow_html=True)

# Input widget with on_change callback
def on_input_change():
    user_input = st.session_state.user_input.strip()
    if user_input:
        # Append user input to chat history
        st.session_state.chat_history.append({"role": "User", "content": user_input})
        append_context("User", user_input)

        # Generate response from bot
        bot_response = generate_response(current_tone, memory["context_log"], user_input)
        st.session_state.chat_history.append({"role": "Assistant", "content": bot_response})
        append_context("Assistant", bot_response)

        # Clear input after sending
        st.session_state.user_input = ""

# Text input field with on_change callback to send message
user_input = st.text_input("Type your message:", key="user_input", placeholder="Apna sawal poochho...", on_change=on_input_change)

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("🌟 Created by **Mayank Raj**. Connect on [GitHub](https://github.com/6merge) and [Instagram](https://www.instagram.com/6merge).")
