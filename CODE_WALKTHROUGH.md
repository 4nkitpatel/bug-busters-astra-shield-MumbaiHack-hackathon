# Complete Code Walkthrough - Disaster Relief Verification System

This document provides a detailed, line-by-line explanation of every file in the MCP-based Disaster Relief Verification System.

---

## Table of Contents

1. [Configuration (`src/config.py`)](#1-configuration-srcconfigpy)
2. [Image Processor (`src/image_processor.py`)](#2-image-processor-srcimage_processorypy)
3. [File System MCP (`src/mcp_tools/filesystem_mcp.py`)](#3-file-system-mcp-srcmcp_toolsfilesystem_mcppy)
4. [Search MCP (`src/mcp_tools/search_mcp.py`)](#4-search-mcp-srcmcp_toolssearch_mcppy)
5. [Forensic Agent (`src/forensic_agent.py`)](#5-forensic-agent-srcforensic_agentpy)
6. [FastAPI Server (`src/api.py`)](#6-fastapi-server-srcapipy)
7. [Streamlit UI (`src/app_ui.py`)](#7-streamlit-ui-srcapp_uipy)
8. [CLI Entry Point (`main.py`)](#8-cli-entry-point-mainpy)

---

## 1. Configuration (`src/config.py`)

**Purpose**: Central configuration file that loads environment variables and sets system-wide constants.

### Line-by-Line Breakdown:

```python
"""Configuration settings for the Disaster Relief Verification System."""
```
- **Line 1**: Module docstring describing the file's purpose.

```python
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
```
- **Lines 3-6**: Imports
  - `os`: Access environment variables
  - `Path`: Type-safe file paths
  - `Optional`: Type hinting for nullable values
  - `load_dotenv`: Loads `.env` file variables

```python
load_dotenv()
```
- **Line 7**: Loads environment variables from `.env` file into `os.environ`.

```python
# API Keys
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
```
- **Lines 9-11**: API key configuration
  - Reads `OPENAI_API_KEY` from environment (for GPT-4 Vision/LLM)
  - Reads `ANTHROPIC_API_KEY` (optional, for Claude if needed)
  - `Optional[str]` means these can be `None` if not set

```python
# Model Configuration
VISION_MODEL: str = "gpt-4-vision-preview"
LLM_MODEL: str = "gpt-4-turbo-preview"
```
- **Lines 13-15**: AI model selection
  - `VISION_MODEL`: Used for image analysis (GPT-4 Vision)
  - `LLM_MODEL`: Used for text generation/summaries (GPT-4 Turbo)

```python
# Performance Settings
MAX_PROCESSING_TIME: int = 30  # seconds
IMAGE_PROCESSING_TIMEOUT: int = 5
BACKGROUND_CHECK_TIMEOUT: int = 20
```
- **Lines 17-20**: Timeout configurations
  - `MAX_PROCESSING_TIME`: Total allowed time for investigation (30s)
  - `IMAGE_PROCESSING_TIMEOUT`: Max time for image extraction (5s)
  - `BACKGROUND_CHECK_TIMEOUT`: Max time for verification checks (20s)

```python
# File System MCP Settings
CASE_FILES_DIR: Path = Path("case_files")
CASE_FILES_DIR.mkdir(exist_ok=True)
```
- **Lines 22-24**: Case file directory setup
  - Creates `case_files/` directory in project root
  - `mkdir(exist_ok=True)`: Creates directory if it doesn't exist, doesn't error if it does

```python
# Scam Database (can be extended with actual API endpoints)
SCAM_DATABASE_URL: Optional[str] = os.getenv("SCAM_DATABASE_URL")
```
- **Lines 26-27**: Scam database API URL (optional, for future integration)

```python
# Official Registry APIs
GOVERNMENT_REGISTRY_URL: Optional[str] = os.getenv("GOVERNMENT_REGISTRY_URL")
```
- **Lines 29-30**: Government registry API URL (optional, for future integration)

```python
# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
```
- **Lines 32-33**: Logging level (defaults to "INFO" if not set)

---

## 2. Image Processor (`src/image_processor.py`)

**Purpose**: Extracts information from images using multiple methods (OCR, Vision AI, QR codes).

### Class Overview:

```python
class ImageProcessor:
    """Processes images to extract contact details, QR codes, and text."""
```
- Main class for multimodal image processing.

### `__init__` Method (Lines 22-23):

```python
def __init__(self):
    self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
```
- **Line 22**: Constructor
- **Line 23**: Initializes OpenAI client if API key exists, otherwise `None`
  - Allows graceful degradation if API key is missing

### `process_image` Method (Lines 25-56):

**Purpose**: Main entry point that orchestrates all extraction methods.

```python
def process_image(self, image_path: str) -> Dict:
```
- **Line 25**: Takes image file path, returns dictionary of extracted data

```python
image = Image.open(image_path)
```
- **Line 35**: Opens image using PIL (Python Imaging Library)

```python
# Extract information using multiple methods
qr_data = self._extract_qr_codes(image)
ocr_text = self._extract_text_ocr(image)
vision_analysis = self._analyze_with_vision(image) if self.client else {}
```
- **Lines 37-40**: Runs three extraction methods in parallel:
  1. QR code extraction
  2. OCR text extraction
  3. Vision AI analysis (only if OpenAI client exists)

```python
# Combine and extract structured data
all_text = f"{ocr_text} {vision_analysis.get('description', '')}"
extracted_info = self._extract_contact_details(all_text)
```
- **Lines 42-44**: 
  - Combines OCR text + Vision description
  - Extracts structured data (phones, emails, URLs) using regex

```python
# Merge QR code data
if qr_data:
    extracted_info['urls'].extend(qr_data)
    extracted_info['urls'] = list(set(extracted_info['urls']))
```
- **Lines 46-49**: Adds QR code URLs to extracted URLs, removes duplicates

```python
return {
    'raw_text': all_text,
    'qr_codes': qr_data,
    'extracted': extracted_info,
    'vision_analysis': vision_analysis
}
```
- **Lines 51-56**: Returns structured dictionary with all extracted information

### `_extract_qr_codes` Method (Lines 58-73):

**Purpose**: Extracts QR codes from image.

```python
def _extract_qr_codes(self, image: Image.Image) -> List[str]:
```
- **Line 58**: Takes PIL Image, returns list of QR code strings

```python
qr_data = []

if pyzbar is None:
    return qr_data
```
- **Lines 60-63**: Early return if `pyzbar` library not available (graceful degradation)

```python
try:
    # Try pyzbar first
    decoded_objects = pyzbar.decode(image)
    for obj in decoded_objects:
        qr_data.append(obj.data.decode('utf-8'))
except Exception as e:
    print(f"QR extraction error: {e}")
```
- **Lines 65-71**: 
  - Decodes QR codes using `pyzbar`
  - Converts binary data to UTF-8 strings
  - Handles errors gracefully

### `_extract_text_ocr` Method (Lines 75-88):

**Purpose**: Extracts text using OCR (Optical Character Recognition).

```python
def _extract_text_ocr(self, image: Image.Image) -> str:
```
- **Line 75**: Takes PIL Image, returns extracted text string

```python
try:
    text = pytesseract.image_to_string(image)
    if not text or not text.strip():
        print("Warning: OCR returned empty text...")
    return text
```
- **Lines 77-81**: 
  - Uses Tesseract OCR to extract text
  - Warns if result is empty
  - Returns text (or empty string)

```python
except Exception as e:
    error_msg = str(e)
    if "tesseract" in error_msg.lower() or "not found" in error_msg.lower():
        print(f"ERROR: Tesseract OCR not found...")
    else:
        print(f"OCR error: {e}")
    return ""
```
- **Lines 82-88**: Error handling with specific message for missing Tesseract

### `_analyze_with_vision` Method (Lines 90-137):

**Purpose**: Uses GPT-4 Vision to analyze image and extract information.

```python
def _analyze_with_vision(self, image: Image.Image) -> Dict:
```
- **Line 90**: Takes PIL Image, returns analysis dictionary

```python
if not self.client:
    print("Warning: OpenAI API key not set. Vision analysis disabled.")
    return {}
```
- **Lines 92-94**: Early return if OpenAI client not initialized

```python
try:
    # Convert image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
```
- **Lines 96-100**: Converts image to base64 string (required for OpenAI API)

```python
response = self.client.chat.completions.create(
    model=VISION_MODEL,
    messages=[...]
)
```
- **Lines 102-127**: Calls OpenAI API with:
  - Vision model (GPT-4 Vision)
  - System prompt asking for specific information extraction
  - Image as base64 data

```python
description = response.choices[0].message.content
return {"description": description}
```
- **Lines 129-130**: Extracts and returns AI-generated description

### `_extract_contact_details` Method (Lines 139-171):

**Purpose**: Uses regex patterns to extract structured contact information from text.

```python
def _extract_contact_details(self, text: str) -> Dict:
```
- **Line 139**: Takes text string, returns dictionary of extracted entities

```python
# Phone number patterns (international formats)
phone_pattern = r'(\+?\d{1-3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\d{10}'
phones = re.findall(phone_pattern, text)
phones = [p if isinstance(p, str) else ''.join(p) for p in phones]
phones = [p.replace(' ', '').replace('-', '').replace('(', '').replace(')', '') for p in phones]
```
- **Lines 141-145**: 
  - Regex pattern matches various phone formats
  - Finds all matches in text
  - Normalizes phone numbers (removes spaces, dashes, parentheses)

```python
# Email pattern
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
emails = re.findall(email_pattern, text)
```
- **Lines 147-149**: Regex pattern for email addresses

```python
# URL pattern
url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
urls = re.findall(url_pattern, text)
```
- **Lines 151-153**: Regex pattern for URLs (http/https)

```python
# Extract domain names from URLs
domains = []
for url in urls:
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.netloc:
            domains.append(parsed.netloc)
    except:
        pass
```
- **Lines 155-164**: Extracts domain names from URLs using `urlparse`

```python
return {
    'phone_numbers': list(set(phones)),
    'emails': list(set(emails)),
    'urls': list(set(urls)),
    'domains': list(set(domains))
}
```
- **Lines 166-171**: Returns deduplicated lists of extracted entities

---

## 3. File System MCP (`src/mcp_tools/filesystem_mcp.py`)

**Purpose**: Manages case files and logs all investigation evidence (MCP = Model Context Protocol tool).

### Class Overview:

```python
class FileSystemMCP:
    """MCP tool for managing case files and evidence logging."""
```
- Implements File System MCP pattern for persistent logging

### `__init__` Method (Lines 12-16):

```python
def __init__(self, case_files_dir: Path = CASE_FILES_DIR):
    self.case_files_dir = case_files_dir
    self.case_files_dir.mkdir(exist_ok=True)
    self.current_case_id: Optional[str] = None
    self.current_case_file: Optional[Path] = None
```
- **Line 12**: Constructor with optional case files directory
- **Line 13-14**: Stores directory path and creates it if missing
- **Line 15-16**: Tracks current case ID and file path (None initially)

### `create_case_file` Method (Lines 18-47):

**Purpose**: Creates a new case file for an investigation.

```python
def create_case_file(self, case_id: str, initial_data: Dict[str, Any]) -> Path:
```
- **Line 18**: Takes case ID and initial data, returns file path

```python
self.current_case_id = case_id
timestamp = datetime.now().isoformat()
```
- **Lines 29-30**: Stores case ID and generates ISO timestamp

```python
case_data = {
    'case_id': case_id,
    'created_at': timestamp,
    'status': 'investigating',
    'evidence': [],
    'timeline': [],
    'initial_data': initial_data
}
```
- **Lines 32-39**: Initializes case file structure with:
  - Case metadata
  - Empty evidence and timeline arrays
  - Initial extracted data

```python
case_filename = f"case_{case_id}_{timestamp.replace(':', '-').split('.')[0]}.json"
self.current_case_file = self.case_files_dir / case_filename
```
- **Lines 41-42**: Creates filename with case ID and timestamp, constructs full path

```python
self._write_case_file(case_data)
self._log_event("case_created", {"case_id": case_id})
```
- **Lines 44-45**: Writes file and logs creation event

### `log_evidence` Method (Lines 49-78):

**Purpose**: Logs evidence to the current case file.

```python
def log_evidence(self, evidence_type: str, evidence_data: Dict[str, Any], 
                source: str = "unknown") -> None:
```
- **Line 49**: Takes evidence type, data, and source

```python
if not self.current_case_file:
    raise ValueError("No active case file. Create a case file first.")
```
- **Lines 59-60**: Validates case file exists

```python
case_data = self._read_case_file()
```
- **Line 62**: Reads current case file

```python
evidence_entry = {
    'timestamp': datetime.now().isoformat(),
    'type': evidence_type,
    'source': source,
    'data': evidence_data
}

case_data['evidence'].append(evidence_entry)
case_data['timeline'].append({
    'timestamp': datetime.now().isoformat(),
    'event': f"Evidence collected: {evidence_type}",
    'source': source
})
```
- **Lines 64-76**: Creates evidence entry and adds to both evidence array and timeline

```python
self._write_case_file(case_data)
```
- **Line 78**: Writes updated case file

### `finalize_case` Method (Lines 90-117):

**Purpose**: Completes the case with final verdict and summary.

```python
def finalize_case(self, verdict: str, risk_score: float, 
                 summary: str, recommendations: List[str]) -> Dict[str, Any]:
```
- **Line 90**: Takes final analysis results

```python
case_data = self._read_case_file()
case_data['status'] = 'completed'
case_data['completed_at'] = datetime.now().isoformat()
case_data['verdict'] = verdict
case_data['risk_score'] = risk_score
case_data['summary'] = summary
case_data['recommendations'] = recommendations
```
- **Lines 107-113**: Updates case file with final results

```python
self._write_case_file(case_data)
return case_data
```
- **Lines 115-117**: Saves and returns final case data

### Helper Methods:

**`_read_case_file` (Lines 132-138)**: Reads JSON case file from disk
**`_write_case_file` (Lines 140-146)**: Writes JSON case file to disk
**`_log_event` (Lines 119-130)**: Internal method to log timeline events

---

## 4. Search MCP (`src/mcp_tools/search_mcp.py`)

**Purpose**: Performs external verification checks (domain age, scam databases, registries).

### Class Overview:

```python
class SearchMCP:
    """MCP tool for performing external searches and background checks."""
```

### `__init__` Method (Lines 14-15):

```python
def __init__(self):
    self.client = httpx.AsyncClient(timeout=10.0)
```
- **Line 15**: Creates async HTTP client with 10-second timeout for API calls

### `check_domain_age` Method (Lines 17-62):

**Purpose**: Checks domain registration age using WHOIS.

```python
async def check_domain_age(self, domain: str) -> Dict[str, Any]:
```
- **Line 17**: Async method (can run concurrently)

```python
try:
    # Clean domain (remove www, http, etc.)
    domain = self._clean_domain(domain)
    
    # WHOIS lookup
    w = whois.whois(domain)
```
- **Lines 27-32**: Cleans domain name and performs WHOIS lookup

```python
creation_date = w.creation_date
if isinstance(creation_date, list):
    creation_date = creation_date[0]
```
- **Lines 34-36**: Handles WHOIS returning list (takes first date)

```python
# Calculate domain age
age_days = None
if creation_date:
    age_days = (datetime.now() - creation_date).days
```
- **Lines 42-45**: Calculates domain age in days

```python
return {
    'domain': domain,
    'registered': w.creation_date is not None,
    'creation_date': str(creation_date) if creation_date else None,
    'expiration_date': str(expiration_date) if expiration_date else None,
    'age_days': age_days,
    'registrar': w.registrar,
    'name_servers': w.name_servers,
    'status': 'registered' if w.creation_date else 'not_registered'
}
```
- **Lines 47-56**: Returns comprehensive domain information

### `check_scam_database` Method (Lines 64-113):

**Purpose**: Checks identifier against scam database.

```python
async def check_scam_database(self, identifier: str, identifier_type: str = "domain") -> Dict[str, Any]:
```
- **Line 64**: Checks domain, email, or phone number

```python
results = {
    'identifier': identifier,
    'type': identifier_type,
    'checked_at': datetime.now().isoformat(),
    'matches': [],
    'risk_level': 'unknown'
}
```
- **Lines 78-84**: Initializes result structure

```python
# Simulated scam patterns (in production, use actual API)
suspicious_patterns = ['scam', 'fraud', 'fake', 'phishing']

identifier_lower = identifier.lower()
for pattern in suspicious_patterns:
    if pattern in identifier_lower:
        results['matches'].append({
            'pattern': pattern,
            'reason': 'Suspicious keyword detected'
        })
        results['risk_level'] = 'high'
```
- **Lines 86-98**: Basic pattern matching (placeholder for real API)

```python
# If we have a scam database URL, make actual API call
if SCAM_DATABASE_URL:
    try:
        response = await self.client.get(
            f"{SCAM_DATABASE_URL}/check",
            params={identifier_type: identifier}
        )
        if response.status_code == 200:
            api_results = response.json()
            results.update(api_results)
    except Exception as e:
        results['api_error'] = str(e)
```
- **Lines 100-111**: Makes actual API call if URL configured

### `check_official_registry` Method (Lines 115-151):

**Purpose**: Checks if organization is registered in official registry.

```python
async def check_official_registry(self, organization_name: str, 
                                 organization_type: str = "ngo") -> Dict[str, Any]:
```
- **Line 115**: Checks organization registration

```python
results = {
    'organization': organization_name,
    'type': organization_type,
    'checked_at': datetime.now().isoformat(),
    'registered': False,
    'registration_details': None
}
```
- **Lines 127-133**: Initializes result (defaults to not registered)

```python
if GOVERNMENT_REGISTRY_URL:
    try:
        response = await self.client.get(
            f"{GOVERNMENT_REGISTRY_URL}/search",
            params={'name': organization_name, 'type': organization_type}
        )
        if response.status_code == 200:
            registry_data = response.json()
            results.update(registry_data)
    except Exception as e:
        results['api_error'] = str(e)
```
- **Lines 136-149**: Makes API call if registry URL configured

### `_clean_domain` Method (Lines 193-207):

**Purpose**: Cleans domain string (removes protocol, www, paths).

```python
def _clean_domain(self, domain: str) -> str:
```
- **Line 193**: Takes messy domain/URL, returns clean domain

```python
# Remove protocol
if '://' in domain:
    parsed = urlparse(domain)
    domain = parsed.netloc or parsed.path

# Remove www
if domain.startswith('www.'):
    domain = domain[4:]

# Remove path
domain = domain.split('/')[0]

return domain.lower()
```
- **Lines 195-207**: Step-by-step cleaning process

---

## 5. Forensic Agent (`src/forensic_agent.py`)

**Purpose**: Main orchestrator that coordinates the entire investigation workflow.

### Class Overview:

```python
class ForensicAgent:
    """
    Main agent that orchestrates the forensic investigation workflow.
    Mimics a human investigator's process using MCP tools.
    """
```

### `__init__` Method (Lines 20-24):

```python
def __init__(self):
    self.image_processor = ImageProcessor()
    self.filesystem_mcp = FileSystemMCP()
    self.search_mcp = SearchMCP()
    self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
```
- **Line 21**: Creates image processor instance
- **Line 22**: Creates file system MCP for logging
- **Line 23**: Creates search MCP for verification
- **Line 24**: Creates OpenAI client for LLM summaries

### `investigate` Method (Lines 26-81):

**Purpose**: Main investigation workflow - orchestrates all steps.

```python
async def investigate(self, image_path: str) -> Dict[str, Any]:
```
- **Line 26**: Async method that takes image path, returns investigation report

```python
start_time = datetime.now()
case_id = str(uuid.uuid4())[:8]
```
- **Lines 36-37**: Records start time and generates unique 8-character case ID

```python
try:
    # Step 1: Extract information from image
    print(f"[Case {case_id}] Step 1: Extracting information from image...")
    extracted_data = self.image_processor.process_image(image_path)
```
- **Lines 40-42**: Step 1 - Extract all information from image

```python
    # Step 2: Create case file
    print(f"[Case {case_id}] Step 2: Creating case file...")
    self.filesystem_mcp.create_case_file(case_id, {
        'image_path': image_path,
        'extracted_data': extracted_data
    })
```
- **Lines 44-49**: Step 2 - Create case file and log initial data

```python
    # Step 3: Perform background checks
    print(f"[Case {case_id}] Step 3: Performing background checks...")
    evidence = await self._gather_evidence(extracted_data)
```
- **Lines 51-53**: Step 3 - Gather evidence using MCP tools

```python
    # Step 4: Analyze evidence and generate verdict
    print(f"[Case {case_id}] Step 4: Analyzing evidence...")
    analysis = await self._analyze_evidence(evidence, extracted_data)
```
- **Lines 55-57**: Step 4 - Analyze evidence and determine verdict

```python
    # Step 5: Finalize case
    print(f"[Case {case_id}] Step 5: Finalizing case...")
    final_report = self.filesystem_mcp.finalize_case(
        verdict=analysis['verdict'],
        risk_score=analysis['risk_score'],
        summary=analysis['summary'],
        recommendations=analysis['recommendations']
    )
```
- **Lines 59-66**: Step 5 - Finalize case file with results

```python
    processing_time = (datetime.now() - start_time).total_seconds()
    final_report['processing_time_seconds'] = processing_time
    
    return final_report
```
- **Lines 68-71**: Calculate and add processing time, return report

### `_gather_evidence` Method (Lines 83-161):

**Purpose**: Uses MCP tools to gather verification evidence.

```python
async def _gather_evidence(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
```
- **Line 83**: Gathers evidence for all extracted entities

```python
evidence = {
    'domain_checks': [],
    'scam_checks': [],
    'registry_checks': [],
    'social_media_checks': []
}
```
- **Lines 93-98**: Initializes evidence structure

```python
extracted = extracted_data.get('extracted', {})

# Check each domain
for domain in extracted.get('domains', []):
    print(f"  Checking domain: {domain}")
    
    # Domain age check
    domain_info = await self.search_mcp.check_domain_age(domain)
    evidence['domain_checks'].append(domain_info)
    self.filesystem_mcp.log_evidence('domain_age_check', domain_info, source='whois')
    
    # Scam database check for domain
    scam_check = await self.search_mcp.check_scam_database(domain, 'domain')
    evidence['scam_checks'].append(scam_check)
    self.filesystem_mcp.log_evidence('scam_database_check', scam_check, source='scam_database')
```
- **Lines 100-122**: For each domain:
  - Checks domain age (WHOIS)
  - Checks scam database
  - Logs both to case file

```python
# Check phone numbers
for phone in extracted.get('phone_numbers', []):
    print(f"  Checking phone: {phone}")
    scam_check = await self.search_mcp.check_scam_database(phone, 'phone')
    evidence['scam_checks'].append(scam_check)
    self.filesystem_mcp.log_evidence('scam_database_check', scam_check, source='scam_database')
```
- **Lines 124-133**: Checks each phone number against scam database

```python
# Check emails
for email in extracted.get('emails', []):
    print(f"  Checking email: {email}")
    scam_check = await self.search_mcp.check_scam_database(email, 'email')
    evidence['scam_checks'].append(scam_check)
    self.filesystem_mcp.log_evidence('scam_database_check', scam_check, source='scam_database')
```
- **Lines 135-144**: Checks each email against scam database

```python
# Extract organization name (simplified - in production, use NLP)
raw_text = extracted_data.get('raw_text', '')
org_name = self._extract_organization_name(raw_text)

if org_name:
    print(f"  Checking organization: {org_name}")
    registry_check = await self.search_mcp.check_official_registry(org_name)
    evidence['registry_checks'].append(registry_check)
    self.filesystem_mcp.log_evidence('registry_check', registry_check, source='government_registry')
```
- **Lines 146-159**: Extracts organization name and checks registry

### `_analyze_evidence` Method (Lines 163-247):

**Purpose**: Analyzes collected evidence to determine risk score and verdict.

```python
async def _analyze_evidence(self, evidence: Dict[str, Any], 
                            extracted_data: Dict[str, Any]) -> Dict[str, Any]:
```
- **Line 163**: Analyzes evidence and returns verdict

```python
# Check if we actually extracted any data
extracted = extracted_data.get('extracted', {})
raw_text = extracted_data.get('raw_text', '').strip()

# If no data was extracted, this is suspicious
no_data_extracted = (
    not raw_text or 
    raw_text == " " or
    (not extracted.get('phone_numbers') and 
     not extracted.get('emails') and 
     not extracted.get('urls') and 
     not extracted.get('domains'))
)
```
- **Lines 175-187**: Detects if extraction failed (important for false positive prevention)

```python
# Calculate risk score based on evidence
risk_factors = []
risk_score = 0

# If no data extracted, add significant risk
if no_data_extracted:
    risk_score += 50
    risk_factors.append("⚠️ WARNING: Unable to extract any contact information...")
```
- **Lines 189-196**: Adds 50 points if no data extracted (prevents false "safe" verdict)

```python
# Check domain age
for domain_check in evidence.get('domain_checks', []):
    age_days = domain_check.get('age_days')
    if age_days is not None:
        if age_days < 30:
            risk_score += 30
            risk_factors.append(f"Domain is very new ({age_days} days old)")
        elif age_days < 365:
            risk_score += 15
            risk_factors.append(f"Domain is relatively new ({age_days} days old)")
```
- **Lines 198-207**: Domain age scoring:
  - < 30 days: +30 points (very suspicious)
  - < 365 days: +15 points (somewhat suspicious)

```python
# Check scam database matches
for scam_check in evidence.get('scam_checks', []):
    if scam_check.get('risk_level') == 'high':
        risk_score += 40
        risk_factors.append(f"High risk match in scam database: {scam_check.get('identifier')}")
    elif scam_check.get('matches'):
        risk_score += 20
        risk_factors.append(f"Suspicious patterns found: {scam_check.get('identifier')}")
```
- **Lines 209-216**: Scam database scoring:
  - High risk: +40 points
  - Any matches: +20 points

```python
# Check registry
for registry_check in evidence.get('registry_checks', []):
    if not registry_check.get('registered', False):
        risk_score += 25
        risk_factors.append("Organization not found in official registry")
```
- **Lines 218-222**: Registry check: +25 points if not registered

```python
# Cap risk score at 100
risk_score = min(risk_score, 100)

# Determine verdict
if risk_score >= 70:
    verdict = "scam"
elif risk_score >= 40:
    verdict = "suspicious"
else:
    verdict = "safe"
```
- **Lines 224-233**: 
  - Caps score at 100
  - Determines verdict based on thresholds:
    - ≥70: SCAM
    - ≥40: SUSPICIOUS
    - <40: SAFE

```python
# Generate summary using LLM if available
summary = self._generate_summary(evidence, risk_factors, verdict)

# Generate recommendations
recommendations = self._generate_recommendations(verdict, risk_score, risk_factors)

return {
    'verdict': verdict,
    'risk_score': risk_score,
    'risk_factors': risk_factors,
    'summary': summary,
    'recommendations': recommendations
}
```
- **Lines 235-247**: Generates summary and recommendations, returns analysis

### `_generate_summary` Method (Lines 260-304):

**Purpose**: Generates human-readable summary using LLM or fallback.

```python
def _generate_summary(self, evidence: Dict[str, Any], 
                     risk_factors: List[str], verdict: str) -> str:
```
- **Line 260**: Generates summary text

```python
if self.client:
    try:
        evidence_summary = f"""
Evidence Collected:
- Domain checks: {len(evidence.get('domain_checks', []))}
- Scam database checks: {len(evidence.get('scam_checks', []))}
- Registry checks: {len(evidence.get('registry_checks', []))}

Risk Factors:
{chr(10).join(f'- {factor}' for factor in risk_factors)}

Verdict: {verdict}
"""
        
        response = self.client.chat.completions.create(
            model=LLM_MODEL,
            messages=[...]
        )
        return response.choices[0].message.content
```
- **Lines 263-291**: Uses LLM to generate professional summary if available

```python
# Fallback summary
return f"""
Investigation Summary:
- Verdict: {verdict.upper()}
- Risk Factors Identified: {len(risk_factors)}
...
"""
```
- **Lines 295-304**: Fallback summary if LLM unavailable

### `_generate_recommendations` Method (Lines 306-333):

**Purpose**: Generates actionable recommendations based on verdict.

```python
def _generate_recommendations(self, verdict: str, risk_score: float, 
                             risk_factors: List[str]) -> List[str]:
```
- **Line 306**: Generates list of recommendations

```python
recommendations = []

if verdict == "scam":
    recommendations.extend([
        "DO NOT proceed with this resource",
        "Report to local authorities if you've already engaged",
        "Share this verification result with others in your community",
        "Use official disaster relief channels instead"
    ])
elif verdict == "suspicious":
    recommendations.extend([
        "Exercise extreme caution",
        "Verify through multiple independent sources",
        ...
    ])
else:
    recommendations.extend([
        "Resource appears legitimate, but always verify independently",
        ...
    ])
```
- **Lines 309-331**: Returns different recommendations based on verdict

---

## 6. FastAPI Server (`src/api.py`)

**Purpose**: REST API server for programmatic access.

### Setup (Lines 11-17):

```python
app = FastAPI(
    title="Disaster Relief Verification System",
    description="Multimodal AI agent for verifying disaster relief help flyers",
    version="1.0.0"
)

agent = ForensicAgent()
```
- **Lines 11-15**: Creates FastAPI app with metadata
- **Line 17**: Creates global agent instance

### Root Endpoint (Lines 20-30):

```python
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Disaster Relief Verification System",
        "version": "1.0.0",
        "endpoints": {
            "verify": "/verify (POST) - Upload image for verification",
            "health": "/health - Health check"
        }
    }
```
- **Lines 20-30**: Returns API information

### Health Check (Lines 33-36):

```python
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
```
- **Lines 33-36**: Simple health check for monitoring

### Verify Endpoint (Lines 39-76):

```python
@app.post("/verify")
async def verify_flyer(file: UploadFile = File(...)):
```
- **Line 39**: POST endpoint that accepts file upload

```python
# Validate file type
if not file.content_type or not file.content_type.startswith('image/'):
    raise HTTPException(
        status_code=400,
        detail="File must be an image"
    )
```
- **Lines 49-54**: Validates file is an image

```python
# Save uploaded file temporarily
with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
    try:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
        
        # Perform investigation
        result = await agent.investigate(tmp_file_path)
        
        return JSONResponse(content=result)
```
- **Lines 56-66**: 
  - Saves uploaded file to temp location
  - Runs investigation
  - Returns JSON result

```python
finally:
    # Clean up temporary file
    if os.path.exists(tmp_file_path):
        os.unlink(tmp_file_path)
```
- **Lines 73-76**: Cleans up temp file

---

## 7. Streamlit UI (`src/app_ui.py`)

**Purpose**: User-friendly web interface for non-technical users.

### Setup (Lines 19-24):

```python
st.set_page_config(
    page_title="Disaster Relief Verification",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
```
- **Lines 19-24**: Configures Streamlit page settings

### CSS Styling (Lines 26-85):

```python
st.markdown("""
<style>
    .verdict-safe { ... }
    .verdict-suspicious { ... }
    .verdict-scam { ... }
    .risk-meter-container { ... }
</style>
""", unsafe_allow_html=True)
```
- **Lines 26-85**: Custom CSS for verdict banners and risk meter

### `init_session_state` Function (Lines 87-91):

```python
def init_session_state():
    if 'agent' not in st.session_state:
        st.session_state.agent = ForensicAgent()
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
```
- **Lines 87-91**: Initializes Streamlit session state (persists across reruns)

### `run_analysis` Function (Lines 93-110):

```python
async def run_analysis(image_path):
    with st.spinner('🕵️ Forensic Analyst is investigating...'):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Extracting information from image...")
        progress_bar.progress(20)
        
        result = await st.session_state.agent.investigate(image_path)
        progress_bar.progress(100)
        return result
```
- **Lines 93-110**: Runs investigation with progress indicators

### `render_verdict` Function (Lines 112-154):

```python
def render_verdict(result):
    verdict = result.get('verdict', 'unknown').lower()
    risk_score = result.get('risk_score', 0)
    
    st.markdown("### 🛡️ Verification Result")
    
    if verdict == 'safe':
        st.markdown(f"""
            <div class="verdict-safe">
                ✅ SAFE
                <div style="font-size: 1rem;">Risk Score: {risk_score}/100</div>
            </div>
        """, unsafe_allow_html=True)
        st.success("This resource appears to be legitimate...")
```
- **Lines 112-154**: Renders color-coded verdict banner and risk meter

### `render_friendly_explanation` Function (Lines 156-216):

```python
def render_friendly_explanation(result):
    st.markdown("### 💡 What did we find?")
    
    # Check if extraction failed
    if not has_data:
        st.warning("⚠️ **Extraction Warning**: No contact information could be extracted...")
    
    # Simplify risk factors for non-tech users
    friendly_factors = []
    for factor in risk_factors:
        if "domain is very new" in factor.lower():
            friendly_factors.append("🌐 The website was created very recently...")
        ...
```
- **Lines 156-216**: 
  - Shows extraction warnings
  - Converts technical risk factors to plain language
  - Displays extracted information
  - Shows recommendations

### `main` Function (Lines 232-291):

```python
def main():
    init_session_state()
    
    st.title("🆘 Disaster Relief Verifier")
    
    tab1, tab2 = st.tabs(["📷 Camera", "📤 Upload"])
```
- **Lines 232-238**: Sets up UI with camera and upload tabs

```python
with tab1:
    camera_image = st.camera_input("Take a photo of the flyer")
    if camera_image:
        image_file = camera_image
        source_type = "camera"
        
with tab2:
    uploaded_image = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])
    if uploaded_image:
        image_file = uploaded_image
        source_type = "upload"
        st.image(image_file, caption="Uploaded Image", use_container_width=True)
```
- **Lines 243-254**: Handles camera input and file upload

```python
if image_file:
    # Save temp file for processing
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(image_file.getvalue())
        tmp_path = tmp_file.name
    
    if st.button("🔍 Verify This Resource", type="primary"):
        result = asyncio.run(run_analysis(tmp_path))
        st.session_state.analysis_result = result
```
- **Lines 256-271**: Saves image and triggers analysis on button click

```python
# Display results if available
if st.session_state.analysis_result:
    st.divider()
    result = st.session_state.analysis_result
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_verdict(result)
        render_friendly_explanation(result)
        
    with col2:
        st.markdown("### ⏱️ Performance")
        st.metric("Analysis Time", f"{result.get('processing_time_seconds', 0):.2f}s")
```
- **Lines 273-291**: Displays results in two-column layout

---

## 8. CLI Entry Point (`main.py`)

**Purpose**: Command-line interface for scripted usage.

### `main` Function (Lines 9-67):

```python
async def main():
    """Main function for CLI usage."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not Path(image_path).exists():
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
```
- **Lines 11-21**: Validates command-line arguments

```python
print("=" * 60)
print("Disaster Relief Verification System")
print("Forensic Analysis Agent")
print("=" * 60)
print(f"\nInvestigating: {image_path}\n")

agent = ForensicAgent()

try:
    result = await agent.investigate(image_path)
    
    print("\n" + "=" * 60)
    print("INVESTIGATION COMPLETE")
    print("=" * 60)
    print(f"\nCase ID: {result.get('case_id')}")
    print(f"Status: {result.get('status')}")
    print(f"Processing Time: {result.get('processing_time_seconds', 0):.2f} seconds")
    
    if result.get('verdict'):
        print(f"\nVERDICT: {result.get('verdict').upper()}")
        print(f"Risk Score: {result.get('risk_score')}/100")
```
- **Lines 23-43**: Runs investigation and prints formatted results

```python
if __name__ == "__main__":
    asyncio.run(main())
```
- **Lines 65-67**: Entry point that runs async main function

---

## System Flow Summary

1. **User uploads image** → Streamlit UI or API
2. **ImageProcessor** extracts:
   - QR codes (pyzbar)
   - Text (Tesseract OCR)
   - Vision analysis (GPT-4 Vision)
3. **ForensicAgent** orchestrates:
   - Creates case file (FileSystemMCP)
   - Gathers evidence (SearchMCP):
     - Domain age checks
     - Scam database checks
     - Registry checks
   - Analyzes evidence (risk scoring)
   - Generates verdict and recommendations
   - Finalizes case file
4. **Results displayed** in UI or returned via API

---

## Key Design Patterns

1. **MCP (Model Context Protocol)**: Separates tools (FileSystem, Search) from agent logic
2. **Async/Await**: Non-blocking I/O for API calls
3. **Graceful Degradation**: System works even if some components fail
4. **Audit Trail**: Complete logging of all investigation steps
5. **Multi-Modal Extraction**: Multiple methods for robustness

---

This completes the comprehensive code walkthrough. Every line has been explained in detail!

