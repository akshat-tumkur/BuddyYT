# BuddyYT

BuddyYT is a Chrome side panel extension that lets you chat with the YouTube video you are currently watching. It reads the active tab URL, fetches the video's transcript, builds a local FAISS vector index, and uses a FastAPI + LangChain backend to answer questions from the transcript context.

## ✨ Features

- Chat with the active YouTube video from a Chrome side panel
- Ask custom questions or use quick prompts for summaries and key takeaways
- Transcript-grounded answers using retrieval-augmented generation
- Conversation memory per video session
- Local FAISS caching so repeated questions for the same video are faster
- OpenAI-powered chat and embeddings via LangChain

## 🛠️ Tech Stack

- **Frontend:** Chrome Extension Manifest V3, HTML, CSS, JavaScript
- **Backend:** FastAPI, Pydantic, Python
- **AI/RAG:** LangChain, OpenAI Chat Completions, OpenAI Embeddings
- **Vector Store:** FAISS
- **Transcript Source:** `youtube-transcript-api`

## 📁 Project Structure

```text
BuddyYT/
├── backend/
│   ├── app.py                  # FastAPI app and CORS setup
│   ├── routes/
│   │   └── chat.py             # /chat API endpoint
│   ├── services/
│   │   ├── rag.py              # RAG chain orchestration
│   │   ├── vector_store.py     # Transcript chunking and FAISS cache
│   │   ├── transcript_service.py
│   │   ├── llm.py
│   │   ├── embeddings.py
│   │   └── history.py
│   ├── prompts/
│   │   └── prompt.py
│   └── utils/
│       └── helpers.py
├── extension/
│   ├── manifest.json           # Chrome extension configuration
│   ├── sidepanel.html
│   ├── sidepanel.css
│   ├── sidepanel.js
│   └── background.js
├── requirements.txt
└── README.md
```

## ✅ Prerequisites

- Python 3.10 or newer
- Google Chrome or another Chromium-based browser with extension support
- An OpenAI API key
- A YouTube video with English captions/transcript available

## ⚙️ Setup

1. Clone the repository:

```bash
git clone https://github.com/akshat-tumkur/BuddyYT
cd BuddyYT
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 🚀 Run the Backend

Start the FastAPI server from the project root:

```bash
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

## 🧩 Load the Chrome Extension

1. Open Chrome and go to `chrome://extensions/`.
2. Enable **Developer mode**.
3. Click **Load unpacked**.
4. Select the `extension/` folder from this project.
5. Open a YouTube video.
6. Open the BuddyYT side panel and start asking questions.

## 🔌 API Reference

### `POST /chat`

Sends a user question and YouTube URL to the backend. The backend retrieves transcript chunks, generates an answer, and returns the active session ID.

Request body:

```json
{
  "query": "Summarize the key points from this video.",
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "session_id": null
}
```

Response:

```json
{
  "answer": "The video explains...",
  "session_id": "generated_session_id"
}
```

## 🧠 How It Works

1. The extension reads the current active tab URL.
2. The side panel sends the user's question and video URL to the FastAPI backend.
3. The backend fetches the YouTube transcript.
4. The transcript is split into chunks and embedded with `text-embedding-3-small`.
5. Chunks are stored in a local FAISS index under `backend/cache/faiss/`.
6. The most relevant chunks are retrieved for each question.
7. `gpt-4o-mini` generates an answer using only the provided transcript context and recent chat history.

## 🔧 Configuration

The current model settings are defined in:

- `backend/services/llm.py` - chat model: `gpt-4o-mini`
- `backend/services/embeddings.py` - embedding model: `text-embedding-3-small`

You can change the model names or generation settings in those files.

## 🩺 Troubleshooting

**The extension says it cannot reach the backend**

Make sure the FastAPI server is running on `http://localhost:8000` or `http://127.0.0.1:8000`.

**No answer is generated**

Check that:

- `OPENAI_API_KEY` is set in `.env`
- The YouTube video has English captions available
- The backend terminal is not showing transcript or API errors

**The first question is slow**

The first request for a video builds the FAISS index. Later questions for the same video should be faster because the index is cached locally.

## 📝 Notes

- Chat history is stored in memory, so sessions reset when the backend restarts.
- FAISS indexes are cached locally and should not be committed to version control.
- The current backend CORS policy allows all origins for local development.

## 👤 Author

Created with curiosity and passion by Akshat Tumkur.

Developed as a hands-on project to explore the design and implementation of modern RAG systems and LLM-powered applications.
