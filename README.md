# 🎓 TKRCET College Buddy - Enterprise AI Chatbot

**Production-ready AI chatbot for TKRCET college with Pure MCP architecture, analytics, and multi-language support.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Features

### **Core Capabilities**
- ✅ **Pure MCP Architecture** - Always fresh data from college website
- ✅ **95%+ Instant Responses** - Expanded static knowledge base (0.1s)
- ✅ **Smart LLM Integration** - Gemma 2:2b for friendly responses
- ✅ **Privacy Protection** - Aggregate data only, no personal info leaked
- ✅ **Database Integration** - 1,648 students, 351 placement records

### **Enhanced Features** 🆕
- ✅ **Conversation Context** - Remembers last 3 queries, handles follow-ups
- ✅ **Analytics System** - Full query tracking and performance monitoring
- ✅ **Admin Dashboard** - Flask web interface at `localhost:5000`
- ✅ **Multi-Language** - Telugu, Hindi, English auto-detection
- ✅ **5 MCP Tools** - Static facts, database, notices, placements, web search

---

## 📊 Performance

| Query Type | Response Time | Coverage |
|------------|---------------|----------|
| Static facts (principal, fees, etc.) | **0.1s** | 95% |
| Database queries (placements) | **1-2s** | Student data |
| Web scraping (live notices) | **5-10s** | Fresh data |
| Multi-language translation | **+0.1s** | 3 languages |

---

## 🎯 What Can It Answer?

### **Instant Responses (0.1s)**
- Personnel: "who is the principal?", "HOD of CSE?"
- Facilities: "library timings?", "sports ground?"
- Admissions: "admission process?", "eligibility?"
- **Scholarships**: "what scholarships available?" 🆕
- **Fees**: "btech fees?", "hostel cost?" 🆕
- **Events**: "tech fest?", "cultural events?" 🆕
- **Exams**: "when are mid-terms?", "exam schedule?" 🆕

### **Database Queries (1-2s)**
- Placements: "how many students placed?", "top companies?"
- Statistics: "CSE placement rate?", "average CGPA?"

### **Live Data (5-10s)**
- Notices: "latest notices?", "recent announcements?"
- Fresh info: "campus life?", "current events?"

### **Follow-up Questions** 🆕
```
You: "placement statistics?"
Bot: "351 students placed..."
You: "what about CSE?"
Bot: [Shows CSE placement stats] ✅
```

---

## 🛠️ Installation

### **Prerequisites**
- Python 3.8+
- Ollama (for LLM responses)
- 4GB RAM minimum

### **Setup**

1. **Clone repository**
```bash
git clone https://github.com/yourusername/college-buddy.git
cd college-buddy
```

2. **Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Ollama and Gemma 2:2b** (optional, for friendly responses)
```bash
# Download Ollama from https://ollama.ai
ollama pull gemma2:2b
ollama serve
```

---

## 🚀 Usage

### **Terminal Chatbot**
```bash
python terminal_chat.py
```

### **Admin Dashboard** 🆕
```bash
python admin_dashboard.py
# Visit: http://localhost:5000
```

### **Test Analytics** 🆕
```python
from app.services.analytics import AnalyticsSystem

analytics = AnalyticsSystem()
stats = analytics.get_stats(days=7)
print(f"Total queries: {stats['total_queries']}")
print(f"Success rate: {stats['success_rate']}%")
```

---

## 🏗️ Architecture

### **Pure MCP System**
```
Query → Language Detection → Context Resolution → Tool Selection
                                                         ↓
                                    ┌────────────────────┴────────────────────┐
                                    ↓                    ↓                    ↓
                            Static Facts         Database Query        Web Scraping
                              (0.1s)                (1-2s)               (5-10s)
                                    ↓                    ↓                    ↓
                                    └────────────────────┬────────────────────┘
                                                         ↓
                                            LLM Formatting (Gemma 2:2b)
                                                         ↓
                                            Translation (if needed)
                                                         ↓
                                            Analytics Logging
                                                         ↓
                                                    Response
```

### **5 MCP Tools**
1. **check_static_facts** - Instant answers from knowledge base
2. **query_database** - Student placement statistics (privacy-protected)
3. **scrape_latest_notices** - Live notices from website
4. **scrape_placements** - General placement information
5. **search_website** - Fallback web search

---

## 📁 Project Structure

```
college-buddy/
├── app/
│   ├── services/
│   │   ├── agent_mcp.py          # Main MCP agent
│   │   ├── mcp_tools.py          # 5 MCP tools
│   │   ├── analytics.py          # Analytics system 🆕
│   │   ├── translator.py         # Multi-language 🆕
│   │   ├── sql_system.py         # Database queries
│   │   └── ultra_rag.py          # Knowledge base
│   └── database/
│       ├── students.db           # Student data (1,648 records)
│       └── analytics.db          # Analytics data 🆕
├── templates/
│   └── dashboard.html            # Admin dashboard UI 🆕
├── admin_dashboard.py            # Flask dashboard 🆕
├── terminal_chat.py              # Terminal interface
├── requirements.txt
└── README.md
```

---

## 📈 Analytics Dashboard

**Access**: `http://localhost:5000`

**Features**:
- Total queries, success rate, cache hit rate
- Average response time trends
- Tool usage distribution
- Top 10 most asked questions
- Recent queries log
- Failed queries for debugging

---

## 🌐 Multi-Language Support

**Supported Languages**: English, Telugu, Hindi

**Auto-Detection**: Automatically detects user language

**Example**:
```
You: "ప్రిన్సిపాల్ ఎవరు" (Telugu)
Bot: [Detects Telugu] → Translates → Responds in Telugu

You: "प्रिंसिपल कौन है" (Hindi)
Bot: [Detects Hindi] → Translates → Responds in Hindi
```

---

## 🔒 Privacy & Security

- ✅ **No personal data exposed** - Only aggregate statistics
- ✅ **Privacy-protected queries** - Individual student data hidden
- ✅ **Secure database** - SQLite with proper access controls
- ✅ **Analytics anonymization** - Query patterns tracked, not user identity

---

## 🧪 Testing

### **Run Tests**
```bash
# Test chatbot
python terminal_chat.py

# Test analytics
python -c "from app.services.analytics import AnalyticsSystem; a = AnalyticsSystem(); print(a.get_stats())"

# Test translator
python app/services/translator.py

# Test admin dashboard
python admin_dashboard.py
```

### **Sample Queries**
```
1. "who is the principal?" → Instant
2. "what scholarships are available?" → Instant
3. "how many students got placed?" → Database query
4. "latest notices?" → Web scraping
5. "placement stats?" then "what about CSE?" → Context
```

---

## 📊 System Metrics

**Current Status**:
- 📚 **Knowledge Base**: 12 sections, 95%+ coverage
- 🗄️ **Database**: 1,648 students, 351 placed
- ⚡ **Performance**: 0.1s - 12s depending on query
- 🌐 **Languages**: 3 (English, Telugu, Hindi)
- 📈 **Analytics**: Full query tracking

---

## 🛣️ Roadmap

### **Completed** ✅
- [x] Pure MCP architecture
- [x] Smart LLM integration
- [x] Database integration
- [x] Expanded knowledge base
- [x] Analytics system
- [x] Conversation context
- [x] Admin dashboard
- [x] Multi-language support

### **Future Enhancements**
- [ ] WhatsApp bot integration
- [ ] Voice interface (speech-to-text)
- [ ] Mobile app (React Native)
- [ ] Advanced analytics (charts/graphs)
- [ ] More language support

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 👥 Authors

- **Vijay Kiran** - Initial work

---

## 🙏 Acknowledgments

- TKRCET College for data and support
- Ollama team for Gemma 2:2b model
- Flask team for web framework
- Contributors and testers

---

## 📞 Support

For issues or questions:
- Create an issue on GitHub
- Contact: vijaykiran1008@gmail.com

---

**Built with ❤️ for TKRCET students**
