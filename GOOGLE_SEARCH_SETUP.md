# Google Search API Integration Setup

## Overview

The system now uses Google Custom Search API for real web searches to:
- Check for scam reports about domains, emails, and phone numbers
- Find official registry entries for organizations
- Perform general web searches for additional context

## Setup Instructions

### Step 1: Get Google Search API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Custom Search API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Custom Search API"
   - Click "Enable"

4. Create API Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy your API key

### Step 2: Create Custom Search Engine

1. Go to [Google Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click "Add" to create a new search engine
3. Configure:
   - **Sites to search**: Leave empty or add specific sites (e.g., `*.gov`, `*.org`)
   - **Name**: Give it a name (e.g., "Disaster Relief Verifier")
   - Click "Create"

4. Get your Search Engine ID:
   - After creation, go to "Setup" > "Basics"
   - Copy the **Search engine ID** (looks like: `012345678901234567890:abcdefghijk`)

### Step 3: Configure in .env

Add these to your `.env` file:

```env
# Google Custom Search API
GOOGLE_SEARCH_API_KEY=your_api_key_here
GOOGLE_CSE_ID=your_search_engine_id_here
```

### Step 4: Install Dependencies

```bash
cd /Users/upmanyujha/Documents/mumbai_hacks_BB
source venv/bin/activate
pip install google-api-python-client>=2.100.0
```

## Features Enabled

### 1. Scam Database Checks
- Searches for scam reports about domains, emails, and phone numbers
- Analyzes search results for scam indicators
- Provides risk assessment based on found reports

### 2. Official Registry Verification
- Searches for official government/NGO registry entries
- Identifies official domains (.gov, .org, etc.)
- Verifies organization registration status

### 3. General Web Search
- Available for future enhancements
- Can be used for additional context gathering

## Usage

Once configured, the system will automatically:
- Use Google Search when checking for scams
- Search for official registry entries
- Provide real search results in evidence logs

## Cost Information

- **Free Tier**: 100 search queries per day
- **Paid**: $5 per 1,000 queries after free tier
- Monitor usage in [Google Cloud Console](https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas)

## Troubleshooting

### "Warning: google-api-python-client not installed"
```bash
pip install google-api-python-client>=2.100.0
```

### "Failed to initialize Google Search API"
- Check that `GOOGLE_SEARCH_API_KEY` is set correctly
- Verify `GOOGLE_CSE_ID` is correct
- Ensure Custom Search API is enabled in Google Cloud Console

### "Error performing Google Search"
- Check API key permissions
- Verify Search Engine ID is correct
- Check quota limits in Google Cloud Console

## Example Configuration

```env
GOOGLE_SEARCH_API_KEY=AIzaSyBrkrB-wcIOMV-rS1m2SQVgDjO--T6nfMA
GOOGLE_CSE_ID=012345678901234567890:abcdefghijk
```

## Benefits

✅ **Real Search Results**: Actual web search results instead of placeholders
✅ **Better Scam Detection**: Finds real scam reports from the web
✅ **Registry Verification**: Finds official registration records
✅ **More Accurate Risk Assessment**: Based on real data from the internet

