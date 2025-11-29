# System Flow Diagram

## Complete Investigation Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INPUT                                    │
│              Photo of Help Flyer/QR Code                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 1: MULTIMODAL PROCESSING                      │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ImageProcessor.process_image()                            │ │
│  │                                                            │ │
│  │  • OCR Text Extraction (Tesseract)                        │ │
│  │  • QR Code Decoding (pyzbar)                              │ │
│  │  • Vision Analysis (GPT-4 Vision)                        │ │
│  │  • Contact Detail Extraction (Regex/NLP)                 │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Output: {                                                      │
│    raw_text: "...",                                            │
│    qr_codes: ["https://..."],                                  │
│    extracted: {                                                │
│      phone_numbers: ["+1-234-567-8900"],                       │
│      emails: ["contact@example.com"],                          │
│      urls: ["https://example.com"],                            │
│      domains: ["example.com"]                                  │
│    }                                                            │
│  }                                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 2: CASE FILE CREATION                         │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ FileSystemMCP.create_case_file()                         │ │
│  │                                                            │ │
│  │  • Generate unique case_id                                │ │
│  │  • Create timestamped JSON case file                      │ │
│  │  • Initialize evidence log                                │ │
│  │  • Log initial extracted data                             │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Output: case_files/case_abc123_2024-01-15T10-30-00.json       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 3: EVIDENCE GATHERING (MCP TOOLS)            │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ForensicAgent._gather_evidence()                         │ │
│  │                                                            │ │
│  │  For each DOMAIN:                                         │ │
│  │    ├─ SearchMCP.check_domain_age()                       │ │
│  │    │   └─ WHOIS lookup → age, registrar, status          │ │
│  │    │                                                      │ │
│  │    ├─ SearchMCP.check_scam_database()                   │ │
│  │    │   └─ Cross-reference with scam DB                   │ │
│  │    │                                                      │ │
│  │    └─ FileSystemMCP.log_evidence()                       │ │
│  │       └─ Log to case file                                │ │
│  │                                                            │ │
│  │  For each PHONE NUMBER:                                   │ │
│  │    ├─ SearchMCP.check_scam_database(phone)               │ │
│  │    └─ FileSystemMCP.log_evidence()                       │ │
│  │                                                            │ │
│  │  For each EMAIL:                                          │ │
│  │    ├─ SearchMCP.check_scam_database(email)               │ │
│  │    └─ FileSystemMCP.log_evidence()                       │ │
│  │                                                            │ │
│  │  For ORGANIZATION NAME:                                   │ │
│  │    ├─ SearchMCP.check_official_registry()                │ │
│  │    └─ FileSystemMCP.log_evidence()                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  All evidence logged to case file in real-time                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 4: EVIDENCE ANALYSIS                          │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ ForensicAgent._analyze_evidence()                        │ │
│  │                                                            │ │
│  │  Risk Scoring:                                            │ │
│  │    • Domain age < 30 days → +30 points                   │ │
│  │    • Domain age < 365 days → +15 points                  │ │
│  │    • Scam DB high risk → +40 points                       │ │
│  │    • Scam DB matches → +20 points                         │ │
│  │    • Not in registry → +25 points                         │ │
│  │                                                            │ │
│  │  Verdict Logic:                                           │ │
│  │    • risk_score >= 70 → "scam"                            │ │
│  │    • risk_score >= 40 → "suspicious"                      │ │
│  │    • risk_score < 40 → "safe"                             │ │
│  │                                                            │ │
│  │  Summary Generation:                                      │ │
│  │    • LLM generates human-readable summary                 │ │
│  │    • Includes risk factors and evidence                   │ │
│  │                                                            │ │
│  │  Recommendations:                                         │ │
│  │    • Based on verdict and risk factors                    │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 5: CASE FINALIZATION                          │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ FileSystemMCP.finalize_case()                            │ │
│  │                                                            │ │
│  │  • Update case status to "completed"                     │ │
│  │  • Add verdict, risk_score, summary                      │ │
│  │  • Add recommendations                                    │ │
│  │  • Calculate processing time                              │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Final Case File Structure:                                     │
│  {                                                              │
│    case_id: "abc123",                                          │
│    status: "completed",                                        │
│    verdict: "suspicious",                                      │
│    risk_score: 55,                                             │
│    evidence: [...],                                            │
│    timeline: [...],                                            │
│    summary: "...",                                             │
│    recommendations: [...]                                       │
│  }                                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    USER OUTPUT                                  │
│  • Verification Result (Safe/Suspicious/Scam)                  │
│  • Risk Score (0-100)                                           │
│  • Evidence Summary                                             │
│  • Recommendations                                              │
│  • Case File Location                                           │
└─────────────────────────────────────────────────────────────────┘
```

## MCP Tools Interaction Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Forensic Agent                            │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               │                              │
               ▼                              ▼
    ┌──────────────────┐          ┌──────────────────┐
    │  File System MCP │          │    Search MCP    │
    └────────┬─────────┘          └────────┬─────────┘
             │                             │
             │                             │
    ┌────────▼─────────┐         ┌────────▼─────────┐
    │  Case File Log   │         │  External APIs    │
    │                  │         │                   │
    │  • Evidence      │         │  • WHOIS          │
    │  • Timeline      │         │  • Scam DB        │
    │  • Verdict       │         │  • Registry       │
    │  • Summary       │         │  • Social Media   │
    └──────────────────┘         └───────────────────┘
```

## Timing Breakdown (Target: < 30 seconds)

```
Total Time Budget: 30 seconds
├─ Image Processing: 5 seconds
│  ├─ OCR: 2s
│  ├─ QR Decode: 1s
│  └─ Vision API: 2s
│
├─ Evidence Gathering: 20 seconds
│  ├─ Domain Checks: 8s (parallel)
│  ├─ Scam DB Checks: 8s (parallel)
│  └─ Registry Checks: 4s
│
└─ Analysis & Report: 5 seconds
   ├─ Risk Scoring: 1s
   ├─ LLM Summary: 3s
   └─ Finalization: 1s
```

## Parallel Processing Opportunities

```
Evidence Gathering (can run in parallel):
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Domain 1    │  │ Domain 2    │  │ Domain 3    │
│ Check       │  │ Check       │  │ Check       │
└─────────────┘  └─────────────┘  └─────────────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
                  ┌─────▼─────┐
                  │ Aggregate │
                  │ Evidence  │
                  └───────────┘
```

