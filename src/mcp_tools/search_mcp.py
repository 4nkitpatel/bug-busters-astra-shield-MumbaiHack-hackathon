"""Search MCP Tool for external verification and background checks."""
import httpx
import whois
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

try:
    from googleapiclient.discovery import build
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False
    print("Warning: google-api-python-client not installed. Google Search will be disabled.")

from src.config import SCAM_DATABASE_URL, GOVERNMENT_REGISTRY_URL, GOOGLE_SEARCH_API_KEY, GOOGLE_CSE_ID, GEMINI_API_KEY, GEMINI_MODEL

# Import Gemini for intelligent search query generation
try:
    import google.generativeai as genai
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
    else:
        GEMINI_AVAILABLE = False
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None


class SearchMCP:
    """MCP tool for performing external searches and background checks."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        # Initialize Google Search API if available
        self.google_search_service = None
        if GOOGLE_SEARCH_AVAILABLE and GOOGLE_SEARCH_API_KEY and GOOGLE_CSE_ID:
            try:
                self.google_search_service = build("customsearch", "v1", developerKey=GOOGLE_SEARCH_API_KEY)
                self.cse_id = GOOGLE_CSE_ID
            except Exception as e:
                print(f"Warning: Failed to initialize Google Search API: {e}")
                self.google_search_service = None
        
        # Initialize Gemini for intelligent search queries
        self.gemini_model = None
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                self.gemini_model = genai.GenerativeModel(GEMINI_MODEL)
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini for search: {e}")
                self.gemini_model = None
    
    async def check_domain_age(self, domain: str) -> Dict[str, Any]:
        """
        Check domain age and registration details.
        
        Args:
            domain: Domain name to check
            
        Returns:
            Dictionary with domain information
        """
        try:
            # Clean domain (remove www, http, etc.)
            domain = self._clean_domain(domain)
            
            # WHOIS lookup
            w = whois.whois(domain)
            
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            expiration_date = w.expiration_date
            if isinstance(expiration_date, list):
                expiration_date = expiration_date[0]
            
            # Calculate domain age
            age_days = None
            if creation_date:
                age_days = (datetime.now() - creation_date).days
            
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
        except Exception as e:
            return {
                'domain': domain,
                'error': str(e),
                'status': 'error'
            }
    
    async def check_scam_database(self, identifier: str, identifier_type: str = "domain") -> Dict[str, Any]:
        """
        Check against scam database using Google Search.
        
        Args:
            identifier: Domain, email, or phone to check
            identifier_type: Type of identifier (domain/email/phone)
            
        Returns:
            Scam database check results
        """
        results = {
            'identifier': identifier,
            'type': identifier_type,
            'checked_at': datetime.now().isoformat(),
            'matches': [],
            'risk_level': 'unknown',
            'search_results': []
        }
        
        # Basic pattern check
        suspicious_patterns = ['scam', 'fraud', 'fake', 'phishing']
        identifier_lower = identifier.lower()
        for pattern in suspicious_patterns:
            if pattern in identifier_lower:
                results['matches'].append({
                    'pattern': pattern,
                    'reason': 'Suspicious keyword detected'
                })
                results['risk_level'] = 'high'
        
        # Use Google Search to check for scam reports
        if self.google_search_service:
            try:
                # Search for scam reports about this identifier
                search_query = f'"{identifier}" scam OR fraud OR complaint'
                search_results = await self._perform_google_search(search_query, max_results=5)
                
                if search_results:
                    results['search_results'] = search_results
                    # Analyze results for scam indicators
                    scam_indicators = ['scam', 'fraud', 'complaint', 'warning', 'fake', 'phishing']
                    for result in search_results:
                        title_snippet = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
                        for indicator in scam_indicators:
                            if indicator in title_snippet:
                                results['matches'].append({
                                    'pattern': indicator,
                                    'reason': f'Found in search results: {result.get("title", "")}',
                                    'source_url': result.get('link')
                                })
                                if results['risk_level'] == 'unknown':
                                    results['risk_level'] = 'medium'
                                elif results['risk_level'] == 'medium':
                                    results['risk_level'] = 'high'
                                break
            except Exception as e:
                results['search_error'] = str(e)
        
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
        
        return results
    
    async def check_official_registry(self, organization_name: str, 
                                     organization_type: str = "ngo",
                                     location: Optional[str] = None) -> Dict[str, Any]:
        """
        Check official government/NGO registry and search for recent updates/news.
        
        Args:
            organization_name: Name of the organization
            organization_type: Type (ngo, charity, business)
            location: Optional location (city, state) for better search results
            
        Returns:
            Registry check results with recent updates
        """
        results = {
            'organization': organization_name,
            'type': organization_type,
            'checked_at': datetime.now().isoformat(),
            'registered': False,
            'registration_details': None,
            'search_results': [],
            'recent_updates': [],
            'verification_status': 'unknown'
        }
        
        # Use Gemini to generate intelligent search queries
        search_queries = []
        if self.gemini_model:
            try:
                query_prompt = f"""Generate 3-4 specific Google search queries to verify and find recent information about this organization:

Organization: {organization_name}
Type: {organization_type}
Location: {location if location else 'Not specified'}

Generate search queries that will help:
1. Verify official registration/registry status
2. Find recent news/updates about the organization
3. Check legitimacy and verify authenticity
4. Find official website or contact information

Return ONLY a JSON array of search query strings, like:
["query 1", "query 2", "query 3"]

Example queries for "Red Cross Hoshiarpur":
["Red Cross Hoshiarpur official registration", "Red Cross Hoshiarpur district society verified", "Red Cross Hoshiarpur recent news 2024", "District Red Cross Society Hoshiarpur official"]

Return only the JSON array, no other text."""
                
                response = self.gemini_model.generate_content(query_prompt)
                import json
                try:
                    queries_json = json.loads(response.text.strip())
                    if isinstance(queries_json, list):
                        search_queries = queries_json
                except:
                    pass
            except Exception as e:
                print(f"Error generating Gemini search queries: {e}")
        
        # Fallback to basic queries if Gemini didn't generate any
        if not search_queries:
            base_query = f'"{organization_name}"'
            if location:
                base_query += f' {location}'
            search_queries = [
                f'{base_query} {organization_type} registry OR registration OR official',
                f'{base_query} verified OR legitimate OR official',
                f'{base_query} recent news OR updates 2024',
                f'{base_query} official website OR contact'
            ]
        
        # Perform searches using Google Search API
        all_search_results = []
        if self.google_search_service:
            try:
                for query in search_queries[:4]:  # Limit to 4 queries
                    search_results = await self._perform_google_search(query, max_results=5)
                    all_search_results.extend(search_results)
                
                if all_search_results:
                    results['search_results'] = all_search_results[:10]  # Limit total results
                    
                    # Check if any results point to official registries
                    official_domains = ['gov', 'org', 'nic.in', 'charitycommission', 'companieshouse', 'redcross', 'redcross.org']
                    for result in all_search_results:
                        link = result.get('link', '').lower()
                        title_snippet = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
                        
                        # Check for official registry
                        if any(domain in link for domain in official_domains):
                            if not results['registered']:
                                results['registered'] = True
                                results['registration_details'] = {
                                    'source': result.get('title', ''),
                                    'url': result.get('link', ''),
                                    'snippet': result.get('snippet', '')
                                }
                                results['verification_status'] = 'verified'
                        
                        # Check for recent updates/news
                        if any(keyword in title_snippet for keyword in ['news', 'update', 'recent', '2024', '2023', 'announcement']):
                            results['recent_updates'].append({
                                'title': result.get('title', ''),
                                'url': result.get('link', ''),
                                'snippet': result.get('snippet', ''),
                                'date': datetime.now().isoformat()  # Could parse actual date from snippet
                            })
                    
                    # If found on reputable platforms, mark as verified
                    reputable_keywords = ['verified', 'official', 'registered', 'legitimate', 'authentic']
                    if any(keyword in ' '.join([r.get('snippet', '') for r in all_search_results[:5]]).lower() 
                           for keyword in reputable_keywords):
                        if not results['registered']:
                            results['verification_status'] = 'likely_legitimate'
            except Exception as e:
                results['search_error'] = str(e)
        
        # If we have a registry URL, make actual API call
        if GOVERNMENT_REGISTRY_URL:
            try:
                response = await self.client.get(
                    f"{GOVERNMENT_REGISTRY_URL}/search",
                    params={
                        'name': organization_name,
                        'type': organization_type
                    }
                )
                if response.status_code == 200:
                    registry_data = response.json()
                    results.update(registry_data)
            except Exception as e:
                results['api_error'] = str(e)
        
        return results
    
    async def check_social_media_presence(self, identifier: str) -> Dict[str, Any]:
        """
        Check social media presence and authenticity.
        
        Args:
            identifier: Organization name or domain
            
        Returns:
            Social media presence data
        """
        # This would check Twitter, Facebook, LinkedIn, etc.
        # For now, return placeholder structure
        return {
            'identifier': identifier,
            'checked_at': datetime.now().isoformat(),
            'platforms': {},
            'authenticity_score': None
        }
    
    async def perform_web_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform web search using Google Custom Search API.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results with title, link, and snippet
        """
        return await self._perform_google_search(query, max_results)
    
    async def _perform_google_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Internal method to perform Google Search.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        if not self.google_search_service:
            # Fallback: return empty or placeholder
            return []
        
        try:
            # Google Custom Search API call (synchronous, but we're in async context)
            # Run in executor to avoid blocking
            import asyncio
            loop = asyncio.get_event_loop()
            
            def _sync_search():
                return self.google_search_service.cse().list(
                    q=query,
                    cx=self.cse_id,
                    num=min(max_results, 10)  # Google allows max 10 results per request
                ).execute()
            
            result = await loop.run_in_executor(None, _sync_search)
            
            search_results = []
            items = result.get('items', [])
            
            for item in items[:max_results]:
                search_results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'displayLink': item.get('displayLink', '')
                })
            
            return search_results
            
        except Exception as e:
            print(f"Error performing Google Search: {e}")
            return []
    
    def _clean_domain(self, domain: str) -> str:
        """Clean and extract domain from URL or domain string."""
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
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

