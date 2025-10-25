# 🚀 Ollama + Gemini Hybrid Setup for College Buddy

Your College Buddy now supports **hybrid LLM system**:
- **Primary**: Gemma 3 4B (Local, Free, Private)
- **Fallback**: Google Gemini 2.5 Flash (Cloud, Reliable)

---

## 📋 **Installation Steps**

### **Step 1: Install Ollama**

#### **Windows (Your OS):**
1. Download Ollama from: https://ollama.com/download/windows
2. Run the installer (`OllamaSetup.exe`)
3. Ollama will install and run automatically in the background

#### **Verify Installation:**
```powershell
# Check if Ollama is running
curl http://localhost:11434

# Should return: "Ollama is running"
```

---

### **Step 2: Download Gemma 3 4B Model**

```powershell
# This will download ~2.7GB model
ollama pull gemma3:4b

# Verify model is downloaded
ollama list
```

**Download Time**: 5-15 minutes (depending on internet speed)

**Disk Space Needed**: ~3GB for model

---

### **Step 3: Configure College Buddy**

Create/update `.env` file in project root:

```env
# Your existing Gemini API key (fallback)
GEMINI_API_KEY=your_gemini_api_key_here

# Local model configuration
USE_LOCAL_MODEL=true
OLLAMA_BASE_URL=http://localhost:11434
LOCAL_MODEL_NAME=gemma3:4b
LOCAL_MODEL_TIMEOUT=15
```

---

### **Step 4: Test the Setup**

```powershell
# Start College Buddy
python main.py

# You should see in logs:
# ✅ Ollama connected at http://localhost:11434
# ✅ Local model ready: gemma2:4b
# ✅ Gemini fallback ready
```

---

## 🎯 **How It Works**

```
Student asks question
        ↓
[1] Try Gemma 3 4B (local)
        ↓
    15 seconds timeout?
        ↓
[2] Fallback to Gemini (cloud)
        ↓
    Return answer
```

**Automatic Switching:**
- ✅ If Gemma 3 responds fast → Use it (FREE!)
- ✅ If Gemma 3 times out → Switch to Gemini
- ✅ If Gemma 3 gives bad answer → Switch to Gemini
- ✅ If Ollama is down → Use Gemini only

---

## ⚙️ **Configuration Options**

### **Use Local Model Only (No Gemini):**
```env
USE_LOCAL_MODEL=true
# Remove or comment out GEMINI_API_KEY
```

### **Use Gemini Only (Disable Local):**
```env
USE_LOCAL_MODEL=false
GEMINI_API_KEY=your_key_here
```

### **Adjust Response Timeout:**
```env
LOCAL_MODEL_TIMEOUT=20  # Wait 20 seconds before fallback
```

### **Try Different Models:**
```powershell
# Faster but lower quality
ollama pull gemma2:2b

# Better quality but slower
ollama pull gemma2:7b

# DeepSeek alternative
ollama pull deepseek-r1:8b
```

Then update `.env`:
```env
LOCAL_MODEL_NAME=gemma2:2b  # or gemma2:7b, deepseek-r1:8b
```

---

## 🔍 **Testing Performance**

### **Test Local Model:**
```powershell
ollama run gemma2:4b "What are the college timings at TKRCET?"
```

### **Monitor Logs:**
When students ask questions, you'll see:
```
🟢 Ollama response in 12.3s  # Used local model
🔵 Gemini response           # Used fallback
⏱️ Ollama timeout after 15s  # Fallback triggered
```

---

## 📊 **Expected Performance**

### **Your Hardware (16GB RAM, CPU only):**
| Model | Response Time | Quality |
|-------|---------------|---------|
| Gemma 3 4B | 10-20 seconds | ⭐⭐⭐⭐ |
| Gemini 2.5 | 1-3 seconds | ⭐⭐⭐⭐⭐ |

**Reality Check:**
- First few queries: Gemma 3 will be used (slow but free)
- Complex queries: May timeout → Gemini takes over (fast)
- Result: Most queries free, important ones fast!

---

## 💰 **Cost Savings**

### **Before (Gemini Only):**
- 10,000 queries/month = ~₹500-1000

### **After (Hybrid):**
- 7,000 queries via Gemma 3 (free)
- 3,000 queries via Gemini = ~₹150-300
- **Savings: 70%!** 🎉

---

## 🐛 **Troubleshooting**

### **Problem: "Ollama not responding"**
```powershell
# Restart Ollama service
Get-Process ollama | Stop-Process -Force
Start-Process "ollama" -ArgumentList "serve"

# Or just restart your computer
```

### **Problem: "Model not found"**
```powershell
# Redownload model
ollama pull gemma2:4b

# Check available models
ollama list
```

### **Problem: "Responses too slow"**
```env
# Reduce timeout to fallback faster
LOCAL_MODEL_TIMEOUT=10

# Or disable local model
USE_LOCAL_MODEL=false
```

### **Problem: "Low quality answers"**
```powershell
# Try larger model (slower but better)
ollama pull gemma2:7b
```

Update `.env`:
```env
LOCAL_MODEL_NAME=gemma2:7b
LOCAL_MODEL_TIMEOUT=25  # Larger model needs more time
```

---

## 🎓 **Recommended for TKRCET**

### **Development/Testing:**
- ✅ Use hybrid system
- ✅ Monitor which model answers better
- ✅ Adjust timeout based on your CPU performance

### **Production (High Traffic):**
- **Option A**: Keep hybrid (70% cost savings)
- **Option B**: Switch to Gemini only (reliability)
- **Option C**: Upgrade to cloud GPU for faster local model

---

## 📈 **Performance Tuning**

### **If Gemma 3 is TOO SLOW:**
```env
# Switch to smaller/faster model
LOCAL_MODEL_NAME=gemma2:2b
LOCAL_MODEL_TIMEOUT=10
```

### **If Gemma 3 quality is POOR:**
```env
# Switch to larger/better model
LOCAL_MODEL_NAME=gemma2:7b
LOCAL_MODEL_TIMEOUT=25
```

### **If you want BEST of both:**
```env
# Use Ollama for simple queries, Gemini for complex
LOCAL_MODEL_TIMEOUT=12  # Quick timeout
# System will auto-fallback for complex questions
```

---

## 🚀 **Next Steps**

1. ✅ **Install Ollama** (5 minutes)
2. ✅ **Download Gemma 3 4B** (10 minutes)
3. ✅ **Test locally** (2 minutes)
4. ✅ **Monitor performance** (1 week)
5. ✅ **Adjust configuration** based on results

---

## 🆘 **Need Help?**

### **Check Ollama Status:**
```powershell
curl http://localhost:11434/api/tags
```

### **View College Buddy Logs:**
Look for these indicators:
- ✅ = Success
- ⚠️ = Warning (fallback used)
- ❌ = Error

### **Quick Reset:**
```powershell
# Stop everything
Get-Job | Stop-Job
Get-Job | Remove-Job -Force

# Restart Ollama
ollama serve

# Restart College Buddy
python main.py
```

---

## 📊 **Success Criteria**

Your setup is working if:
- ✅ Server starts without errors
- ✅ Logs show "Local model ready"
- ✅ Students get responses (even if some are slow)
- ✅ Gemini automatically takes over when needed

---

**You're all set! Your College Buddy now has intelligent model switching.** 🎯

**Cost savings + Reliability = Best of both worlds!** 🚀
