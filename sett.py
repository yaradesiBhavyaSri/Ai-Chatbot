import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from io import BytesIO
from googleapiclient.discovery import build

# Configure the Gemini API client
genai.configure(api_key="AIzaSyBYJvAGWjDCVtFmPKgqPNFEwWAoAgf2WEU")  # Replace with your actual API key
model = genai.GenerativeModel(model_name='gemini-1.5-pro')

# YouTube API Key
youtube_api_key = "AIzaSyDVKC1L1KwNH-4p9AVfQ0-IBGQUHn3TUsM" # Replace with your actual YouTube API key
youtube = build("youtube", "v3", developerKey=youtube_api_key)

# Initialize chat history if not in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User Authentication State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Function: Convert text to speech
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer

# Function: Search YouTube videos
def search_youtube_videos(query):
    request = youtube.search().list(q=query, part="snippet", maxResults=3, type="video")
    response = request.execute()
    videos = [(item["snippet"]["title"], f"https://www.youtube.com/watch?v={item['id']['videoId']}") for item in response.get("items", [])]
    return videos

# Login Page
def login():
    st.title("🔐 Login to AI Tutor")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username == "admin" and password == "password123":  # Change credentials here
            st.session_state.logged_in = True
            st.success("Login successful! Redirecting...")
            st.rerun()  # ✅ Fixed: Replaced st.experimental_rerun() with st.rerun()
        else:
            st.error("Invalid credentials! Try again.")

# Sidebar Navigation
def sidebar():
    with st.sidebar:
        st.markdown("## 📌 Menu")
        page = st.radio("Navigation", ["🏠 Home", "📜 Recent History", "⚙️ Settings", "🔒 Logout"])

        # Display recent chat history as pinned messages
        if st.session_state.chat_history:
            st.markdown("### 📌 Pinned Queries")
            for i, (role, content) in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5 queries
                if role == "user":
                    if st.button(f"📌 {content}", key=f"query_{i}"):
                        st.session_state.selected_query = content  # Store the selected query

        return page

# Main App Logic
if not st.session_state.logged_in:
    login()
else:
    page = sidebar()

    if page == "🏠 Home":
        st.title("🤖 AI-Based Tutor for Personalized Learning")

        # Display chat history
        for role, content in st.session_state.chat_history:
            with st.chat_message(role):
                st.markdown(content)
                if role == "assistant":
                    with st.expander("🔊 Listen to Response", expanded=False):
                        audio_data = text_to_speech(content)
                        st.audio(audio_data, format='audio/mp3')

        # User Input
        user_input = st.chat_input("Ask a question:")
        
        if user_input:
            # Display user input
            st.chat_message("user").markdown(user_input)
            st.session_state.chat_history.append(("user", user_input))  # Store user input

            # Get AI Response
            response = model.generate_content(user_input)
            response_text = response.text

            # Display AI response
            with st.chat_message("assistant"):
                st.markdown(response_text)
                with st.expander("🔊 Listen to Response", expanded=False):
                    audio_data = text_to_speech(response_text)
                    st.audio(audio_data, format='audio/mp3')

                # Fetch and display relevant YouTube videos
                videos = search_youtube_videos(user_input)
                if videos:
                    st.markdown("### 🎥 Related Videos:")
                    for title, url in videos:
                        st.markdown(f"[{title}]({url})")

            # Store AI response in chat history
            st.session_state.chat_history.append(("assistant", response_text))

    elif page == "📜 Recent History":
        st.title("📜 Recent Chat History")
        if st.session_state.chat_history:
            for role, content in reversed(st.session_state.chat_history):
                with st.chat_message(role):
                    st.markdown(content)
        else:
            st.info("No recent history available.")

    elif page == "⚙️ Settings":
        st.title("⚙️ Settings")
        st.write("🔹 **Feature coming soon!** Customize your AI tutor settings here.")

    elif page == "🔒 Logout":
        st.session_state.logged_in = False
        st.session_state.chat_history = []  # Clear history on logout
        st.rerun()
#python -m streamlit run "C:/Users/yarad/OneDrive/Desktop/AICHATBOT/sett.py"