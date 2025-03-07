import asyncio
import re
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, quote_plus

# Base URL for Pet Express website
BASE_URL = "https://www.petexpress.com.ph"

# Asynchronous HTTP client
async def get_async_client():
    return httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        }
    )

# Extract product data from HTML
def extract_product_data(html_content: str) -> List[Dict[str, Any]]:
    """Extract product information from the HTML content"""
    soup = BeautifulSoup(html_content, 'html5lib')
    products = []
    
    # Find all product cards on the page
    product_cards = soup.select('div.product-item')
    
    for card in product_cards:
        try:
            # Product URL and ID
            product_link = card.select_one('a.product-item__image-wrapper')
            if not product_link:
                continue
                
            product_url = urljoin(BASE_URL, product_link.get('href', ''))
            product_id = product_url.split('products/')[1] if 'products/' in product_url else None
            
            # Product title
            title_elem = card.select_one('a.product-item__title')
            title = title_elem.text.strip() if title_elem else 'Unknown Title'
            
            # Product image
            img_elem = card.select_one('img.product-item__primary-image')
            image_url = None
            if img_elem:
                image_url = 'https:' + img_elem.get('data-src', '') if img_elem.get('data-src', '').startswith('//') else img_elem.get('data-src', '')
            
            # Price
            price_elem = card.select_one('span.price')
            price = price_elem.text.strip() if price_elem else 'Price not available'
            
            # Check if on sale
            compare_price_elem = card.select_one('span.price--compare')
            on_sale = bool(compare_price_elem)
            compare_price = compare_price_elem.text.strip() if compare_price_elem else None
            
            # Stock status
            sold_out_elem = card.select_one('span.product-item__label--sold-out')
            in_stock = not bool(sold_out_elem)
            
            products.append({
                'product_id': product_id,
                'title': title,
                'url': product_url,
                'image_url': image_url,
                'price': price,
                'compare_price': compare_price,
                'on_sale': on_sale,
                'in_stock': in_stock
            })
        except Exception as e:
            print(f"Error processing product card: {e}")
            continue
    
    return products

# Function to extract detailed product information
def extract_product_details(html_content: str) -> Dict[str, Any]:
    """Extract detailed product information from a product page"""
    soup = BeautifulSoup(html_content, 'html5lib')
    product_details = {}
    
    try:
        # Basic info
        product_details['title'] = soup.select_one('h1.product-meta__title').text.strip() if soup.select_one('h1.product-meta__title') else 'Unknown Title'
        
        # Description
        description_elem = soup.select_one('div.product-meta__description-content')
        product_details['description'] = description_elem.text.strip() if description_elem else None
        
        # Prices
        price_elem = soup.select_one('span.product-meta__price')
        product_details['price'] = price_elem.text.strip() if price_elem else 'Price not available'
        
        compare_price_elem = soup.select_one('span.product-meta__price--compare')
        product_details['compare_price'] = compare_price_elem.text.strip() if compare_price_elem else None
        product_details['on_sale'] = bool(compare_price_elem)
        
        # Images
        images = []
        image_elems = soup.select('div.product-gallery__carousel-item img')
        for img in image_elems:
            img_url = img.get('data-zoom', img.get('src', ''))
            if img_url:
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                images.append(img_url)
        product_details['images'] = images
        
        # Stock status
        sold_out_elem = soup.select_one('span.product-form__inventory--sold-out')
        product_details['in_stock'] = not bool(sold_out_elem)
        
        # Product variants
        variants = []
        variant_elems = soup.select('div.block-swatch')
        for variant in variant_elems:
            variant_name = variant.select_one('div.block-swatch__item-text').text.strip() if variant.select_one('div.block-swatch__item-text') else None
            if variant_name:
                variants.append(variant_name)
        product_details['variants'] = variants
        
        # Product specifications
        specs = {}
        specs_table = soup.select('div.product-meta__table table tr')
        for row in specs_table:
            cells = row.select('td')
            if len(cells) == 2:
                key = cells[0].text.strip()
                value = cells[1].text.strip()
                specs[key] = value
        product_details['specifications'] = specs
    
    except Exception as e:
        print(f"Error extracting product details: {e}")
    
    return product_details

# Function to extract product categories
def extract_categories(html_content: str) -> List[Dict[str, Any]]:
    """Extract product categories from the main page"""
    soup = BeautifulSoup(html_content, 'html5lib')
    categories = []
    
    try:
        # Look for main navigation menu
        category_elems = soup.select('nav.header__navigation ul.nav-bar li.nav-bar__item--has-dropdown')
        
        for category in category_elems:
            main_category_elem = category.select_one('a.nav-bar__link')
            if not main_category_elem:
                continue
                
            main_category = main_category_elem.text.strip()
            main_category_url = urljoin(BASE_URL, main_category_elem.get('href', ''))
            
            # Get subcategories
            subcategories = []
            subcategory_elems = category.select('ul.nav-dropdown li.nav-dropdown__item a')
            
            for subcategory in subcategory_elems:
                subcategory_name = subcategory.text.strip()
                subcategory_url = urljoin(BASE_URL, subcategory.get('href', ''))
                
                subcategories.append({
                    'name': subcategory_name,
                    'url': subcategory_url
                })
            
            categories.append({
                'name': main_category,
                'url': main_category_url,
                'subcategories': subcategories
            })
    
    except Exception as e:
        print(f"Error extracting categories: {e}")
    
    return categories

# Main scraper functions
async def get_all_products(category: Optional[str] = None, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
    """Fetch products from Pet Express website"""
    async with await get_async_client() as client:
        # Determine URL based on category
        url = BASE_URL
        if category:
            url = f"{BASE_URL}/collections/{category}?page={page}"
        else:
            url = f"{BASE_URL}/collections/all?page={page}"
        
        response = await client.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch products: HTTP {response.status_code}")
        
        products = extract_product_data(response.text)
        
        # Apply pagination limit
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        return products[start_idx:min(end_idx, len(products))]

async def search_products(query: str, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search for products across the entire Pet Express catalog based on a query term
    
    Args:
        query: Search term
        page: Page number for pagination
        limit: Number of results per page
        
    Returns:
        List of products matching the search term
    """
    if not query:
        raise ValueError("Search query cannot be empty")
    
    # URL encode the search query
    encoded_query = quote_plus(query)
    search_url = f"{BASE_URL}/search?q={encoded_query}&type=product&options%5Bprefix%5D=last"
    
    async with await get_async_client() as client:
        response = await client.get(search_url)
        if response.status_code != 200:
            raise Exception(f"Failed to search products: HTTP {response.status_code}")
        
        products = extract_product_data(response.text)
        
        # Add search query and relevance to each product
        for product in products:
            product['search_query'] = query
            
            # Simple relevance scoring based on title match
            relevance_score = 0
            if product['title'] and query.lower() in product['title'].lower():
                # If query is in the title, give it a high score
                title_words = product['title'].lower().split()
                query_words = query.lower().split()
                
                # Check for exact title matches (highest relevance)
                if any(qw == tw for qw in query_words for tw in title_words):
                    relevance_score += 10
                
                # Check for partial matches
                for qw in query_words:
                    if any(qw in tw for tw in title_words):
                        relevance_score += 5
            
            product['relevance_score'] = relevance_score
        
        # Sort products by relevance score (descending)
        products.sort(key=lambda p: p.get('relevance_score', 0), reverse=True)
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_products = products[start_idx:min(end_idx, len(products))]
        
        return paginated_products

async def get_product_details(product_id: str) -> Dict[str, Any]:
    """Fetch detailed information about a specific product"""
    async with await get_async_client() as client:
        url = f"{BASE_URL}/products/{product_id}"
        
        response = await client.get(url)
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            raise Exception(f"Failed to fetch product details: HTTP {response.status_code}")
        
        return extract_product_details(response.text)

async def get_product_categories() -> List[Dict[str, Any]]:
    """Fetch all product categories"""
    async with await get_async_client() as client:
        response = await client.get(BASE_URL)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch categories: HTTP {response.status_code}")
        
        return extract_categories(response.text)
