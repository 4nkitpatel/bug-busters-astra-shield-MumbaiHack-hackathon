"""Forensic Analysis Agent - Main orchestrator for verification workflow."""
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from openai import OpenAI
import google.generativeai as genai

from src.config import OPENAI_API_KEY, LLM_MODEL, MAX_PROCESSING_TIME, GEMINI_API_KEY, GEMINI_MODEL
from src.image_processor import ImageProcessor
from src.mcp_tools import FileSystemMCP, SearchMCP


class ForensicAgent:
    """
    Main agent that orchestrates the forensic investigation workflow.
    Mimics a human investigator's process using MCP tools.
    """
    
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.filesystem_mcp = FileSystemMCP()
        self.search_mcp = SearchMCP()
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        
        # Initialize Gemini for summary generation
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel(GEMINI_MODEL)
        else:
            self.gemini_model = None
    
    async def investigate(self, image_path: str) -> Dict[str, Any]:
        """
        Main investigation method - performs complete forensic analysis.
        
        Args:
            image_path: Path to the help flyer image
            
        Returns:
            Complete investigation report
        """
        start_time = datetime.now()
        case_id = str(uuid.uuid4())[:8]
        
        try:
            # Step 1: Extract information from image
            print(f"[Case {case_id}] Step 1: Extracting information from image...")
            extracted_data = self.image_processor.process_image(image_path)
            
            # Step 2: Create case file
            print(f"[Case {case_id}] Step 2: Creating case file...")
            self.filesystem_mcp.create_case_file(case_id, {
                'image_path': image_path,
                'extracted_data': extracted_data
            })
            
            # Step 3: Perform background checks
            print(f"[Case {case_id}] Step 3: Performing background checks...")
            evidence = await self._gather_evidence(extracted_data)
            
            # Step 4: Analyze evidence and generate verdict
            print(f"[Case {case_id}] Step 4: Analyzing evidence...")
            analysis = await self._analyze_evidence(evidence, extracted_data)
            
            # Step 5: Finalize case
            print(f"[Case {case_id}] Step 5: Finalizing case...")
            final_report = self.filesystem_mcp.finalize_case(
                verdict=analysis['verdict'],
                risk_score=analysis['risk_score'],
                summary=analysis['summary'],
                recommendations=analysis['recommendations']
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            final_report['processing_time_seconds'] = processing_time
            
            # Ensure all necessary data is included in the return
            final_report['initial_data'] = {
                'image_path': image_path,
                'extracted_data': extracted_data
            }
            # Return evidence as a dictionary (not list) for easier access
            final_report['evidence'] = evidence
            final_report['risk_factors'] = analysis['risk_factors']
            final_report['risk_score'] = analysis['risk_score']
            final_report['verdict'] = analysis['verdict']
            final_report['summary'] = analysis['summary']
            final_report['recommendations'] = analysis['recommendations']
            
            return final_report
            
        except Exception as e:
            print(f"[Case {case_id}] Error during investigation: {e}")
            return {
                'case_id': case_id,
                'status': 'error',
                'error': str(e)
            }
        finally:
            await self.search_mcp.close()
    
    async def _gather_evidence(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather evidence using MCP tools - mimics investigator workflow.
        
        Args:
            extracted_data: Data extracted from image
            
        Returns:
            Collected evidence
        """
        evidence = {
            'domain_checks': [],
            'scam_checks': [],
            'registry_checks': [],
            'social_media_checks': []
        }
        
        extracted = extracted_data.get('extracted', {})
        
        # Check each domain
        for domain in extracted.get('domains', []):
            print(f"  Checking domain: {domain}")
            
            # Domain age check
            domain_info = await self.search_mcp.check_domain_age(domain)
            evidence['domain_checks'].append(domain_info)
            self.filesystem_mcp.log_evidence(
                'domain_age_check',
                domain_info,
                source='whois'
            )
            
            # Scam database check for domain
            scam_check = await self.search_mcp.check_scam_database(domain, 'domain')
            evidence['scam_checks'].append(scam_check)
            self.filesystem_mcp.log_evidence(
                'scam_database_check',
                scam_check,
                source='scam_database'
            )
        
        # Check phone numbers
        for phone in extracted.get('phone_numbers', []):
            print(f"  Checking phone: {phone}")
            scam_check = await self.search_mcp.check_scam_database(phone, 'phone')
            evidence['scam_checks'].append(scam_check)
            self.filesystem_mcp.log_evidence(
                'scam_database_check',
                scam_check,
                source='scam_database'
            )
        
        # Check emails
        for email in extracted.get('emails', []):
            print(f"  Checking email: {email}")
            scam_check = await self.search_mcp.check_scam_database(email, 'email')
            evidence['scam_checks'].append(scam_check)
            self.filesystem_mcp.log_evidence(
                'scam_database_check',
                scam_check,
                source='scam_database'
            )
        
        # Extract organization names and locations from Gemini's structured output (preferred)
        vision_analysis = extracted_data.get('vision_analysis', {})
        org_names = []
        locations = []
        
        # First, try to get organization names and locations from Gemini's structured output
        if isinstance(vision_analysis, dict):
            entities = vision_analysis.get('entities', {})
            if isinstance(entities, dict):
                gemini_orgs = entities.get('organization_names', [])
                if isinstance(gemini_orgs, list):
                    org_names.extend([org for org in gemini_orgs if org and isinstance(org, str) and len(org.strip()) > 2])
            
            # Extract locations from vision analysis
            vision_locations = vision_analysis.get('locations', [])
            if isinstance(vision_locations, list):
                locations.extend([loc for loc in vision_locations if loc and isinstance(loc, str)])
        
        # Also check extracted data for locations
        extracted = extracted_data.get('extracted', {})
        if isinstance(extracted, dict):
            extracted_locations = extracted.get('locations', [])
            if isinstance(extracted_locations, list):
                locations.extend([loc for loc in extracted_locations if loc and isinstance(loc, str)])
        
        # Fallback: extract from raw text if Gemini didn't find any
        if not org_names:
            raw_text = extracted_data.get('raw_text', '')
            org_name = self._extract_organization_name(raw_text)
            if org_name:
                org_names.append(org_name)
        
        # Check each organization name with location context
        for org_name in org_names:
            if org_name and org_name.strip():
                org_name = org_name.strip()
                location_str = ', '.join(locations[:2]) if locations else None  # Use first 2 locations
                print(f"  Checking organization: {org_name}" + (f" (Location: {location_str})" if location_str else ""))
                registry_check = await self.search_mcp.check_official_registry(
                    org_name, 
                    organization_type="ngo",  # Default, could be enhanced
                    location=location_str
                )
                evidence['registry_checks'].append(registry_check)
                self.filesystem_mcp.log_evidence(
                    'registry_check',
                    registry_check,
                    source='government_registry'
                )
        
        # Verify QR code URLs/domains if present
        qr_codes = extracted_data.get('qr_codes', [])
        if qr_codes:
            print(f"  Found {len(qr_codes)} QR code(s), verifying URLs/domains...")
            for qr_data in qr_codes:
                if qr_data and (qr_data.startswith('http://') or qr_data.startswith('https://')):
                    # Extract domain from QR URL
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(qr_data)
                        qr_domain = parsed.netloc
                        if qr_domain:
                            print(f"  Checking QR code domain: {qr_domain}")
                            # Check domain age
                            domain_info = await self.search_mcp.check_domain_age(qr_domain)
                            evidence['domain_checks'].append(domain_info)
                            # Check scam database
                            scam_check = await self.search_mcp.check_scam_database(qr_domain, 'domain')
                            evidence['scam_checks'].append(scam_check)
                    except Exception as e:
                        print(f"  Error processing QR code URL: {e}")
        
        return evidence
    
    async def _analyze_evidence(self, evidence: Dict[str, Any], 
                                extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze collected evidence to determine risk and verdict.
        
        Args:
            evidence: Collected evidence
            extracted_data: Original extracted data
            
        Returns:
            Analysis results with verdict and risk score
        """
        # Check if we actually extracted any data
        extracted = extracted_data.get('extracted', {}) or {}
        raw_text = (extracted_data.get('raw_text') or '').strip()
        vision_analysis = extracted_data.get('vision_analysis', {}) or {}
        image_type = vision_analysis.get('image_type', 'other')

        # Classify image type more generically if Gemini didn't set it
        if image_type == 'other':
            lowered = raw_text.lower()
            help_keywords = ['donate', 'donation', 'help needed', 'relief', 'fundraiser', 'qr code', 'upi', 'paytm', 'gpay', 'emergency', 'support us']
            if any(k in lowered for k in help_keywords):
                image_type = 'help_flyer'
            elif any(k in lowered for k in ['breaking', 'news', 'tweet', 'retweet', 'follow']):
                image_type = 'social_post'

        is_help_flyer = image_type == 'help_flyer'

        # If no contact data was extracted
        no_contacts = (
            not extracted.get('phone_numbers') and
            not extracted.get('emails') and
            not extracted.get('urls') and
            not extracted.get('domains')
        )

        no_data_extracted = (not raw_text or raw_text == " ") or no_contacts
        
        # Calculate risk score based on evidence
        risk_factors = []
        risk_score = 0
        
        # If no data extracted, add a softer, context-aware risk
        if no_data_extracted:
            if is_help_flyer:
                # Help flyer with no contact info is moderately suspicious
                risk_score += 20
                risk_factors.append("Unable to extract any clear contact information from what appears to be a help/donation flyer.")
            else:
                # For general posts/news, this is only a mild signal
                risk_score += 5
                risk_factors.append("No contact information detected. This may simply be an informational or social post.")
        
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
        
        # Check scam database matches
        for scam_check in evidence.get('scam_checks', []):
            if scam_check.get('risk_level') == 'high':
                risk_score += 40
                risk_factors.append(f"High risk match in scam database: {scam_check.get('identifier')}")
            elif scam_check.get('matches'):
                risk_score += 20
                risk_factors.append(f"Suspicious patterns found: {scam_check.get('identifier')}")
        
        # Check registry
        for registry_check in evidence.get('registry_checks', []):
            if not registry_check.get('registered', False):
                risk_score += 25
                risk_factors.append("Organization not found in official registry")
        
        # Cap risk score at 100
        risk_score = min(risk_score, 100)
        
        # Determine verdict
        if risk_score >= 70:
            verdict = "scam"
        elif risk_score >= 40:
            verdict = "suspicious"
        else:
            verdict = "safe"
        
        # Generate summary using LLM if available
        summary = self._generate_summary(evidence, risk_factors, verdict, extracted_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(verdict, risk_score, risk_factors)
        
        return {
            'verdict': verdict,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'summary': summary,
            'recommendations': recommendations
        }
    
    def _extract_organization_name(self, text: str) -> Optional[str]:
        """Extract organization name from text (simplified)."""
        # This is a simplified extraction - in production, use NLP models
        lines = text.split('\n')
        for line in lines[:5]:  # Check first few lines
            line = line.strip()
            if len(line) > 5 and len(line) < 50:
                # Likely organization name
                return line
        return None
    
    def _generate_summary(self, evidence: Dict[str, Any], 
                         risk_factors: List[str], verdict: str,
                         extracted_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate human-readable, well-formatted summary using Gemini."""
        # Try Gemini first for better formatting
        if self.gemini_model:
            try:
                # Build detailed evidence context
                domain_findings = []
                for dc in evidence.get('domain_checks', []):
                    if isinstance(dc, dict):
                        domain = dc.get('domain', '')
                        age_days = dc.get('age_days')
                        if age_days is not None:
                            domain_findings.append(f"Domain '{domain}' is {age_days} days old")
                
                scam_findings = []
                for sc in evidence.get('scam_checks', []):
                    if isinstance(sc, dict):
                        identifier = sc.get('identifier', '')
                        risk_level = sc.get('risk_level', 'unknown')
                        matches = sc.get('matches', [])
                        if risk_level == 'high' or (matches and len(matches) > 0):
                            scam_findings.append(f"'{identifier}' flagged with {len(matches)} scam report(s)")
                        else:
                            scam_findings.append(f"'{identifier}' - no scam reports found")
                
                registry_findings = []
                for rc in evidence.get('registry_checks', []):
                    if isinstance(rc, dict):
                        org = rc.get('organization', '')
                        registered = rc.get('registered', False)
                        if registered:
                            registry_findings.append(f"'{org}' verified in official registry")
                        else:
                            registry_findings.append(f"'{org}' not found in official registry")
                
                # Get organization names from extracted data
                org_names = []
                if extracted_data:
                    vision_analysis = extracted_data.get('vision_analysis', {})
                    if isinstance(vision_analysis, dict):
                        entities = vision_analysis.get('entities', {})
                        if isinstance(entities, dict):
                            org_names = entities.get('organization_names', [])
                
                evidence_summary = f"""
INVESTIGATION DATA:
- Domain checks performed: {len(evidence.get('domain_checks', []))}
- Scam database checks: {len(evidence.get('scam_checks', []))}
- Registry verification checks: {len(evidence.get('registry_checks', []))}

SPECIFIC FINDINGS:
{chr(10).join(f'• {f}' for f in domain_findings[:3]) if domain_findings else ''}
{chr(10).join(f'• {f}' for f in scam_findings[:3]) if scam_findings else ''}
{chr(10).join(f'• {f}' for f in registry_findings[:3]) if registry_findings else ''}

ORGANIZATIONS IDENTIFIED:
{', '.join(org_names[:3]) if org_names else 'None identified'}

RISK FACTORS:
{chr(10).join(f'• {factor}' for factor in risk_factors[:5]) if risk_factors else '• No specific risk factors identified'}

FINAL VERDICT: {verdict.upper()}
"""
                
                prompt = f"""You are a professional forensic analyst writing an executive summary for a disaster relief verification report.

Write a clear, well-formatted, human-friendly executive summary (2-3 short paragraphs) based on this investigation data:

{evidence_summary}

Requirements:
- Use clear, simple language that anyone can understand (even non-technical users)
- Format with proper paragraphs separated by line breaks
- Be concise but informative (150-250 words)
- Start with what the image is about (if organization names are provided, mention them)
- Explain what was checked and what was found
- End with the verdict and what it means for the user
- Use professional but accessible tone
- No bullet points, just flowing paragraphs
- Make it easy to read and understand
- If organizations are mentioned, reference them by name

Write only the summary text, no headers, labels, or markdown formatting."""

                response = self.gemini_model.generate_content(prompt)
                summary_text = response.text.strip()
                
                # Clean up any markdown formatting if present
                summary_text = summary_text.replace('**', '').replace('*', '').replace('#', '').replace('##', '')
                
                return summary_text
            except Exception as e:
                print(f"Error generating Gemini summary: {e}")
        
        # Fallback to OpenAI if Gemini not available
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
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a forensic analyst. Write a clear, well-formatted executive summary (2-3 paragraphs) in simple, human-friendly language. No bullet points, just flowing paragraphs."
                        },
                        {
                            "role": "user",
                            "content": f"Generate a concise, professional summary of this investigation:\n\n{evidence_summary}"
                        }
                    ],
                    max_tokens=250
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Error generating LLM summary: {e}")
        
        # Final fallback summary
        return f"""Our investigation has determined this resource to be {verdict.upper()}. 

We identified {len(risk_factors)} risk factor(s) during our analysis. The verification process included checking domain registration details, cross-referencing with scam databases, and verifying organization registrations.

Based on the evidence collected, we recommend exercising appropriate caution and verifying through additional independent sources before proceeding."""
    
    def _generate_recommendations(self, verdict: str, risk_score: float, 
                                 risk_factors: List[str]) -> List[str]:
        """Generate recommendations based on verdict."""
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
                "Check official disaster relief registries",
                "Ask for references or credentials",
                "Consider using established relief organizations instead"
            ])
        else:
            recommendations.extend([
                "Resource appears legitimate, but always verify independently",
                "Cross-check with official sources when possible",
                "Be cautious with personal information sharing"
            ])
        
        return recommendations

