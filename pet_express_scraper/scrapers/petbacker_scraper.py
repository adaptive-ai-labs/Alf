import aiohttp
import asyncio
import re
import json
import urllib.parse
from bs4 import BeautifulSoup
import logging
import time
from typing import List, Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PetbackerScraper:
    """
    Scraper for petbacker.ph to extract groomer information
    """
    
    BASE_URL = "https://www.petbacker.ph"
    GROOMING_URL = f"{BASE_URL}/s/dog-grooming/manila--metro-manila--philippines"
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from a URL using standard HTTP request"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.error(f"Failed to fetch {url}: Status code {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
            
    async def fetch_api_data(self, url: str, params: Dict[str, Any] = None, headers: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Fetch JSON data from PetBacker API endpoints"""
        try:
            default_headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Referer": "https://www.petbacker.ph/"
            }
            
            if headers:
                default_headers.update(headers)
            
            logger.info(f"Fetching API data from {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=default_headers) as response:
                    if response.status == 200:
                        try:
                            data = await response.json()
                            return data
                        except json.JSONDecodeError:
                            text = await response.text()
                            logger.error(f"Failed to parse JSON from API response: {text[:200]}...")
                            return None
                    else:
                        logger.error(f"Failed to fetch API data: Status code {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching API data from {url}: {e}")
            return None
    
    async def search_groomers(self, location: str = "manila--metro-manila--philippines", breed: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for pet groomers in the specified location
        
        Args:
            location: Location formatted as slug (e.g., "manila--metro-manila--philippines")
            breed: Optional dog breed to filter results (used for scoring, not filtering API results)
            
        Returns:
            List of groomer information dictionaries
        """
        # Format the URL correctly
        if not location:
            location = "manila--metro-manila--philippines"
        else:
            # Format location for URL - example: manila--metro-manila--philippines
            location = location.lower().replace(' ', '-')
            if "philippines" not in location:
                location = f"{location}--philippines"
        
        url = f"{self.BASE_URL}/s/dog-grooming/{location}"
        logger.info(f"Searching for groomers at {url}")
        
        # Extract location parameters for API call
        location_parts = location.split('--')
        city = location_parts[0] if len(location_parts) > 0 else 'manila'
        state = location_parts[1] if len(location_parts) > 1 else 'metro-manila'
        country = location_parts[2] if len(location_parts) > 2 else 'philippines'
        
        # PetBacker's API endpoint for searching groomers
        api_url = f"{self.BASE_URL}/api/v1/search/groomers"
        
        # Parameters for the API call
        params = {
            "city": city,
            "state": state,
            "country": country,
            "service": "grooming",
            "page": 1,
            "limit": 10
        }
        
        # Attempt to fetch data from the API
        logger.info(f"Attempting to fetch groomer listings from API with params: {params}")
        api_data = await self.fetch_api_data(api_url, params=params)
        
        if api_data and 'groomers' in api_data and isinstance(api_data['groomers'], list):
            logger.info(f"Successfully fetched {len(api_data['groomers'])} groomers from API")
            return self._parse_api_groomer_data(api_data['groomers'], breed)
            
        # If API request fails, fall back to HTML parsing
        logger.warning("API request failed, falling back to regular HTTP request")
        html_content = await self.fetch_page(url)
        if not html_content:
            logger.error("Failed to retrieve groomer listings")
            return []
        
        # Parse the groomer cards
        return self._parse_groomer_listings(html_content, breed)
    
    def _parse_api_groomer_data(self, groomers_data: List[Dict[str, Any]], breed: Optional[str] = None) -> List[Dict[str, Any]]:
        """Parse the groomer data from API response"""
        groomers = []
        
        for groomer in groomers_data[:5]:  # Limit to first 5 groomers for efficiency
            try:
                # Extract data from API response
                groomer_id = groomer.get('id', '')
                name = groomer.get('name', 'Unknown Groomer')
                groomer_url = f"{self.BASE_URL}/profile/{groomer_id}" if groomer_id else ""
                location = groomer.get('location', {}).get('formatted_address', 'Manila, Philippines')
                rating = float(groomer.get('rating', 0.0))
                reviews_count = int(groomer.get('reviews_count', 0))
                price_info = groomer.get('price_info', 'Price not available')
                img_url = groomer.get('profile_image', '')
                
                # Add breed compatibility score if breed is provided
                compatibility = 0
                if breed:
                    services = groomer.get('services', [])
                    specialties = groomer.get('specialties', [])
                    bio = groomer.get('bio', '')
                    
                    breed_lower = breed.lower()
                    compatibility = 7  # Default score
                    
                    # Check if breed is mentioned in specialties or bio
                    if any(breed_lower in specialty.lower() for specialty in specialties):
                        compatibility = 10
                    elif breed_lower in bio.lower():
                        compatibility = 9
                
                # Assemble the groomer data
                groomer_data = {
                    "id": groomer_id,
                    "name": name,
                    "url": groomer_url,
                    "location": location,
                    "rating": rating,
                    "reviews_count": reviews_count,
                    "price_info": price_info,
                    "image_url": img_url,
                    "breed_compatibility": compatibility
                }
                
                groomers.append(groomer_data)
                
            except Exception as e:
                logger.error(f"Error parsing groomer data: {e}")
        
        return groomers
    
    def _parse_groomer_listings(self, html_content: str, breed: Optional[str] = None) -> List[Dict[str, Any]]:
        """Parse the HTML content to extract groomer information"""
        soup = BeautifulSoup(html_content, 'html.parser')
        groomers = []
        
        # Find all groomer cards on the page
        groomer_cards = soup.select('.sitter-card')
        # Also check for listing-item which is used in the new layout
        if not groomer_cards:
            groomer_cards = soup.select('a.listing-item')
            
        logger.info(f"Found {len(groomer_cards)} groomer cards")
        
        for card in groomer_cards[:5]:  # Limit to first 5 groomers for efficiency
            try:
                # Extract basic info
                # Check different URL extraction methods based on the page layout
                if card.name == 'a' and 'href' in card.attrs:
                    # Direct link in new layout
                    groomer_url = self.BASE_URL + card['href']
                else:
                    # Traditional layout
                    groomer_url_element = card.select_one('a.profileimage-bg')
                    groomer_url = self.BASE_URL + groomer_url_element['href'] if groomer_url_element else ""
                
                name_element = card.select_one('.sitter-name')
                name = name_element.text.strip() if name_element else "Unknown Groomer"
                
                location_element = card.select_one('.list-group-item:has(.fa-map-marker)')
                location = location_element.text.strip().replace("\n", " ").replace("  ", " ") if location_element else "Manila, Philippines"
                
                rating_element = card.select_one('.rate-number')
                rating = float(rating_element.text.strip()) if rating_element else 0.0
                
                # Extract review count
                reviews_element = card.select_one('.rate-reviews')
                reviews_count = 0
                if reviews_element:
                    reviews_match = re.search(r'(\d+)', reviews_element.text)
                    if reviews_match:
                        reviews_count = int(reviews_match.group(1))
                
                # Extract price info
                price_element = card.select_one('.price-label')
                price_info = price_element.text.strip() if price_element else "Price not available"
                
                # Extract profile image
                img_element = card.select_one('img.sitter-img')
                img_url = img_element['src'] if img_element and 'src' in img_element.attrs else ""
                
                # Create a unique ID
                # Extract groomer ID from URL - pattern varies based on URL format
                if '/profile/' in groomer_url:
                    groomer_id = groomer_url.split('/')[-1]
                elif '/philippines/grooming/' in groomer_url or '/pet-sitter/' in groomer_url:
                    # For URLs like /philippines/grooming/metro-manila/taguig/furbabg-gromming-home-groomer
                    # or /pet-sitter/breed-specialist/location
                    groomer_id = groomer_url.split('/')[-1]
                else:
                    groomer_id = f"groomer-{len(groomers)}"
                
                # Add breed compatibility score if breed is provided
                compatibility = 0
                if breed:
                    # Later we'll extract the groomer's profile to check for breed mentions
                    compatibility = 7  # Default medium-high score, will be refined later
                
                # Assemble the groomer data
                groomer_data = {
                    "id": groomer_id,
                    "name": name,
                    "url": groomer_url,
                    "location": location,
                    "rating": rating,
                    "reviews_count": reviews_count,
                    "price_info": price_info,
                    "image_url": img_url,
                    "breed_compatibility": compatibility
                }
                
                groomers.append(groomer_data)
                
            except Exception as e:
                logger.error(f"Error parsing groomer card: {e}")
        
        return groomers
    
    async def get_groomer_details(self, groomer_url: str, breed: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch detailed information about a groomer from their profile page
        
        Args:
            groomer_url: URL to the groomer's profile
            breed: Optional dog breed to check compatibility
            
        Returns:
            Dictionary with detailed groomer information
        """
        logger.info(f"Fetching groomer details from {groomer_url}")
        
        # Try to extract profile ID for API request
        profile_id = None
        if '/profile/' in groomer_url:
            profile_id = groomer_url.split('/profile/')[-1]
        elif '/philippines/grooming/' in groomer_url:
            # For URLs like /philippines/grooming/metro-manila/taguig/furbabg-gromming-home-groomer
            parts = groomer_url.split('/')
            if len(parts) >= 6:
                profile_id = parts[-1]  # Use the slug as ID
        
        if profile_id:
            # PetBacker's API endpoint for groomer profile
            api_url = f"{self.BASE_URL}/api/v1/profile/{profile_id}"
            
            # Attempt to fetch data from the API
            logger.info(f"Attempting to fetch groomer profile from API for ID: {profile_id}")
            api_data = await self.fetch_api_data(api_url)
            
            if api_data and 'profile' in api_data:
                logger.info(f"Successfully fetched groomer profile from API")
                return self._parse_api_groomer_profile(api_data['profile'], breed)
        
        # If API request fails, fall back to HTML parsing
        logger.warning("API request failed or profile ID not found, falling back to regular HTTP request")
        html_content = await self.fetch_page(groomer_url)
        if not html_content:
            logger.error(f"Failed to retrieve groomer profile from {groomer_url}")
            return {}
        
        # Parse the groomer profile
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract services
        services = []
        service_elements = soup.select('.service-card')
        for service in service_elements:
            service_name = service.select_one('.service-name')
            if service_name:
                services.append(service_name.text.strip())
        
        # Extract reviews
        reviews = []
        review_elements = soup.select('.review-item')
        for review in review_elements[:3]:  # Limit to first 3 reviews
            review_text = review.select_one('.review-text')
            if review_text:
                reviews.append(review_text.text.strip())
        
        # Extract about section
        about_section = soup.select_one('.about-me')
        about_text = about_section.text.strip() if about_section else ""
        
        # Calculate breed compatibility
        compatibility_score = 7.0  # Default score
        if breed:
            breed_lower = breed.lower()
            # Check if breed is mentioned in about text or reviews
            if about_text and breed_lower in about_text.lower():
                compatibility_score = 9.0
            elif any(breed_lower in review.lower() for review in reviews):
                compatibility_score = 8.5
            
            # Check if they mention experience with all breeds
            all_breeds_terms = ["all breeds", "any breed", "all dogs", "any dog"]
            if any(term in about_text.lower() for term in all_breeds_terms):
                compatibility_score = max(compatibility_score, 8.0)
        
        # Extract contact info if available
        contact_info = "Contact via petbacker.ph"
        contact_element = soup.select_one('.contact-info')
        if contact_element:
            contact_info = contact_element.text.strip()
        
        return {
            "services": services,
            "reviews": reviews,
            "about": about_text,
            "breed_compatibility": compatibility_score,
            "contact_info": contact_info
        }
    
    def _check_breed_category_match(self, breed: str, text: str) -> bool:
        """Check if breed category matches text (e.g., 'large dog' matches 'German Shepherd')"""
        breed_lower = breed.lower()
        text_lower = text.lower()
        
        # Map breeds to categories
        large_breeds = ["german shepherd", "rottweiler", "great dane", "doberman", "mastiff", "saint bernard"]
        medium_breeds = ["golden retriever", "labrador", "boxer", "collie", "husky", "bulldog"]
        small_breeds = ["chihuahua", "pomeranian", "shih tzu", "yorkshire terrier", "maltese", "poodle"]
        
        # Check for category terms in text
        category_terms = {
            "large": ["large breed", "large dog", "big dog"],
            "medium": ["medium breed", "medium dog", "medium-sized"],
            "small": ["small breed", "small dog", "toy breed", "miniature"]
        }
        
        # Determine breed category
        if any(b in breed_lower for b in large_breeds):
            breed_category = "large"
        elif any(b in breed_lower for b in medium_breeds):
            breed_category = "medium"
        elif any(b in breed_lower for b in small_breeds):
            breed_category = "small"
        else:
            # If we can't determine the category, return False
            return False
        
        # Check if any term for this breed's category appears in the text
        return any(term in text_lower for term in category_terms[breed_category])
    
    def _parse_api_groomer_profile(self, profile_data: Dict[str, Any], breed: Optional[str] = None) -> Dict[str, Any]:
        """Parse the groomer profile data from API response"""
        try:
            # Extract basic profile info
            groomer_id = profile_data.get('id', '')
            name = profile_data.get('name', 'Unknown Groomer')
            bio = profile_data.get('bio', '')
            location = profile_data.get('location', {}).get('formatted_address', 'Manila, Philippines')
            rating = float(profile_data.get('rating', 0.0))
            reviews_count = int(profile_data.get('reviews_count', 0))
            
            # Extract services
            services = []
            for service in profile_data.get('services', []):
                service_name = service.get('name', '')
                if service_name:
                    services.append(service_name)
            
            # Extract reviews
            reviews = []
            for review in profile_data.get('reviews', [])[:3]:  # Limit to first 3 reviews
                review_text = review.get('content', '')
                if review_text:
                    reviews.append(review_text)
            
            # Calculate breed compatibility score
            compatibility_score = 7.0  # Default score
            if breed:
                breed_lower = breed.lower()
                specialties = profile_data.get('specialties', [])
                
                # Check if breed is mentioned in specialties or bio
                if any(breed_lower in specialty.lower() for specialty in specialties):
                    compatibility_score = 10.0
                elif breed_lower in bio.lower():
                    compatibility_score = 9.0
                # Check for indirect breed references (e.g., large dogs, small dogs)
                elif self._check_breed_category_match(breed, bio) or \
                     any(self._check_breed_category_match(breed, specialty) for specialty in specialties):
                    compatibility_score = 8.0
            
            # Compile the profile data
            profile = {
                "id": groomer_id,
                "name": name,
                "location": location,
                "bio": bio,
                "services": services,
                "rating": rating,
                "reviews_count": reviews_count,
                "reviews": reviews,
                "breed_compatibility": compatibility_score,
                "contact_info": "Contact via petbacker.ph"
            }
            
            return profile
            
        except Exception as e:
            logger.error(f"Error parsing groomer profile API data: {e}")
            return {}

# Function to search for groomers based on dog breed and location
async def search_petbacker_groomers(dog_breed: str, location: str = "Philippines", max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search for groomers on petbacker.ph and get detailed information
    
    Args:
        dog_breed: Dog breed to search for
        location: Location to search in (will be formatted appropriately)
        max_results: Maximum number of groomer results to return
        
    Returns:
        List of groomer information with details
    """
    # Format location for the URL
    if location.lower() == "philippines":
        formatted_location = "manila--metro-manila--philippines"
    else:
        # Format other locations properly
        formatted_location = location.lower().replace(' ', '-')
        if "philippines" not in formatted_location:
            formatted_location = f"{formatted_location}--philippines"
    
    scraper = PetbackerScraper()
    
    # Get list of groomers
    groomers = await scraper.search_groomers(formatted_location, dog_breed)
    
    # Sort by rating and compatibility
    sorted_groomers = sorted(
        groomers, 
        key=lambda x: (x.get("breed_compatibility", 0), x.get("rating", 0)), 
        reverse=True
    )
    
    # Limit results
    top_groomers = sorted_groomers[:max_results]
    
    # Get detailed info for each groomer
    detailed_groomers = []
    for groomer in top_groomers:
        if groomer.get("url"):
            details = await scraper.get_groomer_details(groomer["url"], dog_breed)
            # Merge basic info with details
            groomer.update(details)
        detailed_groomers.append(groomer)
    
    return detailed_groomers
