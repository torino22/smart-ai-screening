# 🧠 Smart Interview Screening System

An AI-powered interview assistant that transcribes candidate audio, extracts key information using NLP, matches relevant FAQs via semantic search (RAG), and returns audio/text-based responses—all with an interactive Streamlit frontend.

---

## 📸 Quick Start Guide

### Step 1: Upload Interview Audio (for candidates)

  1. Enter a **Session ID** for the candidate
    NOTE: For use ease of use you can enter the name or email as session_id (e.g., `john_doe_interview`)
  2. Choose how to add audio:
    - **Upload File**: Select audio file (wav, mp3, mp4, m4a)
    - **Record Audio**: Click record button to capture live audio
  3. Click **Upload Audio** to process

### Step 2: Access Evaluation (for screening authority)

  1. Click **Evaluate Candidates** 
  2. Enter password when prompted (which will be stored in .env for streamlit use)
  3. You're now in the evaluation interface

### Step 3: Evaluate Candidate

  1. Enter the **Session ID** of candidate you want to evaluate
  2. **Generate FAQ** to get suggested questions
  3. **Chat Interface**:
    - Type your question in the text box
    - Click **Send** 
    - AI responds with audio
    - View chat history above


---


## 🚀 Features

  - 📁 Upload or record candidate audio
  - 🔐 Password-protected access (admin only access for evaluation)
  - ❓ AI-generated FAQ questions
  - 💬 Text-to-audio chat evaluation
  - 🔄 Multiple candidate sessions (multitenant)


---


## Tips

- Use clear, unique session IDs
- Green status = system ready
- Click FAQ questions to auto-fill
- Use **Logout** to switch candidates safely
-


---


## 📁 Project Structure

<pre><code>
  smart_ai_screening/
  ├── venv/                            # Virtual environment (library root)
  ├── app/                             # Main application directory
  │   ├── config/
  │   │   ├── __init__.py
  │   │   └── settings.py
  │   ├── db/
  │   │   ├── __init__.py
  │   │   ├── models.py
  │   │   └── setup.py
  │   ├── pydantics/
  │   │   ├── __init__.py
  │   │   └── schemas.py
  │   ├── routers/
  │   │   ├── __init__.py
  │   │   ├── chat.py
  │   │   └── file_io.py
  │   ├── services/
  │   │   ├── __init__.py
  │   │   ├── file_io.py
  │   │   ├── llm_service.py
  │   │   ├── nsr.py
  │   │   ├── sql.py
  │   │   ├── streamlit_ui.py
  │   │   └── vector.py
  │   ├── templates/
  │   │   ├── __init__.py
  │   │   ├── chat_prompt_template.py
  │   │   ├── generic_faq.py
  │   │   └── skills.txt
  │   ├── utils/
  │   │   ├── __init__.py
  │   │   └── logger.py
  │   └── __init__.py
  ├── chroma_db/                     # Vector database directory
  ├── logs/                          # Application logs
  ├── output_audio/                  # Audio output files
  ├── uploads/                       # File uploads directory
  ├── .env                           # Environment variables
  ├── .gitignore                     # Git ignore file
  ├── database.db                    # SQLite database
  ├── database.db-shm                # SQLite shared memory file
  ├── database.db-wal                # SQLite write-ahead log
  ├── main.py                        # Main application entry point
  └── requirements.txt               # Python dependencies
</code></pre>


---


## 📁 Project Structure Overview

### Core Application (app/)

- **config/:** Application configuration and settings
- **db/:** Database models and setup scripts
- **pydantics/:** Data validation schemas using Pydantic
- **routers/:** API route handlers (chat, file I/O)
- **services/:** Business logic services (LLM, vector search, SQL, etc.)
- **templates/:** Prompt templates and skill definitions
- **utils/:** Utility functions (logging, etc.)

### Data & Storage

- **chroma_db/:** Vector database for embeddings and similarity search
- **uploads/:** User-uploaded files
- **output_audio/:** Generated audio files
- **database.db:** Main SQLite database with associated files

### Configuration & Dependencies

- **.env:** Environment variables and secrets
- **requirements.txt:** Python package dependencies
- **venv/:** Virtual environment for isolated dependencies

### Logs & Metadata

- **logs/:** Application log files
- **.gitignore:** Git version control ignore rules



---


## 💬 Interview Chat Interface

- Input session ID (linked to uploaded audio)
- Ask questions about the candidate (e.g., _"Does he know Python?"_)
- AI evaluates candidate responses based on transcribed self-introduction
- FAQ responses are generated and spoken using text-to-speech
- Button: `Generate FAQ` to display hardcoded Q&A
- Button: `Evaluate Candidates` triggers backend processing


---


## ⚙️ Tech Stack

<pre><code>

| Layer        | Tools & Libraries                           |
|--------------|---------------------------------------------|
| Backend      | FastAPI, SQLAlchemy                         |
| ML/NLP       | HuggingFace Transformers, Whisper, ChromaDB |
| Audio        | ffmpeg-python, edge-tts                     |
| Frontend     | Streamlit                                   |
| Database     | SQLite                                      |

</code></pre>


---


## 🧪 Sample Workflow

1. **User uploads `John_self_intro_audio.wav`**

2. **Backend transcribes to text:**
```bash
   > "Hi, I’m John. I have 4 years of experience in Python and Django..."
```

3. **Named Entity Recognition extracts:**

```bash
   {
     "name": "John",
     "skills": ["Python", "Django"],
     "Location": "Chennai",
     "Company_Name": "InnoTech Solutions"
   }
```

4. **User asks:**

```bash
"Does he know Python?"
```

5. **System confirms via extracted skills and responds via TTS.**


---


## 🛠️ Installation

### 🔧 Backend (FastAPI)
```bash
git clone https://github.com/yourusername/smart-interview-assistant
cd <to the dir where stremlit_ui.py exist>
pip install -r requirements.txt
uvicorn main:app --reload
```


---


## 🖥️ Frontend (Streamlit)

```bash
cd <to your root folder where main.py exsist>
streamlit run app.py
```


---


## .env setup

```bash
OPENAI_API_KEY=<openAI-key>
BACKEND_ROOT_URL=<{root_url}>
STREAMLIT_ADMIN_PASSWORD=<admin-pswd>
```


---


## 🧾 Deliverables

-  ✅ Codebase (backend + frontend)
-  🎧 Sample audio files
-  ❓ Predefined FAQs and embeddings
-  📖 Complete README
-  🗃️ Entity extraction schema with JSON output


---
