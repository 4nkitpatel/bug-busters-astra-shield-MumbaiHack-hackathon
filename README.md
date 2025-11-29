# AstraShield - Disaster Relief Verification System

A forensic AI agent that verifies disaster relief flyers, QR codes, and donation requests to prevent fraud using multimodal analysis and real-time grounding.

🌐 **Live Demo**: [bug-busters-astra-shield-mumbai-hac.vercel.app](https://bug-busters-astra-shield-mumbai-hac.vercel.app)

## 🛡️ Overview

AstraShield is an intelligent verification system designed to combat predatory scams in disaster relief efforts. It uses advanced AI to analyze images of help flyers, QR codes, and social media posts, then performs comprehensive background checks to verify legitimacy.

## ✨ Features

- **Multimodal Image Analysis**: Extracts text, QR codes, and entities from images using OCR and Gemini Vision AI
- **Intelligent Entity Extraction**: Identifies organizations, phone numbers, emails, URLs, bank details, and locations
- **Real-time Verification**: 
  - Domain age checks (WHOIS)
  - Scam database cross-referencing (Google Search)
  - Official registry verification
  - Recent news/updates detection
- **Gemini-Powered Search**: Uses Gemini 3 Pro to generate intelligent Google search queries for comprehensive verification
- **Risk Assessment**: Calculates risk scores (0-100) and provides clear verdicts (SAFE, SUSPICIOUS, SCAM)
- **Modern React Frontend**: Beautiful, intuitive UI with camera capture and file upload
- **Multi-language Support**: Extracts text in Hindi, English, and regional languages

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Image Processing**: OCR (Tesseract), QR code decoding (pyzbar), Gemini Vision AI
- **Forensic Agent**: Orchestrates verification workflow using MCP tools
- **Search MCP**: Google Custom Search API integration for background checks
- **File System MCP**: Case file logging and evidence management

### Frontend (React/TypeScript)
- **Modern UI**: Tailwind CSS with dark theme
- **Camera Integration**: Direct camera capture for mobile/desktop
- **Real-time Analysis**: Progress tracking and status updates
- **Rich Reports**: Detailed entity forensics, evidence logs, and recommendations

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+
- Tesseract OCR: `brew install tesseract` (macOS) or `apt-get install tesseract-ocr` (Linux)
- Zbar: `brew install zbar` (macOS) or `apt-get install zbar-tools` (Linux)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/4nkitpatel/bug-busters-astra-shield-MumbaiHack-hackathon.git
   cd bug-busters-astra-shield-MumbaiHack-hackathon
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   GOOGLE_SEARCH_API_KEY=your_google_search_api_key
   GOOGLE_CSE_ID=your_custom_search_engine_id
   OPENAI_API_KEY=your_openai_api_key  # Optional, fallback
   ```

   See [ENV_SETUP.md](ENV_SETUP.md) and [GOOGLE_SEARCH_SETUP.md](GOOGLE_SEARCH_SETUP.md) for detailed setup instructions.

5. **Run the backend server**
   ```bash
   uvicorn src.api:app --reload --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   ```

4. **Open in browser**
   ```
   http://localhost:3000
   ```

## 📖 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design
- [ENV_SETUP.md](ENV_SETUP.md) - Environment variable setup guide
- [GOOGLE_SEARCH_SETUP.md](GOOGLE_SEARCH_SETUP.md) - Google Custom Search API setup
- [API_KEYS_USAGE.md](API_KEYS_USAGE.md) - API key usage and requirements
- [USAGE_GUIDE.md](USAGE_GUIDE.md) - User guide and examples
- [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md) - Recent improvements and enhancements
- [QR_CODE_ENHANCEMENTS.md](QR_CODE_ENHANCEMENTS.md) - QR code processing enhancements

## 🔧 API Endpoints

### `POST /verify`
Upload an image for verification.

**Request:**
- `file`: Image file (multipart/form-data)

**Response:**
```json
{
  "riskScore": 25,
  "verdict": "SAFE",
  "summary": "Executive summary...",
  "entities": [...],
  "evidencePoints": [...],
  "recommendation": "Recommendation text...",
  "sources": [...]
}
```

### `GET /health`
Health check endpoint.

## 🎯 Use Cases

1. **Disaster Relief Verification**: Verify legitimacy of help flyers and donation requests
2. **QR Code Analysis**: Extract and verify QR code content (URLs, payment links)
3. **Organization Verification**: Check if organizations are registered and legitimate
4. **Scam Detection**: Identify potential scams through comprehensive background checks

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Google Gemini API**: Multimodal AI for image analysis
- **OpenAI API**: Fallback vision analysis
- **Tesseract OCR**: Text extraction
- **Pyzbar**: QR code decoding
- **Google Custom Search API**: Real-time web search
- **WHOIS**: Domain registration checks

### Frontend
- **React 19**: UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Recharts**: Data visualization
- **Axios**: HTTP client
- **Vite**: Build tool

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🙏 Acknowledgments

- Built for Mumbai Hackathon
- Uses Google Gemini API for AI capabilities
- Inspired by the need to combat disaster relief scams

---

**Made with ❤️ for a safer world**
