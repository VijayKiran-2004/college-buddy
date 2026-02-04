# TKRCET College Buddy - Quick Start Guide

## Installation (5 minutes)

### 1. Setup Environment
```bash
# Clone and navigate
cd college-buddy

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Ollama (Optional - for friendly responses)
```bash
# Download from https://ollama.ai
ollama pull gemma2:2b
ollama serve
```

### 3. Run Chatbot
```bash
python terminal_chat.py
```

---

## Quick Test

Try these queries:
1. `who is the principal?` → Instant (0.1s)
2. `what scholarships available?` → Instant (0.1s)
3. `how many students placed?` → Database (1-2s)
4. `latest notices?` → Web scraping (5-10s)

---

## Admin Dashboard

```bash
python admin_dashboard.py
# Visit: http://localhost:5000
```

---

## Features Overview

✅ **95%+ instant responses** - Expanded knowledge base
✅ **Conversation context** - "what about CSE?" works
✅ **Analytics tracking** - All queries logged
✅ **Multi-language** - Telugu, Hindi, English
✅ **Privacy protected** - Aggregate data only

---

## Troubleshooting

**Ollama timeout?**
- Increase timeout in `agent_mcp.py` (line 228): `timeout=30`
- Or disable LLM: System works without Ollama

**Import errors?**
```bash
pip install -r requirements.txt --upgrade
```

**Database errors?**
- Check `app/database/students.db` exists
- Run: `python app/services/sql_system.py` to test

---

## Next Steps

1. Test all features
2. Customize knowledge base in `ultra_rag.py`
3. Add more queries to analytics
4. Deploy to production

**Need help?** Check README.md for full documentation.
