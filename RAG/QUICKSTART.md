# Quick Start Guide - KYC/AML Compliance RAG Chatbot

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip3 install -r requirements.txt
```

### Step 2: Configure API Key
1. Get your Google API key from: https://makersuite.google.com/app/apikey
2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API key:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

### Step 3: Run the Application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📝 Using the Chatbot

1. **Set API Key**: Enter your Google API key in the sidebar and click "Set API Key"
2. **Load Documents**: Click "Load Sample Documents" to load the regulatory documents
3. **Ask Questions**: Type your compliance questions in the chat input

---

## 💡 Example Questions to Try

### Merchant KYC
```
What documents are required for merchant KYC?
```

### AML Red Flags
```
Define AML red-flag transaction detection
```

### FATF Standards
```
What are FATF recommendations for customer due diligence?
```

### GDPR Compliance
```
What are GDPR requirements for KYC data retention?
```

### Beneficial Ownership
```
What is beneficial ownership identification?
```

---

## 📚 Sample Documents Included

The chatbot comes pre-loaded with sample regulatory documents:

- **RBI AML Guidelines** - Merchant KYC requirements and red-flag detection
- **FATF Recommendations** - International AML standards
- **SEBI Compliance** - Securities market KYC norms
- **GDPR Requirements** - Data protection for KYC processes

---

## 🔧 Troubleshooting

### Test Your Setup
Run the test script to verify everything is configured correctly:
```bash
python3 test_setup.py
```

### Common Issues

**Import Errors**
- Make sure all dependencies are installed: `pip3 install -r requirements.txt`

**API Key Not Working**
- Verify your key at https://makersuite.google.com/app/apikey
- Check that `.env` file exists and contains your key
- Restart the application after setting the key

**No Documents Loaded**
- Click "Load Sample Documents" in the sidebar
- Check that the `documents/` folder contains the sample files

---

## 📖 Full Documentation

See [README.md](README.md) for complete documentation and [walkthrough.md](file:///Users/krishnachaitanya/.gemini/antigravity/brain/fb74be42-0b0d-4a1d-9182-402301a62bbf/walkthrough.md) for implementation details.
