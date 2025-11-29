"""FastAPI server for the Disaster Relief Verification System."""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import tempfile
import os
from pathlib import Path

from src.forensic_agent import ForensicAgent

app = FastAPI(
    title="Disaster Relief Verification System",
    description="Multimodal AI agent for verifying disaster relief help flyers",
    version="1.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = ForensicAgent()


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


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/verify")
async def verify_flyer(file: UploadFile = File(...)):
    """
    Main verification endpoint.
    
    Upload an image of a help flyer to get a forensic analysis.
    
    Returns:
        Complete investigation report with verdict and evidence in AstraShield-compatible format
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
        try:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
            
            # Perform investigation
            result = await agent.investigate(tmp_file_path)
            
            # Ensure result is a dictionary
            if not isinstance(result, dict):
                raise HTTPException(
                    status_code=500,
                    detail=f"Invalid result format from investigation: {type(result)}"
                )
            
            # Transform result to AstraShield-compatible format
            try:
                transformed_result = transform_to_astrashield_format(result)
            except Exception as e:
                # Log the error for debugging
                import traceback
                print(f"Error transforming result: {e}")
                print(f"Result type: {type(result)}")
                print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
                print(f"Traceback: {traceback.format_exc()}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Error transforming result: {str(e)}"
                )
            
            return JSONResponse(content=transformed_result)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error during investigation: {str(e)}"
            )
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)


def transform_to_astrashield_format(result: dict) -> dict:
    """
    Transform our investigation result to match AstraShield's VerificationResult format.
    """
    verdict_map = {
        'safe': 'SAFE',
        'suspicious': 'SUSPICIOUS',
        'scam': 'SCAM'
    }
    
    # Extract entities from the result - check multiple possible locations
    entities = []
    extracted = {}
    
    # Try to get extracted data from different possible locations with type checking
    if 'initial_data' in result:
        initial_data = result.get('initial_data', {})
        # Check if initial_data is a dict
        if isinstance(initial_data, dict):
            extracted_data = initial_data.get('extracted_data', {})
            if isinstance(extracted_data, dict):
                extracted = extracted_data.get('extracted', {})
            else:
                extracted = {}
        else:
            extracted = {}
    elif 'extracted_data' in result:
        extracted_data = result.get('extracted_data', {})
        if isinstance(extracted_data, dict):
            extracted = extracted_data.get('extracted', {})
        else:
            extracted = {}
    
    # Ensure extracted is a dictionary
    if not isinstance(extracted, dict):
        extracted = {}
    
    # If still empty, try to get from evidence or other fields
    if not extracted:
        # Try to extract from raw text if available
        raw_text = result.get('raw_text', '')
        if isinstance(raw_text, str) and raw_text:
            # Basic extraction from raw text
            import re
            # Extract phone numbers
            phones = re.findall(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', raw_text)
            # Extract emails
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', raw_text)
            # Extract URLs
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', raw_text)
            extracted = {
                'phone_numbers': phones if phones else [],
                'emails': emails if emails else [],
                'urls': urls if urls else [],
                'domains': []
            }
    
    # Ensure extracted is still a dict before proceeding
    if not isinstance(extracted, dict):
        extracted = {}
    
    # Add phone numbers
    phone_numbers = extracted.get('phone_numbers', []) if isinstance(extracted.get('phone_numbers'), list) else []
    for phone in phone_numbers:
        if phone and phone.strip():
            entities.append({
                'type': 'PHONE',
                'value': phone.strip(),
                'verificationStatus': 'Extracted from image',
                'isFlagged': False
            })
    
    # Add emails
    emails = extracted.get('emails', []) if isinstance(extracted.get('emails'), list) else []
    for email in emails:
        if email and isinstance(email, str) and email.strip():
            entities.append({
                'type': 'EMAIL',
                'value': email.strip(),
                'verificationStatus': 'Extracted from image',
                'isFlagged': False
            })
    
    # Add URLs
    urls = extracted.get('urls', []) if isinstance(extracted.get('urls'), list) else []
    for url in urls:
        if url and isinstance(url, str) and url.strip():
            entities.append({
                'type': 'URL',
                'value': url.strip(),
                'verificationStatus': 'Extracted from image',
                'isFlagged': False
            })
    
    # Add domains
    domains = extracted.get('domains', []) if isinstance(extracted.get('domains'), list) else []
    for domain in domains:
        if domain and domain.strip():
            entities.append({
                'type': 'URL',
                'value': domain.strip(),
                'verificationStatus': 'Extracted from image',
                'isFlagged': False
            })
    
    # Add organization names from Gemini's structured output
    initial_data = result.get('initial_data', {})
    if isinstance(initial_data, dict):
        extracted_data = initial_data.get('extracted_data', {})
        if isinstance(extracted_data, dict):
            vision_analysis = extracted_data.get('vision_analysis', {})
            if isinstance(vision_analysis, dict):
                vision_entities = vision_analysis.get('entities', {})
                if isinstance(vision_entities, dict):
                    org_names = vision_entities.get('organization_names', [])
                    if isinstance(org_names, list):
                        for org_name in org_names:
                            if org_name and isinstance(org_name, str) and org_name.strip():
                                entities.append({
                                    'type': 'ORGANIZATION',
                                    'value': org_name.strip(),
                                    'verificationStatus': 'Extracted from image',
                                    'isFlagged': False
                                })
    
    # Build evidence map for entity verification
    evidence_map = {
        'domains': {},
        'phones': {},
        'emails': {},
        'organizations': {}
    }
    
    # Process evidence to build verification descriptions
    evidence_dict = result.get('evidence', {})
    if not isinstance(evidence_dict, dict):
        evidence_dict = {}
    
    # Process domain checks
    for domain_check in evidence_dict.get('domain_checks', []):
        if isinstance(domain_check, dict):
            domain = domain_check.get('domain', '')
            if domain:
                age_days = domain_check.get('age_days')
                if age_days is not None:
                    if age_days < 30:
                        evidence_map['domains'][domain] = f"Domain is very new ({age_days} days old), which may indicate a recently created site."
                    elif age_days < 365:
                        evidence_map['domains'][domain] = f"Domain is relatively new ({age_days} days old)."
                    else:
                        evidence_map['domains'][domain] = f"Domain has been registered for {age_days} days, indicating established presence."
                else:
                    evidence_map['domains'][domain] = "Domain registration details verified."
    
    # Process scam checks
    for scam_check in evidence_dict.get('scam_checks', []):
        if isinstance(scam_check, dict):
            identifier = scam_check.get('identifier', '')
            identifier_type = scam_check.get('type', '')
            risk_level = scam_check.get('risk_level', 'unknown')
            matches = scam_check.get('matches', [])
            
            if identifier:
                if identifier_type == 'domain':
                    if risk_level == 'high' or (matches and len(matches) > 0):
                        evidence_map['domains'][identifier] = f"Flagged in scam database with {len(matches)} match(es). High risk indicators detected."
                    else:
                        evidence_map['domains'][identifier] = "No scam reports found in our database."
                elif identifier_type == 'phone':
                    if risk_level == 'high' or (matches and len(matches) > 0):
                        evidence_map['phones'][identifier] = f"Phone number flagged in scam database with {len(matches)} match(es)."
                    else:
                        evidence_map['phones'][identifier] = "No scam reports found for this phone number."
                elif identifier_type == 'email':
                    if risk_level == 'high' or (matches and len(matches) > 0):
                        evidence_map['emails'][identifier] = f"Email address flagged in scam database with {len(matches)} match(es)."
                    else:
                        evidence_map['emails'][identifier] = "No scam reports found for this email address."
    
    # Process registry checks
    for registry_check in evidence_dict.get('registry_checks', []):
        if isinstance(registry_check, dict):
            org_name = registry_check.get('organization', '')
            registered = registry_check.get('registered', False)
            registration_details = registry_check.get('registration_details', {})
            search_results = registry_check.get('search_results', [])
            
            verification_status = registry_check.get('verification_status', 'unknown')
            recent_updates = registry_check.get('recent_updates', [])
            
            if org_name:
                if registered:
                    source = registration_details.get('source', 'official registry')
                    evidence_map['organizations'][org_name] = f"Verified as registered in {source}. Official registration confirmed."
                elif verification_status == 'likely_legitimate':
                    evidence_map['organizations'][org_name] = f"Appears in verified sources and reputable platforms, indicating likely legitimacy."
                elif search_results and len(search_results) > 0:
                    # Check if found on reputable platforms
                    reputable_platforms = ['housing.com', 'proptiger', '99acres', 'magicbricks', 'real estate', 'property', 'redcross', 'redcross.org', 'ngo', 'charity']
                    found_reputable = any(any(platform in (r.get('title', '') + r.get('snippet', '')).lower() for platform in reputable_platforms) for r in search_results if isinstance(r, dict))
                    if found_reputable:
                        evidence_map['organizations'][org_name] = f"Listed on multiple reputable platforms. No official registry entry found, but appears in legitimate listings."
                    else:
                        evidence_map['organizations'][org_name] = f"Found in search results but not verified in official registry. Exercise caution."
                else:
                    evidence_map['organizations'][org_name] = "Not found in official registry or reputable platforms. Verification incomplete."
                
                # Add recent updates info to description if available
                if recent_updates and len(recent_updates) > 0:
                    current_desc = evidence_map['organizations'].get(org_name, '')
                    update_count = len(recent_updates)
                    evidence_map['organizations'][org_name] = f"{current_desc} Recent updates/news found ({update_count} source(s))."
    
    # Update entity verification statuses based on evidence
    for entity in entities:
        entity_value = entity['value'].lower()
        entity_type = entity['type']
        
        # Match entity to evidence
        if entity_type == 'URL' or entity_type == 'DOMAIN':
            for domain, desc in evidence_map['domains'].items():
                if domain.lower() in entity_value or entity_value in domain.lower():
                    entity['verificationStatus'] = desc
                    if 'scam' in desc.lower() or 'flagged' in desc.lower() or 'high risk' in desc.lower():
                        entity['isFlagged'] = True
                    break
        elif entity_type == 'PHONE':
            for phone, desc in evidence_map['phones'].items():
                # Normalize phone numbers for comparison
                phone_clean = ''.join(filter(str.isdigit, phone))
                entity_clean = ''.join(filter(str.isdigit, entity_value))
                if phone_clean in entity_clean or entity_clean in phone_clean:
                    entity['verificationStatus'] = desc
                    if 'scam' in desc.lower() or 'flagged' in desc.lower():
                        entity['isFlagged'] = True
                    break
        elif entity_type == 'EMAIL':
            for email, desc in evidence_map['emails'].items():
                if email.lower() == entity_value:
                    entity['verificationStatus'] = desc
                    if 'scam' in desc.lower() or 'flagged' in desc.lower():
                        entity['isFlagged'] = True
                    break
        elif entity_type == 'ORGANIZATION':
            for org, desc in evidence_map['organizations'].items():
                if org.lower() in entity_value or entity_value in org.lower():
                    entity['verificationStatus'] = desc
                    if 'not found' in desc.lower() and 'verified' not in desc.lower():
                        entity['isFlagged'] = True
                    break
    
    # Transform risk factors into detailed evidence points
    risk_factors = result.get('risk_factors', [])
    if not isinstance(risk_factors, list):
        risk_factors = [risk_factors] if risk_factors else []
    
    # Build detailed evidence points from evidence and risk factors
    evidence_points = []
    evidence_dict = result.get('evidence', {})
    if not isinstance(evidence_dict, dict):
        evidence_dict = {}
    
    # Add evidence from domain checks
    for domain_check in evidence_dict.get('domain_checks', []):
        if isinstance(domain_check, dict):
            domain = domain_check.get('domain', '')
            age_days = domain_check.get('age_days')
            if age_days is not None and age_days < 365:
                evidence_points.append(f"Domain '{domain}' is relatively new ({age_days} days old), which may indicate a recently created site.")
    
    # Add evidence from scam checks
    for scam_check in evidence_dict.get('scam_checks', []):
        if isinstance(scam_check, dict):
            identifier = scam_check.get('identifier', '')
            matches = scam_check.get('matches', [])
            search_results = scam_check.get('search_results', [])
            
            if matches and len(matches) > 0:
                match_reasons = [m.get('reason', '') for m in matches if isinstance(m, dict)]
                if match_reasons:
                    evidence_points.append(f"'{identifier}' flagged in scam database: {', '.join(match_reasons[:2])}")
            elif search_results and len(search_results) > 0:
                # Check if search results indicate legitimacy
                positive_indicators = ['verified', 'legitimate', 'official', 'registered']
                negative_indicators = ['scam', 'fraud', 'complaint', 'warning']
                titles_snippets = ' '.join([r.get('title', '') + ' ' + r.get('snippet', '') for r in search_results if isinstance(r, dict)]).lower()
                if any(indicator in titles_snippets for indicator in negative_indicators):
                    evidence_points.append(f"Search results for '{identifier}' contain negative indicators.")
                elif any(indicator in titles_snippets for indicator in positive_indicators):
                    evidence_points.append(f"'{identifier}' appears in legitimate sources and verified platforms.")
    
    # Add evidence from registry checks
    for registry_check in evidence_dict.get('registry_checks', []):
        if isinstance(registry_check, dict):
            org_name = registry_check.get('organization', '')
            registered = registry_check.get('registered', False)
            registration_details = registry_check.get('registration_details', {})
            search_results = registry_check.get('search_results', [])
            recent_updates = registry_check.get('recent_updates', [])
            verification_status = registry_check.get('verification_status', 'unknown')
            
            if org_name:
                if registered:
                    source = registration_details.get('source', 'official registry')
                    url = registration_details.get('url', '')
                    evidence_points.append(f"'{org_name}' is verified as registered in {source}.")
                    if url:
                        evidence_points.append(f"Official registration details available at verified sources.")
                elif verification_status == 'likely_legitimate':
                    evidence_points.append(f"'{org_name}' appears in verified sources and reputable platforms, indicating likely legitimacy.")
                elif search_results and len(search_results) > 0:
                    # Check for reputable platforms
                    platform_names = []
                    for result in search_results[:5]:
                        if isinstance(result, dict):
                            link = result.get('link', '').lower()
                            title = result.get('title', '')
                            if 'housing.com' in link or 'proptiger' in link or '99acres' in link or 'redcross' in link:
                                platform_names.append(title.split('-')[0].strip() if '-' in title else title[:30])
                    
                    if platform_names:
                        evidence_points.append(f"'{org_name}' is consistently listed across multiple reputable platforms ({', '.join(set(platform_names[:3]))}) with matching details.")
                    else:
                        evidence_points.append(f"'{org_name}' found in search results but not verified in official registry.")
                
                # Add recent updates/news if available
                if recent_updates and len(recent_updates) > 0:
                    update_titles = [u.get('title', '')[:50] for u in recent_updates[:2] if isinstance(u, dict)]
                    if update_titles:
                        evidence_points.append(f"Recent updates/news found about '{org_name}': {', '.join(update_titles)}")
    
    # Add risk factors as evidence points if not already covered
    for risk_factor in risk_factors:
        if isinstance(risk_factor, str) and risk_factor not in evidence_points:
            # Make risk factors more descriptive
            if 'Unable to extract' in risk_factor:
                evidence_points.append("⚠️ WARNING: Unable to extract any clear contact information from the image. This significantly increases risk.")
            elif 'Domain is very new' in risk_factor:
                evidence_points.append(f"⚠️ {risk_factor}")
            elif 'scam database' in risk_factor.lower():
                evidence_points.append(f"🚨 {risk_factor}")
            elif 'not found in official registry' in risk_factor.lower():
                evidence_points.append(f"⚠️ {risk_factor}")
            else:
                evidence_points.append(risk_factor)
    
    # If no evidence points, add a generic one
    if not evidence_points:
        evidence_points.append("Analysis completed. No specific risk indicators identified.")
    
    # Get recommendations - ensure it's a list and format properly
    recommendations = result.get('recommendations', [])
    if not isinstance(recommendations, list):
        recommendations = [recommendations] if recommendations else []
    
    # Format recommendation as a single string
    if recommendations:
        recommendation = '. '.join(recommendations[:3])  # Take first 3 recommendations
        if not recommendation.endswith('.'):
            recommendation += '.'
    else:
        recommendation = 'Proceed with caution and verify through independent sources.'
    
    # Extract sources from evidence and search results
    sources = []
    sources_seen = set()  # To avoid duplicates
    
    # Extract from evidence dictionary
    for domain_check in evidence_dict.get('domain_checks', []):
        if isinstance(domain_check, dict):
            # WHOIS doesn't provide URLs, skip
            pass
    
    for scam_check in evidence_dict.get('scam_checks', []):
        if isinstance(scam_check, dict):
            search_results = scam_check.get('search_results', [])
            if isinstance(search_results, list):
                for result in search_results[:5]:
                    if isinstance(result, dict) and result.get('link'):
                        link = result.get('link', '')
                        if link not in sources_seen:
                            sources_seen.add(link)
                            sources.append({
                                'title': result.get('title', 'Search Result')[:50],
                                'uri': link
                            })
    
    for registry_check in evidence_dict.get('registry_checks', []):
        if isinstance(registry_check, dict):
            registration_details = registry_check.get('registration_details', {})
            if isinstance(registration_details, dict) and registration_details.get('url'):
                url = registration_details.get('url', '')
                if url not in sources_seen:
                    sources_seen.add(url)
                    sources.append({
                        'title': registration_details.get('source', 'Official Registry')[:50],
                        'uri': url
                    })
            
            search_results = registry_check.get('search_results', [])
            if isinstance(search_results, list):
                for result in search_results[:5]:
                    if isinstance(result, dict) and result.get('link'):
                        link = result.get('link', '')
                        if link not in sources_seen:
                            sources_seen.add(link)
                            sources.append({
                                'title': result.get('title', 'Search Result')[:50],
                                'uri': link
                            })
            
            # Add recent updates as sources
            recent_updates = registry_check.get('recent_updates', [])
            if isinstance(recent_updates, list):
                for update in recent_updates[:3]:
                    if isinstance(update, dict) and update.get('url'):
                        url = update.get('url', '')
                        if url not in sources_seen:
                            sources_seen.add(url)
                            sources.append({
                                'title': update.get('title', 'Recent Update')[:50],
                                'uri': url
                            })
    
    return {
        'riskScore': result.get('risk_score', 0),
        'verdict': verdict_map.get(result.get('verdict', 'suspicious').lower(), 'SUSPICIOUS'),
        'summary': result.get('summary', 'No summary available.'),
        'entities': entities,
        'evidencePoints': evidence_points,
        'recommendation': recommendation,
        'sources': sources
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

