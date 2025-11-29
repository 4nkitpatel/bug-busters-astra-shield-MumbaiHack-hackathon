# QR Code Image Processing & Gemini-Powered Search Enhancements

## Overview
Enhanced the system to extract ALL visible information from QR code images and use Gemini 3 Pro for intelligent Google searches to verify organizations and find recent updates.

## Key Enhancements

### 1. Comprehensive Text Extraction from QR Code Images

**Problem**: When images contained QR codes, the system was only extracting QR code data, missing visible text like organization names, locations, bank details, etc.

**Solution**:
- Enhanced Gemini prompt to extract ALL visible text in multiple languages (Hindi, English, regional languages)
- Prioritizes Gemini's `full_text` extraction (most accurate) over OCR
- Extracts:
  - Organization names (in any language)
  - Location information (cities, states)
  - Bank details (account numbers, IFSC codes, UPI IDs)
  - Contact information (phones, emails)
  - QR code content
  - Any other visible text

**Files Changed**:
- `src/image_processor.py` (lines 131-148, 61-95)

**Example**:
For "Red Cross Hoshiarpur" image:
- Extracts: "RED CROSS HOSHIARPUR", "District Red Cross Society", "Hoshiarpur", "UPI ID: districtredcrosshsp@idfcbank", "Account No.: 10157275177", "IFSC Code: IDFB0022152"

### 2. QR Code URL/Domain Verification

**Problem**: QR codes containing URLs were extracted but not verified.

**Solution**:
- Automatically extracts domains from QR code URLs
- Verifies QR code domains using:
  - Domain age check (WHOIS)
  - Scam database check
- Adds QR code domains to evidence collection

**Files Changed**:
- `src/image_processor.py` (lines 71-95)
- `src/forensic_agent.py` (lines 195-210)

**Example**:
If QR code contains `https://example.org/donate`:
- Extracts domain: `example.org`
- Checks domain age
- Checks scam database
- Includes in evidence

### 3. Gemini-Powered Intelligent Google Search

**Problem**: Basic search queries didn't find comprehensive information about organizations.

**Solution**:
- Uses Gemini 3 Pro to generate intelligent, context-aware search queries
- Generates 3-4 specific queries for each organization:
  1. Official registration/registry verification
  2. Recent news/updates
  3. Legitimacy verification
  4. Official website/contact information
- Searches Google using these queries
- Analyzes results for:
  - Official registry entries
  - Recent updates/news
  - Reputable platform listings
  - Verification status

**Files Changed**:
- `src/mcp_tools/search_mcp.py` (lines 15-16, 21-35, 154-250)

**Example**:
For "Red Cross Hoshiarpur":
- Gemini generates queries like:
  - "Red Cross Hoshiarpur official registration"
  - "Red Cross Hoshiarpur district society verified"
  - "Red Cross Hoshiarpur recent news 2024"
  - "District Red Cross Society Hoshiarpur official"

### 4. Location-Aware Organization Verification

**Problem**: Organization verification didn't use location context, leading to less accurate results.

**Solution**:
- Extracts location information from images (cities, states)
- Passes location to organization verification
- Uses location in search queries for better accuracy
- Example: "Red Cross Hoshiarpur" + "Hoshiarpur, Punjab" → more accurate results

**Files Changed**:
- `src/image_processor.py` (lines 140-141, 85-88)
- `src/forensic_agent.py` (lines 167-195)
- `src/mcp_tools/search_mcp.py` (lines 154-250)

### 5. Recent Updates/News Detection

**Problem**: System didn't search for recent news/updates about organizations.

**Solution**:
- Detects recent updates/news in search results
- Identifies keywords: "news", "update", "recent", "2024", "announcement"
- Stores recent updates with titles, URLs, snippets
- Includes recent updates in evidence points
- Adds recent updates as verification sources

**Files Changed**:
- `src/mcp_tools/search_mcp.py` (lines 220-230)
- `src/api.py` (lines 350-365, 400-420)

**Example Evidence Point**:
"Recent updates/news found about 'Red Cross Hoshiarpur': Red Cross Hoshiarpur launches new donation drive, District Red Cross Society updates 2024"

### 6. Enhanced Bank Details Extraction

**Problem**: Bank details (account numbers, IFSC codes, UPI IDs) weren't being extracted.

**Solution**:
- Gemini now extracts bank details as structured data:
  - Bank name
  - Account number
  - IFSC code
  - UPI ID
- UPI IDs are added to email entities for verification
- Account numbers stored as special entities

**Files Changed**:
- `src/image_processor.py` (lines 140-141, 85-88)

### 7. Multi-Language Support

**Problem**: System couldn't extract text in Hindi and regional languages.

**Solution**:
- Enhanced Gemini prompt to extract text in ALL languages
- Preserves original language in `full_text`
- Extracts organization names in original language
- Example: "श्री राम जन्मभूमि तीर्थ क्षेत्र" → Extracted correctly

**Files Changed**:
- `src/image_processor.py` (lines 131-148)

## Technical Architecture

### Enhanced Image Processing Flow

```
Image Input
    ↓
1. QR Code Extraction (pyzbar)
    ↓
2. OCR Text Extraction (Tesseract) - Hindi, English, etc.
    ↓
3. Gemini Vision Analysis
    ├─ full_text (ALL visible text)
    ├─ organization_names
    ├─ locations
    ├─ bank_details
    ├─ phone_numbers, emails, urls
    └─ image_type
    ↓
4. Merge All Sources
    ├─ Prioritize Gemini full_text
    ├─ Combine with OCR
    └─ Extract structured entities
    ↓
5. QR Code URL Extraction
    ├─ Extract domains from QR URLs
    └─ Add to verification queue
```

### Enhanced Organization Verification Flow

```
Organization Name + Location
    ↓
Gemini Query Generation
    ├─ Query 1: Official registration
    ├─ Query 2: Recent news/updates
    ├─ Query 3: Legitimacy verification
    └─ Query 4: Official website
    ↓
Google Search (4 queries)
    ↓
Result Analysis
    ├─ Official registry detection
    ├─ Recent updates detection
    ├─ Reputable platform detection
    └─ Verification status determination
    ↓
Evidence Collection
    ├─ Registration status
    ├─ Recent updates
    ├─ Search results
    └─ Verification status
```

## Data Structures

### Enhanced Vision Analysis Output
```python
{
    "full_text": "All visible text in original languages",
    "organization_names": ["Red Cross Hoshiarpur", "District Red Cross Society"],
    "locations": ["Hoshiarpur", "Punjab"],
    "bank_details": {
        "bank_name": "IDFC Bank Hoshiarpur",
        "account_number": "10157275177",
        "ifsc_code": "IDFB0022152",
        "upi_id": "districtredcrosshsp@idfcbank"
    },
    "phone_numbers": [...],
    "emails": [...],
    "urls": [...],
    "domains": [...],
    "image_type": "help_flyer",
    "description": "..."
}
```

### Enhanced Registry Check Results
```python
{
    "organization": "Red Cross Hoshiarpur",
    "type": "ngo",
    "registered": True/False,
    "verification_status": "verified" | "likely_legitimate" | "unknown",
    "registration_details": {...},
    "search_results": [...],
    "recent_updates": [
        {
            "title": "Red Cross Hoshiarpur launches new drive",
            "url": "https://...",
            "snippet": "...",
            "date": "2024-01-15T..."
        }
    ]
}
```

## Quality Control Checklist

✅ All visible text extracted (OCR + Gemini)
✅ Multi-language support (Hindi, English, regional)
✅ QR code URLs verified (domain age, scam check)
✅ Location-aware organization verification
✅ Gemini-powered intelligent search queries
✅ Recent updates/news detection
✅ Bank details extraction (UPI, account, IFSC)
✅ Enhanced evidence points with recent updates
✅ Recent updates added as verification sources

## Testing Recommendations

1. **Test with Red Cross Hoshiarpur image**:
   - Should extract: "RED CROSS HOSHIARPUR", "District Red Cross Society", "Hoshiarpur"
   - Should verify organization with location context
   - Should find recent updates if available
   - Should extract bank details

2. **Test with Ram Temple donation image**:
   - Should extract: "Shri Ram Janmabhoomi Teerth Kshetra", "Ayodhya", "Uttar Pradesh"
   - Should extract Hindi text correctly
   - Should verify organization
   - Should extract QR code URL if present

3. **Test with QR code containing URL**:
   - Should extract domain from QR URL
   - Should verify domain (age, scam check)
   - Should include in evidence

## Next Steps (Future Enhancements)

1. Add support for extracting crypto wallet addresses from QR codes
2. Add image quality assessment for better OCR
3. Add support for more regional languages
4. Cache search results to reduce API calls
5. Add confidence scores for extracted entities
6. Add support for extracting donation amounts/percentages

