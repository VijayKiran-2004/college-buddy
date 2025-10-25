# 🎓 College Buddy - TKRCET AI Chatbot

An intelligent AI-powered chatbot for Teegala Krishna Reddy College of Engineering and Technology (TKRCET) that helps students get instant answers about admissions, courses, faculty, facilities, and more.

## ✨ Features

- 🤖 **AI-Powered Responses**: Uses RAG (Retrieval Augmented Generation) with Gemini AI
- 🎤 **Voice Input**: Multi-language voice search (English, Telugu, Hindi)
- 🔊 **Voice Response**: Natural text-to-speech with adjustable speed
- 📱 **Responsive Design**: Works perfectly on desktop and mobile
- ⚡ **Fast & Smart**: Intelligent caching and response optimization
- 🎯 **Student-Friendly**: Conversational, warm, and helpful responses
- 📊 **Analytics**: Background query analysis for continuous improvement

## 🚀 Tech Stack

- **Backend**: Python, FastAPI, WebSocket
- **AI/ML**: Google Gemini API, LangChain, ChromaDB
- **Vector Search**: Sentence Transformers (BAAI/bge-small-en)
- **Frontend**: HTML, JavaScript, Tailwind CSS
- **Voice**: Web Speech API, Speech Synthesis API

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API Key

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd college-buddy
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

5. Run the server:
```bash
python main.py
```

6. Open your browser to `http://localhost:8001`

## 🌐 Deployment

### Deploy to Render

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: college-buddy
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
6. Add Environment Variable: `GEMINI_API_KEY`
7. Click "Create Web Service"

Your bot will be live at: `https://college-buddy.onrender.com`

## 📁 Project Structure

```
college-buddy/
├── main.py                 # FastAPI server
├── rag/                    # RAG system
│   ├── chain.py           # Response generation
│   ├── retriever.py       # Document retrieval
│   ├── text_processor.py  # Query processing
│   └── rules.py           # Conversational rules
├── scraper/               # Data ingestion
├── static/                # Frontend files
│   └── index.html        # Chat interface
├── requirements.txt       # Python dependencies
└── .env                  # Environment variables
```

## 🎯 Usage

1. **Text Chat**: Type your question in the input box
2. **Voice Input**: Click the microphone icon or press Alt+V
3. **Voice Response**: Enable "Voice Response" in settings
4. **Adjust Speed**: Use the voice speed slider (0.7x - 1.5x)

## 🔧 Configuration

Edit `.env` file:
```env
GEMINI_API_KEY=your_api_key
PORT=8001
```

## 📊 Features in Detail

### Smart Retrieval
- 13 topic categories with intelligent query expansion
- Semantic search with ChromaDB vector database
- Context-aware response generation

### Voice System
- Multi-language support (English, Telugu, Hindi)
- Perfect text-voice synchronization
- Natural voice selection (Neural/Premium voices)
- Adjustable speech speed

### Student-Friendly
- All responses enhanced through Gemini for warm, conversational tone
- Encouraging and supportive language
- Clear, concise answers with helpful links

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 👥 Contact

For questions or support, please contact the TKRCET IT department.

---

**Made with ❤️ for TKRCET Students**
