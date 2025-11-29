# Environment Variables Setup Guide

## 📋 Quick Setup

### Step 1: Create `.env` File

The `.env` file is hidden (in `.gitignore`) for security. You need to create it manually.

**Option A: Using Terminal**
```bash
cd /Users/upmanyujha/Documents/mumbai_hacks_BB
cp .env.example .env
```

**Option B: Using File Explorer/Finder**
1. Navigate to the project root: `/Users/upmanyujha/Documents/mumbai_hacks_BB`
2. Create a new file named `.env` (note the dot at the beginning)
3. Copy the contents from `.env.example` into it

**Option C: Using VS Code/Cursor**
1. Right-click in the project root folder
2. Select "New File"
3. Name it `.env`
4. Copy contents from `.env.example`

### Step 2: Add Your API Keys

Open the `.env` file and replace the placeholder values with your actual API keys:

```env
# Required for image vision analysis
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Recommended for better summaries
GEMINI_API_KEY=your-actual-gemini-key-here

# Optional (not currently used)
ANTHROPIC_API_KEY=your-actual-anthropic-key-here
```

### Step 3: Get Your API Keys

#### OpenAI API Key:
1. Go to: https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Paste it in `.env` file

#### Gemini API Key:
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key
5. Paste it in `.env` file

#### Anthropic API Key (Optional):
1. Go to: https://console.anthropic.com/
2. Sign in or create an account
3. Navigate to API Keys section
4. Create a new key
5. Copy and paste in `.env` file

## ✅ Verification

After setting up your `.env` file, verify it's working:

```bash
# From project root
cd /Users/upmanyujha/Documents/mumbai_hacks_BB
source venv/bin/activate
python -c "from src.config import OPENAI_API_KEY, GEMINI_API_KEY; print('OpenAI:', 'Set' if OPENAI_API_KEY else 'Not Set'); print('Gemini:', 'Set' if GEMINI_API_KEY else 'Not Set')"
```

## 🔒 Security Notes

- **Never commit `.env` to git** - It's already in `.gitignore`
- **Never share your API keys** - Keep them private
- **Use `.env.example`** - For sharing the structure without keys
- **Rotate keys if exposed** - If you accidentally share a key, regenerate it

## 📝 File Structure

```
mumbai_hacks_BB/
├── .env              # Your actual API keys (hidden, not in git)
├── .env.example      # Template file (safe to commit)
├── src/
│   └── config.py     # Reads from .env file
└── ...
```

## 🚨 Troubleshooting

### "ModuleNotFoundError: No module named 'dotenv'"
```bash
pip install python-dotenv
```

### "API key not found"
- Check that `.env` file exists in project root
- Verify the key names match exactly (case-sensitive)
- Make sure there are no extra spaces around the `=` sign
- Restart your Python process after creating `.env`

### "Invalid API key"
- Verify you copied the entire key (no truncation)
- Check for extra spaces or newlines
- Regenerate the key from the provider's dashboard

## 📚 Related Documentation

- See `API_KEYS_USAGE.md` for details on where each key is used
- See `README.md` for general setup instructions

