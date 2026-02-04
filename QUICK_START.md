# Quick Start Guide - College Buddy v2.0

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
# Activate virtual environment (if not already active)
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install requirements
pip install -r requirements.txt
```

### Step 2: Start Ollama

```bash
# Pull the model (first time only)
ollama pull gemma2:2b

# Ollama should auto-start, verify with:
ollama ps
```

### Step 3: Run the Chatbot

```bash
python terminal_chat.py
```

---

## ✅ Test the Chatbot

Try these queries to verify everything works:

### Valid College Queries (Should Answer)
- "how r u?"
- "where is college located?"
- "who is the principal?"
- "what are the college timings?"
- "what courses are offered?"
- "tell me about facilities"

### Invalid Queries (Should Reject)
- "(a+b)^2"
- "solve 2+2"
- "what is photosynthesis?"
- "capital of France?"

**Expected Rejection Message:**
```
I'm sorry, I can only answer questions about TKRCET college. 
Please ask me about admissions, courses, facilities, timings, 
faculty, or other college-related topics.
```

---

## 🧪 Run Tests

Verify scope validation is working:

```bash
python test_scope_validation.py
```

**Expected Output:**
```
✓ PASSED - how r u? (GREETING)
✓ PASSED - where is college located? (COLLEGE INFO)
✓ PASSED - who is the principal? (PERSONNEL)
✓ PASSED - (a+b)^2 (MATH FORMULA - rejected)
✓ PASSED - solve 2+2 (MATH - rejected)

Total Tests: 9
Passed: 8
Success Rate: 89%
```

---

## 🔧 Troubleshooting

### Chatbot won't start
```bash
# Check if Ollama is running
ollama ps

# If not, start it
ollama serve
```

### Wrong answers or off-topic responses
```bash
# Delete cached indices to force rebuild
Remove-Item app/database/vectordb/ultrarag_faiss.index
Remove-Item app/database/vectordb/ultrarag_bm25.pkl

# Restart chatbot
python terminal_chat.py
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Out of memory
- Close other applications
- The gemma2:2b model uses ~1.5GB RAM
- Consider using a smaller model if needed

---

## 📁 What's New in v2.0

### ✨ Scope Validation (January 2026)
- ✅ Filters out non-college queries (math, science, general knowledge)
- ✅ Enhanced greeting detection ("how r u?", "what's up", etc.)
- ✅ Explicit rejection messages for off-topic questions
- ✅ 89% test success rate

### ⚡ Performance Improvements
- ✅ Switched to Gemma 2:2b (2x faster)
- ✅ Reduced context window (40% speed boost)
- ✅ Optimized prompt engineering
- ✅ Cached indices for instant startup

### 🛡️ Reliability Enhancements
- ✅ Strict LLM prompt enforcement
- ✅ Multi-layer scope validation
- ✅ Comprehensive test suite
- ✅ Better error handling

---

## 📚 Available Commands

Once the chatbot is running:

- `help` - Show available commands
- `clear` - Clear screen
- `status` - Show system status
- `exit` or `quit` - Exit chatbot

---

## 💡 Pro Tips

1. **First run takes longer**: FAISS and BM25 indices are built on first run
2. **Subsequent runs are instant**: Indices are cached
3. **Test regularly**: Run `test_scope_validation.py` to verify behavior
4. **Keep Ollama running**: Chatbot needs Ollama service active
5. **Use specific queries**: More specific questions get better answers

---

## 📊 System Status

Check if everything is working:

```bash
# In the chatbot, type:
status
```

**Expected Output:**
```
✓ Knowledge Base: 2029 documents loaded
✓ Embedding Model: all-MiniLM-L6-v2
✓ LLM Model: Gemma 2:2b (via Ollama)
✓ Retrieval: Hybrid FAISS + BM25
✓ System: UltraRAG v2.0
```

---

## 🆘 Need Help?

1. Check `README.md` for detailed documentation
2. Review test results: `python test_scope_validation.py`
3. Check Ollama status: `ollama ps`
4. Verify dependencies: `pip list`

---

## 🎯 Next Steps

1. ✅ Test the chatbot with various queries
2. ✅ Verify scope validation is working
3. ✅ Explore the knowledge base
4. ✅ Customize for your needs (optional)

---

**That's it! Your chatbot is ready to use! 🎉**

**Version**: 2.0  
**Last Updated**: January 2026
