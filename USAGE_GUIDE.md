# Usage Guide

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR
# macOS: brew install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Command Line Usage

```bash
python main.py path/to/help_flyer_image.jpg
```

### 3. API Server

```bash
# Start server
uvicorn src.api:app --reload

# In another terminal, test with curl
curl -X POST "http://localhost:8000/verify" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/image.jpg"
```

## Detailed Examples

### Python API

```python
import asyncio
from src.forensic_agent import ForensicAgent

async def verify():
    agent = ForensicAgent()
    result = await agent.investigate("flyer.jpg")
    
    print(f"Verdict: {result['verdict']}")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Summary: {result['summary']}")

asyncio.run(verify())
```

### Using Individual Components

#### Image Processing

```python
from src.image_processor import ImageProcessor

processor = ImageProcessor()
result = processor.process_image("flyer.jpg")

print("Extracted phones:", result['extracted']['phone_numbers'])
print("Extracted emails:", result['extracted']['emails'])
print("Extracted URLs:", result['extracted']['urls'])
```

#### MCP Tools Directly

```python
import asyncio
from src.mcp_tools import FileSystemMCP, SearchMCP

# File System MCP
fs_mcp = FileSystemMCP()
case_file = fs_mcp.create_case_file("test123", {"test": "data"})
fs_mcp.log_evidence("test_evidence", {"key": "value"})

# Search MCP
async def search_example():
    search_mcp = SearchMCP()
    domain_info = await search_mcp.check_domain_age("example.com")
    print(domain_info)
    await search_mcp.close()

asyncio.run(search_example())
```

## Understanding the Output

### Verdict Types

- **safe**: Low risk (risk score < 40)
  - Resource appears legitimate
  - Still recommend independent verification

- **suspicious**: Medium risk (risk score 40-69)
  - Some concerning indicators
  - Exercise caution
  - Verify through multiple sources

- **scam**: High risk (risk score >= 70)
  - Strong indicators of fraudulent activity
  - Do not proceed
  - Report if already engaged

### Risk Score Breakdown

- **0-39**: Low risk
- **40-69**: Medium risk
- **70-100**: High risk

### Case File Structure

Case files are saved in `case_files/` directory with the following structure:

```json
{
  "case_id": "abc123",
  "created_at": "2024-01-15T10:30:00",
  "status": "completed",
  "verdict": "suspicious",
  "risk_score": 55,
  "evidence": [
    {
      "timestamp": "2024-01-15T10:30:05",
      "type": "domain_age_check",
      "source": "whois",
      "data": { ... }
    }
  ],
  "timeline": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "event": "case_created",
      "data": { ... }
    }
  ],
  "summary": "...",
  "recommendations": [ ... ]
}
```

## Integration Examples

### Flask Integration

```python
from flask import Flask, request, jsonify
from src.forensic_agent import ForensicAgent
import asyncio

app = Flask(__name__)
agent = ForensicAgent()

@app.route('/verify', methods=['POST'])
def verify():
    file = request.files['file']
    file.save('temp.jpg')
    
    result = asyncio.run(agent.investigate('temp.jpg'))
    return jsonify(result)
```

### Django Integration

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from src.forensic_agent import ForensicAgent
import asyncio

@csrf_exempt
def verify_flyer(request):
    if request.method == 'POST':
        file = request.FILES['file']
        with open('temp.jpg', 'wb') as f:
            f.write(file.read())
        
        agent = ForensicAgent()
        result = asyncio.run(agent.investigate('temp.jpg'))
        return JsonResponse(result)
```

## Troubleshooting

### Common Issues

1. **Tesseract not found**
   - Install Tesseract OCR
   - Ensure it's in your PATH

2. **OpenAI API errors**
   - Check your API key in `.env`
   - Verify you have credits/quota

3. **Import errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

4. **Slow processing**
   - Check internet connection (for API calls)
   - Consider using local models for OCR
   - Optimize image size before processing

## Performance Tips

1. **Image Optimization**: Resize large images before processing
2. **Parallel Processing**: Domain checks run in parallel automatically
3. **Caching**: Consider caching domain lookups for repeated checks
4. **Rate Limiting**: Be mindful of API rate limits

## Next Steps

- Integrate with actual scam databases
- Add more verification sources
- Implement batch processing
- Add multi-language support
- Create mobile app integration

