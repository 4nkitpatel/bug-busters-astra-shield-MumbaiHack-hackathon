# API Keys Usage Guide

This document explains where each API key from `config.py` is used in the codebase.

## 📋 API Keys Overview

From `src/config.py`:
- `OPENAI_API_KEY` - Used for OpenAI services
- `ANTHROPIC_API_KEY` - Currently **NOT USED** (reserved for future use)
- `GEMINI_API_KEY` - Used for Google Gemini services

---

## 🔑 OPENAI_API_KEY

**Status:** ✅ **ACTIVELY USED**

### Usage Locations:

#### 1. **Image Processing** (`src/image_processor.py`)
- **Purpose:** Vision AI analysis of images
- **Model:** `gpt-4-vision-preview` (from `VISION_MODEL` config)
- **Function:** `_analyze_with_vision()`
- **What it does:**
  - Analyzes images using GPT-4 Vision
  - Extracts text, descriptions, and context from images
  - Provides structured analysis of flyer content
- **Fallback:** If not set, vision analysis is disabled (warning shown)

#### 2. **Forensic Agent** (`src/forensic_agent.py`)
- **Purpose:** LLM-based summary and recommendation generation
- **Model:** `gpt-4-turbo-preview` (from `LLM_MODEL` config)
- **Function:** `_generate_summary()` (fallback)
- **What it does:**
  - Generates executive summaries (if Gemini not available)
  - Creates human-readable investigation summaries
  - Used as fallback when Gemini API is not configured
- **Fallback:** Falls back to basic text summary if not set

### Summary:
- **Primary Use:** Image vision analysis (GPT-4 Vision)
- **Secondary Use:** Summary generation (fallback to GPT-4 Turbo)
- **Required:** Recommended (for image analysis)
- **Optional:** System works without it but with limited functionality

---

## 🔑 GEMINI_API_KEY

**Status:** ✅ **ACTIVELY USED**

### Usage Locations:

#### 1. **Forensic Agent** (`src/forensic_agent.py`)
- **Purpose:** Generate well-formatted, human-friendly executive summaries
- **Model:** `gemini-2.0-flash-exp` (from `GEMINI_MODEL` config)
- **Function:** `_generate_summary()`
- **What it does:**
  - Creates professional, well-formatted executive summaries
  - Generates 2-3 paragraph summaries in simple language
  - Provides better formatting than OpenAI fallback
- **Priority:** First choice for summary generation
- **Fallback:** Falls back to OpenAI if not available

### Summary:
- **Primary Use:** Executive summary generation (Gemini 2.0 Flash)
- **Required:** Optional (but recommended for better summaries)
- **Fallback:** Uses OpenAI if not set

---

## 🔑 ANTHROPIC_API_KEY

**Status:** ❌ **NOT CURRENTLY USED**

### Current Status:
- **Defined in config:** Yes
- **Used anywhere:** No
- **Purpose:** Reserved for future Claude/Anthropic integration
- **Action Required:** None (can be removed from config if not needed)

### Potential Future Uses:
- Could be used for alternative LLM-based analysis
- Could replace OpenAI for summary generation
- Could be used for additional AI-powered features

---

## 📊 Usage Priority & Flow

### Image Analysis Flow:
```
1. Image Processing (image_processor.py)
   └─> Uses OPENAI_API_KEY (GPT-4 Vision)
       └─> Analyzes image content
       └─> Extracts text and context
```

### Summary Generation Flow:
```
1. Forensic Agent (forensic_agent.py)
   └─> Try GEMINI_API_KEY first (Gemini 2.0 Flash)
       └─> Generate well-formatted summary
   └─> Fallback to OPENAI_API_KEY (GPT-4 Turbo)
       └─> Generate basic summary
   └─> Final fallback: Basic text summary
```

---

## ⚙️ Configuration Priority

### Required for Full Functionality:
1. **OPENAI_API_KEY** - For image vision analysis
2. **GEMINI_API_KEY** - For best quality summaries (optional but recommended)

### Optional:
- **ANTHROPIC_API_KEY** - Not used, can be ignored

---

## 🔧 Setup Instructions

### Step 1: Create `.env` File

The `.env` file is hidden (in `.gitignore`) for security. Create it manually:

**Using Terminal:**
```bash
cd /Users/upmanyujha/Documents/mumbai_hacks_BB
cp .env.example .env
```

**Or create manually:**
1. Create a new file named `.env` in the project root
2. Copy contents from `.env.example`

### Step 2: Add Your API Keys

Open `.env` and replace placeholder values:

### Minimum Setup (Basic Functionality):
```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

### Recommended Setup (Full Functionality):
```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
GEMINI_API_KEY=your-actual-gemini-key-here
```

### Complete Setup (All Keys):
```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
GEMINI_API_KEY=your-actual-gemini-key-here
ANTHROPIC_API_KEY=your-actual-anthropic-key-here  # Not used yet
```

### Step 3: Get API Keys

- **OpenAI**: https://platform.openai.com/api-keys
- **Gemini**: https://makersuite.google.com/app/apikey
- **Anthropic**: https://console.anthropic.com/ (optional)

📖 **See `ENV_SETUP.md` for detailed setup instructions**

---

## 📝 Code References

### Files Using API Keys:

1. **src/image_processor.py**
   - Line 16: Imports `OPENAI_API_KEY`, `VISION_MODEL`
   - Line 23: Initializes OpenAI client
   - Line 40: Uses for vision analysis

2. **src/forensic_agent.py**
   - Line 10: Imports `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GEMINI_MODEL`
   - Line 25: Initializes OpenAI client (fallback)
   - Line 28-32: Initializes Gemini client (primary)
   - Line 272: Uses Gemini for summary generation
   - Line 314: Falls back to OpenAI if Gemini unavailable

---

## 🎯 Summary

- **OPENAI_API_KEY**: Used for image vision analysis (required for full functionality)
- **GEMINI_API_KEY**: Used for executive summary generation (recommended for better quality)
- **ANTHROPIC_API_KEY**: Not used (reserved for future features)

