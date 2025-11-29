"""Configuration settings for the Disaster Relief Verification System."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
GOOGLE_SEARCH_API_KEY: Optional[str] = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CSE_ID: Optional[str] = os.getenv("GOOGLE_CSE_ID")  # Custom Search Engine ID

# Model Configuration
VISION_MODEL: str = "gpt-4-vision-preview"
LLM_MODEL: str = "gpt-4-turbo-preview"
GEMINI_MODEL: str = "gemini-2.0-flash-exp"  # Using Gemini 2.0 flash for best quality summaries

# Performance Settings
MAX_PROCESSING_TIME: int = 30  # seconds
IMAGE_PROCESSING_TIMEOUT: int = 5
BACKGROUND_CHECK_TIMEOUT: int = 20

# File System MCP Settings
CASE_FILES_DIR: Path = Path("case_files")
CASE_FILES_DIR.mkdir(exist_ok=True)

# Scam Database (can be extended with actual API endpoints)
SCAM_DATABASE_URL: Optional[str] = os.getenv("SCAM_DATABASE_URL")

# Official Registry APIs
GOVERNMENT_REGISTRY_URL: Optional[str] = os.getenv("GOVERNMENT_REGISTRY_URL")

# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

