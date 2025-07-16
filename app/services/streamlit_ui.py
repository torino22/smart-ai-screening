import io
import os
import tempfile
from datetime import datetime

import requests
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from dotenv import load_dotenv

load_dotenv()
BACKEND_ROOT_URL = os.getenv("BACKEND_ROOT_URL")

# Constants
ROOT_URL = BACKEND_ROOT_URL  # Update this with your actual host and port
STREAMLIT_ADMIN_PASSWORD = os.getenv("STREAMLIT_ADMIN_PASSWORD")
TIMEOUT = 200


def check_health():
    """Check if the backend is healthy"""
    try:
        response = requests.get(f"{ROOT_URL}/health", timeout=TIMEOUT)
        return response.status_code == 200
    except:
        return False


def upload_media(session_id, audio_file):
    """Upload audio file to backend"""
    try:
        files = {'file': audio_file}
        data = {'session_id': session_id}
        response = requests.post(f"{ROOT_URL}/media", files=files, data=data, timeout=TIMEOUT)
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)


def get_faq_questions(session_id):
    """Fetch FAQ questions for a specific session"""
    try:
        response = requests.post(f"{ROOT_URL}/faq", params={'session_id': session_id}, timeout=TIMEOUT)
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False):
                return True, result.get('result', [])
            else:
                return False, result.get('message', 'Failed to fetch FAQs')
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)


def send_chat_query(session_id, query):
    """Send chat query to backend and get audio response"""
    try:
        response = requests.post(f"{ROOT_URL}/chat", params={'session_id': session_id, 'query': query}, timeout=TIMEOUT)
        if response.status_code == 200:
            # Save the audio file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_file.write(response.content)
                return True, tmp_file.name
        else:
            return False, f"Request failed with status {response.status_code}"
    except Exception as e:
        return False, str(e)


def main():
    st.set_page_config(page_title="Interview Screening System", layout="wide")

    # Create layout with health status
    health_col, main_col = st.columns([1, 4])

    with health_col:
        st.subheader("System Status")
        health_status = check_health()
        if health_status:
            st.success("🟢 Backend Online")
        else:
            st.error("🔴 Backend Offline")
        st.write("---")

    with main_col:
        st.title("Interview Screening System")

        # Initialize session state
        if 'stage' not in st.session_state:
            st.session_state.stage = 'upload'
        if 'session_id' not in st.session_state:
            st.session_state.session_id = None
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'faq_questions' not in st.session_state:
            st.session_state.faq_questions = []
        if 'current_chat_session' not in st.session_state:
            st.session_state.current_chat_session = None

        # Stage 1: Upload Audio
        if st.session_state.stage == 'upload':
            st.header("Upload Interview Audio")

            session_id = st.text_input("Session ID", placeholder="Enter session ID")

            # Audio input options
            audio_option = st.radio("Choose audio input method:", ["Upload File", "Record Audio"])

            uploaded_file = None
            recorded_audio = None

            if audio_option == "Upload File":
                uploaded_file = st.file_uploader("Choose audio file", type=['wav', 'mp3', 'mp4', 'm4a'])
            else:
                st.write("Click to start/stop recording:")
                st.info("💡 Click the record button to start, click again to stop recording")
                recorded_audio = audio_recorder(
                    text="Click to Record",
                    recording_color="#e87070",
                    neutral_color="#6aa36f",
                    icon_name="microphone-lines",
                    icon_size="2x",
                    pause_threshold=30.0,  # 30 seconds of silence before auto-stop
                    sample_rate=16000,  # Good quality for speech
                    auto_start=False  # Manual start/stop
                )

                if recorded_audio is not None:
                    st.success("Audio recorded successfully!")
                    st.audio(recorded_audio, format='audio/wav')
                    # Show recording duration
                    duration = len(recorded_audio) / 16000  # Approximate duration
                    st.write(f"Recording duration: {duration:.1f} seconds")

            # Better button layout with full width
            st.write("")  # Add spacing
            col1, col2 = st.columns(2)

            with col1:
                upload_button = st.button("📁 Upload Audio", type="primary", use_container_width=True)
                if upload_button:
                    if not session_id:
                        st.error("Please enter a session ID")
                    elif audio_option == "Upload File" and not uploaded_file:
                        st.error("Please upload an audio file")
                    elif audio_option == "Record Audio" and recorded_audio is None:
                        st.error("Please record audio first")
                    else:
                        with st.spinner("Uploading and processing audio..."):
                            # Use recorded audio or uploaded file
                            audio_file = recorded_audio if audio_option == "Record Audio" else uploaded_file

                            # Convert recorded audio bytes to file-like object if needed
                            if audio_option == "Record Audio":
                                audio_file = io.BytesIO(recorded_audio)
                                audio_file.name = "recorded_audio.wav"

                            success, response = upload_media(session_id, audio_file)
                            if success:
                                st.success("Audio uploaded successfully!")
                                st.session_state.session_id = session_id
                            else:
                                st.error(f"Upload failed: {response}")

            with col2:
                if st.button("🔍 Evaluate Candidates", type="secondary", use_container_width=True):
                    st.session_state.stage = 'auth'
                    st.rerun()

        # Stage 2: Authentication
        elif st.session_state.stage == 'auth':
            st.header("Authentication Required")

            password = st.text_input("Enter Password", type="password")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔐 Login", type="primary", use_container_width=True):
                    if password == STREAMLIT_ADMIN_PASSWORD:
                        st.session_state.authenticated = True
                        st.session_state.stage = 'chat'
                        st.rerun()
                    else:
                        st.error("Invalid password")

        # Stage 3: Chat Interface
        elif st.session_state.stage == 'chat' and st.session_state.authenticated:
            st.header("Interview Analysis Chat")

            # Session ID input for evaluation
            chat_session_id = st.text_input(
                "Enter Candidate Session ID to Evaluate:",
                value=st.session_state.current_chat_session or "",
                placeholder="Enter session ID of the candidate you want to evaluate"
            )

            if chat_session_id != st.session_state.current_chat_session:
                st.session_state.current_chat_session = chat_session_id
                st.session_state.faq_questions = []  # Reset FAQs for new session
                st.session_state.chat_history = []  # Reset chat history for new session

            if chat_session_id:
                st.info(f"Evaluating Candidate: {chat_session_id}")

                # Create two columns for chat interface
                col1, col2 = st.columns([3, 1])

                with col2:
                    st.subheader("FAQ")

                    if st.button("Generate FAQ", use_container_width=True):
                        with st.spinner("Generating FAQ questions..."):
                            success, faq_data = get_faq_questions(chat_session_id)
                            if success:
                                st.session_state.faq_questions = faq_data
                                st.success("FAQ questions generated!")
                            else:
                                st.error(f"Failed to generate FAQ: {faq_data}")

                    if st.session_state.faq_questions:
                        st.write("**Available Questions:**")
                        for i, question in enumerate(st.session_state.faq_questions):
                            if st.button(f"{question}", key=f"faq_{i}", use_container_width=True):
                                st.session_state.selected_query = question

                with col1:
                    # Chat Interface with left-right layout
                    st.subheader("Chat")

                    # Chat container
                    chat_container = st.container()

                    with chat_container:
                        if st.session_state.chat_history:
                            for i, chat in enumerate(st.session_state.chat_history):
                                # Evaluator message (User question)
                                with st.container():
                                    st.markdown("**👤 Evaluator:**")
                                    st.info(f"❓ {chat['query']}")
                                    st.caption(f"📅 {chat['timestamp']}")
                                    st.write("")  # Add some spacing

                                # AI response (Audio)
                                with st.container():
                                    st.markdown("**🤖 AI Response:**")
                                    if chat['audio_file'] and os.path.exists(chat['audio_file']):
                                        st.success("🎵 Audio Response Generated")
                                        st.audio(chat['audio_file'], format='audio/mp3')
                                    else:
                                        st.warning("⚠️ Audio file not available")
                                    st.write("---")  # Add separator between conversations
                        else:
                            st.info("💬 Start a conversation by typing a question below")

                    # Query input at the bottom
                    st.markdown("---")

                    # Better query input layout
                    query = st.text_input(
                        "Ask a question about the candidate:",
                        value=st.session_state.get('selected_query', ''),
                        placeholder="Type your question here...",
                        key="query_input"
                    )

                    # Full width send button
                    send_button = st.button("Send", type="primary", use_container_width=True)

                    if send_button and query:
                        with st.spinner("🎤 AI is generating audio response..."):
                            success, audio_file_path = send_chat_query(chat_session_id, query)
                            if success:
                                # Add to chat history
                                st.session_state.chat_history.append({
                                    'query': query,
                                    'audio_file': audio_file_path,
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                                st.session_state.selected_query = ''
                                st.rerun()
                            else:
                                st.error(f"❌ Query failed: {audio_file_path}")
                    elif send_button and not query:
                        st.error("Please enter a question")
            else:
                # Show clean chat interface even without session ID
                # Create two columns for chat interface
                col1, col2 = st.columns([3, 1])

                with col2:
                    st.subheader("FAQ")
                    st.write("Enter a session ID to generate FAQ questions")

                with col1:
                    # Chat Interface
                    st.subheader("Chat")
                    st.info("💬 Start a conversation by typing a question below")

                    # Query input at the bottom
                    st.markdown("---")

                    # Query input layout
                    query = st.text_input(
                        "Ask a question about the candidate:",
                        placeholder="Type your question here...",
                        key="query_input_empty"
                    )

                    # Send button (disabled when no session)
                    send_button = st.button("Send", type="primary", use_container_width=True, disabled=True)
                    if send_button:
                        st.warning("Please enter a candidate session ID first")

            # Reset button
            st.write("")  # Add spacing
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                # Clean up temporary audio files
                for chat in st.session_state.chat_history:
                    if chat.get('audio_file') and os.path.exists(chat['audio_file']):
                        try:
                            os.unlink(chat['audio_file'])
                        except:
                            pass

                st.session_state.stage = 'upload'
                st.session_state.session_id = None
                st.session_state.authenticated = False
                st.session_state.chat_history = []
                st.session_state.faq_questions = []
                st.session_state.current_chat_session = None
                st.session_state.selected_query = ''
                st.rerun()


if __name__ == "__main__":
    main()