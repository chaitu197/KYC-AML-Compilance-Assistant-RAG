# Troubleshooting Guide - KYC/AML RAG Chatbot

## ❌ Error: "Quota exceeded for metric: generativelanguage.googleapis.com"

![API Quota Error](/Users/krishnachaitanya/.gemini/antigravity/brain/fb74be42-0b0d-4a1d-9182-402301a62bbf/uploaded_image_0_1764358603484.png)

### What This Means

The Google Gemini API is rejecting requests because:
- ❌ Your API key has quota limit: 0 (no quota allocated)
- ❌ The free tier may not include embeddings API
- ❌ API key might not have Gemini API enabled

### ✅ Solutions

#### Option 1: Enable Gemini API Properly (Recommended)

1. **Go to Google AI Studio**: https://makersuite.google.com/app/apikey
2. **Create a NEW API key** (don't reuse old ones)
3. **Enable these APIs**:
   - Generative Language API
   - Embedding API
4. **Check billing**: Free tier has limits, consider enabling billing for production use
5. **Wait 5-10 minutes** for API activation

#### Option 2: Use OpenAI Instead

If Google API isn't working, switch to OpenAI (more reliable for production):

**Install OpenAI packages:**
```bash
pip3 install openai langchain-openai
```

**Get OpenAI API key:**
- Go to https://platform.openai.com/api-keys
- Create new key
- Add to `.env`: `OPENAI_API_KEY=sk-...`

**I can modify the code to use OpenAI** - just let me know!

#### Option 3: Use Free Local Embeddings (No API Key Needed)

For testing without any API keys, use local embeddings:

**Install sentence-transformers:**
```bash
pip3 install sentence-transformers
```

**I can create a version that runs 100% locally** - no API keys required!

---

## 🔍 Current Error Details

From your screenshots:

**Error 1 - sample_gdpr.txt:**
```
Quota exceeded for metric: generativelanguage.googleapis.com/embeddings
limit: 0
```

**Error 2 - sample_rbi_aml.txt:**
```
429 You exceeded your current quota
Quota exceeded for metric: generativelanguage.googleapis.com/embeddings
limit: 0
```

**Root cause:** The API key has **zero quota** for embeddings.

---

## 🚀 Quick Fix Options

### Option A: Try a Different Google Account
Some Google accounts have better free tier access than others.

### Option B: Wait and Retry
Sometimes quota resets after 24 hours.

### Option C: Switch to Alternative (Recommended)
Use OpenAI or local embeddings for reliable operation.

---

## 💡 Which Solution Do You Prefer?

1. **Fix Google API** - Get a working Google API key with quota
2. **Switch to OpenAI** - More reliable, better for production ($)
3. **Use Local Embeddings** - Free, no API needed, runs offline

Let me know and I'll implement the solution!

---

## 📊 Comparison

| Solution | Cost | Reliability | Speed | Setup |
|----------|------|-------------|-------|-------|
| Google Gemini | Free tier limited | ⚠️ Quota issues | Fast | Medium |
| OpenAI | $0.0001/1K tokens | ✅ Very reliable | Fast | Easy |
| Local (sentence-transformers) | Free | ✅ Always works | Slower | Easy |

**Recommendation:** Use **OpenAI** for production or **Local embeddings** for testing/demo.
