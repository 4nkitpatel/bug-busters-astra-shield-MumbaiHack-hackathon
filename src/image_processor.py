"""Multimodal image processing for extracting information from help flyers."""
import re
import base64
from io import BytesIO
from typing import Dict, List, Optional, Tuple
from PIL import Image
import pytesseract
try:
    from pyzbar import pyzbar
except ImportError:
    pyzbar = None
    print("Warning: zbar shared library not found. QR code scanning will be disabled.")
import qrcode
from openai import OpenAI
import google.generativeai as genai

from src.config import OPENAI_API_KEY, VISION_MODEL, GEMINI_API_KEY, GEMINI_MODEL


class ImageProcessor:
    """Processes images to extract contact details, QR codes, and text."""
    
    def __init__(self):
        # OpenAI client (kept as fallback)
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

        # Gemini client for multimodal image analysis (preferred)
        if GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(GEMINI_MODEL)
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini model: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
    
    def process_image(self, image_path: str) -> Dict:
        """
        Main processing function that extracts all information from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing extracted information
        """
        image = Image.open(image_path)
        
        # Extract information using multiple methods
        qr_data = self._extract_qr_codes(image)
        ocr_text = self._extract_text_ocr(image)
        # Prefer Gemini for vision analysis; fall back to OpenAI if needed
        if self.gemini_model:
            vision_analysis = self._analyze_with_gemini(image)
        elif self.client:
            vision_analysis = self._analyze_with_vision(image)
        else:
            vision_analysis = {}
        
        # Combine all text sources: OCR + Gemini full_text + description
        gemini_full_text = vision_analysis.get('full_text', '') if isinstance(vision_analysis, dict) else ''
        gemini_description = vision_analysis.get('description', '') if isinstance(vision_analysis, dict) else ''
        
        # Prioritize Gemini's full_text (most accurate), then OCR, then description
        all_text = f"{gemini_full_text} {ocr_text} {gemini_description}".strip()
        
        # First, regex-based extraction from combined text
        extracted_info = self._extract_contact_details(all_text)

        # If Gemini returned structured entities, merge them in
        llm_entities = vision_analysis.get("entities") if isinstance(vision_analysis, dict) else None
        if isinstance(llm_entities, dict):
            extracted_info = self._merge_entities(extracted_info, llm_entities)
        
        # Extract bank details and locations from Gemini if available
        if isinstance(vision_analysis, dict):
            bank_details = vision_analysis.get('bank_details', {})
            if isinstance(bank_details, dict):
                # Extract UPI ID if present
                upi_id = bank_details.get('upi_id', '')
                if upi_id:
                    extracted_info.setdefault('emails', []).append(upi_id)  # UPI IDs are email-like
                
                # Extract account number as a special entity
                account_number = bank_details.get('account_number', '')
                if account_number:
                    extracted_info.setdefault('account_numbers', []).append(account_number)
            
            locations = vision_analysis.get('locations', [])
            if isinstance(locations, list):
                extracted_info['locations'] = locations
        
        # Merge QR code data - extract URLs/domains from QR codes
        if qr_data:
            for qr_item in qr_data:
                if qr_item:
                    # Check if QR code contains a URL
                    if qr_item.startswith('http://') or qr_item.startswith('https://'):
                        extracted_info['urls'].append(qr_item)
                        # Extract domain from URL
                        try:
                            from urllib.parse import urlparse
                            parsed = urlparse(qr_item)
                            if parsed.netloc:
                                extracted_info['domains'].append(parsed.netloc)
                        except:
                            pass
                    else:
                        # QR code might contain other data (UPI, phone, etc.)
                        # Try to extract phone/email patterns
                        if '@' in qr_item:
                            extracted_info['emails'].append(qr_item)
                        elif any(c.isdigit() for c in qr_item) and len(qr_item) >= 10:
                            # Might be a phone number or account number
                            extracted_info.setdefault('qr_data', []).append(qr_item)
            
            extracted_info['urls'] = list(set(extracted_info['urls']))
            extracted_info['domains'] = list(set(extracted_info['domains']))
        
        return {
            'raw_text': all_text,
            'qr_codes': qr_data,
            'extracted': extracted_info,
            'vision_analysis': vision_analysis
        }
    
    def _extract_qr_codes(self, image: Image.Image) -> List[str]:
        """Extract QR codes from image."""
        qr_data = []
        
        if pyzbar is None:
            return qr_data

        try:
            # Try pyzbar first
            decoded_objects = pyzbar.decode(image)
            for obj in decoded_objects:
                qr_data.append(obj.data.decode('utf-8'))
        except Exception as e:
            print(f"QR extraction error: {e}")
        
        return qr_data
    
    def _extract_text_ocr(self, image: Image.Image) -> str:
        """Extract text using OCR."""
        try:
            text = pytesseract.image_to_string(image)
            if not text or not text.strip():
                print("Warning: OCR returned empty text. Check if Tesseract is installed and image quality is good.")
            return text
        except Exception as e:
            error_msg = str(e)
            if "tesseract" in error_msg.lower() or "not found" in error_msg.lower():
                print(f"ERROR: Tesseract OCR not found. Please install: brew install tesseract")
            else:
                print(f"OCR error: {e}")
            return ""

    def _analyze_with_gemini(self, image: Image.Image) -> Dict:
        """
        Use Gemini (multimodal) to analyze the image and extract rich text.

        This is the preferred vision backend when GEMINI_API_KEY is set.
        """
        if not self.gemini_model:
            print("Warning: Gemini API key not set or model not initialized. Gemini vision analysis disabled.")
            return {}

        try:
            # Convert PIL image to bytes
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_bytes = buffered.getvalue()

            prompt = (
                "You are a forensic analyst examining a disaster relief or donation-related image.\n"
                "CRITICAL: Extract ALL visible text from the image, including:\n"
                "- Organization names (in any language: English, Hindi, regional languages)\n"
                "- Location information (cities, states, addresses)\n"
                "- Contact details (phone numbers, emails, UPI IDs, bank details)\n"
                "- QR code content (if visible or decoded)\n"
                "- Any text in Hindi, English, or other languages\n"
                "- Account numbers, IFSC codes, bank names\n"
                "- Any other relevant information\n\n"
                "Return a STRICT JSON object with this exact structure:\n"
                "{\n"
                "  \"full_text\": \"... ALL visible text from the image, preserving line breaks and structure. Include Hindi, English, and any other languages present ...\",\n"
                "  \"phone_numbers\": [\"+91-1234567890\", \"...\"],\n"
                "  \"emails\": [\"example@ngo.org\", \"...\"],\n"
                "  \"urls\": [\"https://example.org/donate\", \"...\"],\n"
                "  \"domains\": [\"example.org\", \"...\"],\n"
                "  \"organization_names\": [\"Full Organization Name\", \"...\"],\n"
                "  \"locations\": [\"City Name\", \"State Name\", \"...\"],\n"
                "  \"bank_details\": {\"bank_name\": \"...\", \"account_number\": \"...\", \"ifsc_code\": \"...\", \"upi_id\": \"...\"},\n"
                "  \"image_type\": \"help_flyer\" | \"donation_request\" | \"news_post\" | \"social_post\" | \"other\",\n"
                "  \"description\": \"Detailed description of what this image is about, including purpose, organization, and key information.\"\n"
                "}\n"
                "Rules:\n"
                "- Extract text in ALL languages present (Hindi, English, etc.)\n"
                "- Include organization names exactly as they appear (e.g., 'Shri Ram Janmabhoomi Teerth Kshetra', 'Red Cross Hoshiarpur')\n"
                "- Extract bank details, UPI IDs, account numbers if present\n"
                "- Extract location information (cities, states)\n"
                "- Respond with VALID JSON only, no markdown, no comments.\n"
                "- If a field is unknown, return an empty string \"\" or empty array [] or empty object {}.\n"
                "- Phone numbers should include country code if visible.\n"
            )

            response = self.gemini_model.generate_content(
                [
                    {"mime_type": "image/png", "data": img_bytes},
                    prompt,
                ]
            )

            raw_text = (response.text or "").strip()
            if not raw_text:
                print("Warning: Gemini returned empty response for image.")
                return {}

            import json
            try:
                data = json.loads(raw_text)
            except Exception as e:
                print(f"Gemini JSON parse error: {e}. Falling back to plain text description.")
                return {"description": raw_text}

            # Normalize fields
            description = (data.get("description") or data.get("full_text") or "").strip()
            entities = {
                "phone_numbers": data.get("phone_numbers") or [],
                "emails": data.get("emails") or [],
                "urls": data.get("urls") or [],
                "domains": data.get("domains") or [],
                "organization_names": data.get("organization_names") or [],
            }
            image_type = data.get("image_type") or "other"

            return {
                "description": description,
                "entities": entities,
                "image_type": image_type,
                "full_text": data.get("full_text", ""),
            }
        except Exception as e:
            print(f"Gemini vision analysis error: {e}")
            return {}
    
    def _analyze_with_vision(self, image: Image.Image) -> Dict:
        """Use GPT-4 Vision to analyze the image."""
        if not self.client:
            print("Warning: OpenAI API key not set. Vision analysis disabled.")
            return {}
        
        try:
            # Convert image to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            response = self.client.chat.completions.create(
                model=VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this disaster relief help flyer. Extract:
1. All contact information (phone, email, website)
2. Organization name
3. Purpose/type of help offered
4. Any suspicious indicators
5. Overall description of the flyer"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            description = response.choices[0].message.content
            return {"description": description}
        except Exception as e:
            error_msg = str(e)
            if "api" in error_msg.lower() and "key" in error_msg.lower():
                print(f"ERROR: Invalid or missing OpenAI API key. Please set OPENAI_API_KEY in .env file")
            else:
                print(f"Vision API error: {e}")
            return {}
    
    def _extract_contact_details(self, text: str) -> Dict:
        """Extract structured contact details from text using regex heuristics."""
        # Country-agnostic phone pattern: supports +CC, spaces, dashes, brackets
        phone_pattern = r'(?:\\+\\d{1,3}[\\s-]?)?(?:\\(\\d{1,4}\\)[\\s-]?)?\\d{3,4}[\\s-]?\\d{3,4}[\\s-]?\\d{0,4}'
        phones_raw = re.findall(phone_pattern, text)
        phones = []
        for p in phones_raw:
            normalized = re.sub(r'[^\\d+]', '', p)
            if len(normalized) >= 7:
                phones.append(normalized)

        # Email pattern
        email_pattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'
        emails = re.findall(email_pattern, text)

        # URL pattern (http/https)
        url_pattern = r'http[s]?://[^\\s]+'  # simple, robust URL pattern
        urls = re.findall(url_pattern, text)

        # Bare domain pattern (example.org, ngo.in, etc.)
        domain_pattern = r'\\b[a-zA-Z0-9.-]+\\.(?:com|org|net|edu|gov|ngo|in|io|co|us|uk|info|biz)\\b'
        bare_domains = re.findall(domain_pattern, text)

        # @handles (social handles)
        handle_pattern = r'@([A-Za-z0-9_]{3,50})'
        handles = [f"@{h}" for h in re.findall(handle_pattern, text)]

        # Extract domain names from URLs
        domains = list(bare_domains)
        for url in urls:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                if parsed.netloc:
                    domains.append(parsed.netloc)
            except Exception:
                pass

        return {
            'phone_numbers': list(set(phones)),
            'emails': list(set(emails)),
            'urls': list(set(urls)),
            'domains': list(set(domains)),
            'handles': list(set(handles)),
        }

    def _merge_entities(self, base: Dict, llm_entities: Dict) -> Dict:
        """Merge regex-based entities with LLM-extracted entities."""
        merged = dict(base)
        for key in ['phone_numbers', 'emails', 'urls', 'domains']:
            base_list = merged.get(key, []) or []
            llm_list = llm_entities.get(key, []) or []
            combined = list({item.strip() for item in base_list + llm_list if isinstance(item, str) and item.strip()})
            merged[key] = combined
        return merged

