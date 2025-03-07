# Pet Express Search API Specification

## Overview

The Pet Express Search API provides a simple and efficient way to search for pet products available on the Pet Express e-commerce website. This API enables users to query the entire Pet Express catalog with search terms and receive relevant product results. The enhanced recommendation endpoint uses intelligent agents to analyze product compatibility with specific dog breeds and age groups, scrape web reviews, and provide highly personalized product recommendations with suitability scores.

## Base URL

```
http://localhost:8000
```

## API Endpoints

### 1. Product Recommendations

Search for products, scrape web reviews, and generate personalized recommendations based on dog breed and age category. The recommendation system analyzes product compatibility with specific breeds and life stages, providing suitability scores and reasoning.

**Endpoint:** `/api/recommend`

**HTTP Method:** GET

**Query Parameters:**

| Parameter | Type   | Required | Default | Description                                       |
|-----------|--------|----------|---------|---------------------------------------------------|
| query     | string | Yes      | -       | Search term to find products (e.g., "dog food")   |
| dog_breed | string | Yes      | -       | Dog breed for recommendations (e.g., "Labrador") |
| age       | string | Yes      | -       | Age category of the dog ("puppy" or "adult")     |
| page      | integer| No       | 1       | Page number for pagination (min: 1)              |
| limit     | integer| No       | 10      | Number of results per page (min: 1, max: 20)     |
| max_recommendations | integer| No | 5   | Maximum number of recommendations (min: 1, max: 10) |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/recommend?query=dog%20food&dog_breed=Labrador&age=puppy&page=1&limit=10" -H "accept: application/json"
```

**Response Format:**

```json
{
  "success": true,
  "query": "dog food",
  "dog_breed": "Labrador",
  "age": "puppy",
  "count": 3,
  "recommendations": [
    {
      "product_id": "royal-canin-labrador-puppy-dry-dog-food",
      "title": "Royal Canin Labrador Puppy Dry Dog Food",
      "url": "https://www.petexpress.com.ph/products/royal-canin-labrador-puppy-dry-dog-food",
      "price": "Sale priceP 2,500.00",
      "image_url": "https://www.petexpress.com.ph/cdn/shop/files/royal-canin-labrador-puppy-food.png",
      "reviews": [
        "This product is specially formulated for Labrador puppies and helps maintain their growth and development. Highly recommended by vets.",
        "My Labrador puppy loves this food. It's made specifically for the breed's needs and helps with joint development which is important for Labs."
      ],
      "recommendation_reason": "Highly recommended for Labrador puppies. Product specifically mentions compatibility.",
      "suitability_score": 9.5
    },
    // ... more recommendations
  ],
  "summary": "Based on your search for 'dog food' for your Labrador puppy, we highly recommend Royal Canin Labrador Puppy Dry Dog Food (Suitability Score: 9.5/10). It's specially formulated for the nutritional needs of growing Labrador puppies and helps support healthy joint development, which is particularly important for this breed. We've also found 2 other products that might be suitable for your Labrador puppy."
}
```

**Response Fields:**

| Field           | Type    | Description                                         |
|-----------------|---------|-----------------------------------------------------|
| success         | boolean | Indicates if the request was successful             |
| query           | string  | The search term used for the query                  |
| dog_breed       | string  | The dog breed used for recommendations              |
| age             | string  | The dog age category used for recommendations       |
| count           | integer | Number of recommendations returned                  |
| recommendations | array   | Array of recommendation objects                     |
| summary         | string  | AI-generated summary of the recommendations         |

**Recommendation Object Fields:**

| Field                 | Type    | Description                                     |
|-----------------------|---------|-------------------------------------------------|
| product_id            | string  | Unique identifier for the product               |
| title                 | string  | Name of the product                             |
| url                   | string  | Full URL to the product page                    |
| price                 | string  | Current price of the product                    |
| image_url             | string  | URL to the product image                        |
| reviews               | array   | Web-scraped reviews for the product             |
| recommendation_reason | string  | Reason for recommending this product            |
| suitability_score     | number  | Score 0-10 indicating match for breed and age   |

### 2. Search Products

Search for products across the entire Pet Express catalog based on a search term.

**Endpoint:** `/api/search`

**HTTP Method:** GET

**Query Parameters:**

| Parameter | Type   | Required | Default | Description                                      |
|-----------|--------|----------|---------|--------------------------------------------------|
| query     | string | Yes      | -       | Search term to find products (e.g., "dog treats") |
| page      | integer| No       | 1       | Page number for pagination (min: 1)              |
| limit     | integer| No       | 20      | Number of results per page (min: 1, max: 100)    |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/search?query=dog%20treats&page=1&limit=10" -H "accept: application/json"
```

**Response Format:**

```json
{
  "success": true,
  "query": "dog treats",
  "count": 10,
  "page": 1,
  "limit": 10,
  "data": [
    {
      "product_id": "jerhigh-meat-stick-dog-treats-70g?_pos=1&_sid=76be924ad&_ss=r",
      "title": "JerHigh Meat Stick Dog Treats 70g",
      "url": "https://www.petexpress.com.ph/products/jerhigh-meat-stick-dog-treats-70g?_pos=1&_sid=76be924ad&_ss=r",
      "image_url": "https://www.petexpress.com.ph/cdn/shop/files/10321399JerHighMeatStickDogTreats70gA_{width}x.png?v=1731303418",
      "price": "Sale priceP 100.00",
      "compare_price": null,
      "on_sale": false,
      "in_stock": true,
      "search_query": "dog treats",
      "relevance_score": 20
    },
    // ... more products
  ]
}
```

**Response Fields:**

| Field           | Type    | Description                                           |
|-----------------|---------|-------------------------------------------------------|
| success         | boolean | Indicates if the request was successful               |
| query           | string  | The search term used for the query                    |
| count           | integer | Number of products returned in this response          |
| page            | integer | Current page number                                   |
| limit           | integer | Maximum number of results per page                    |
| data            | array   | Array of product objects                              |

**Product Object Fields:**

| Field           | Type    | Description                                           |
|-----------------|---------|-------------------------------------------------------|
| product_id      | string  | Unique identifier for the product                     |
| title           | string  | Name of the product                                   |
| url             | string  | Full URL to the product page                          |
| image_url       | string  | URL to the product image (contains {width} placeholder)|
| price           | string  | Current price of the product                          |
| compare_price   | string  | Original price if on sale, null otherwise             |
| on_sale         | boolean | Indicates if the product is on sale                   |
| in_stock        | boolean | Indicates if the product is in stock                  |
| search_query    | string  | The search term used to find this product             |
| relevance_score | integer | Relevance score of the product to the search query    |

### 3. Get Product Details

Fetch detailed information about a specific product.

**Endpoint:** `/api/product/{product_id}`

**HTTP Method:** GET

**Path Parameters:**

| Parameter   | Type   | Required | Description                          |
|-------------|--------|----------|--------------------------------------|
| product_id  | string | Yes      | ID of the product to retrieve details|

### 4. Get Products

Fetch products, optionally filtered by category.

**Endpoint:** `/api/products`

**HTTP Method:** GET

**Query Parameters:**

| Parameter | Type    | Required | Default | Description                                 |
|-----------|---------|----------|---------|---------------------------------------------|
| category  | string  | No       | null    | Category to filter products                 |
| page      | integer | No       | 1       | Page number for pagination (min: 1)         |
| limit     | integer | No       | 20      | Number of results per page (min: 1, max: 100)|

### 5. Get Categories

Fetch all product categories.

**Endpoint:** `/api/categories`

**HTTP Method:** GET

## Error Handling

The API returns appropriate HTTP status codes and error messages in the following format:

```json
{
  "detail": "Error message"
}
```

**Common Error Codes:**

| Status Code | Description                                      |
|-------------|--------------------------------------------------|
| 400         | Bad Request - Invalid parameters                 |
| 404         | Not Found - Resource not found                   |
| 500         | Internal Server Error - Server-side issue        |

## Implementation Details

### Enhanced Recommendation System

The `/api/recommend` endpoint implements a sophisticated recommendation system designed to provide personalized product suggestions based on a dog's breed and age. Here's how it works:

1. **Product Search**: The system first searches the Pet Express website for products matching the query (e.g., "dog food").

2. **Web Review Scraping**: For each matching product, the system uses the Tavily API to search the web for reviews and information specifically related to the product and the specified dog breed and age.

3. **Breed-Specific Analysis**: The recommendation agent analyzes the scraped reviews using a sophisticated scoring system that looks for:
   - Direct mentions of the specific dog breed
   - Breed-related terms and synonyms (e.g., "brachycephalic" for bulldogs)
   - Age-appropriate terminology (e.g., "puppy", "junior", "adult", "senior")
   - Breed-specific nutritional needs (e.g., joint health for large breeds)

4. **Suitability Scoring**: Each product receives a suitability score from 0-10, reflecting how well it matches the specific breed and age requirements:
   - 8-10: Highly recommended, with specific mentions of compatibility for the breed and age
   - 6-7: Good match based on multiple positive reviews
   - 4-5: May be suitable but limited specific information available
   - 0-3: Limited evidence of suitability for the specific breed and age

5. **Recommendation Summary**: The system generates a concise summary of the recommendations, highlighting the most suitable product and explaining why it was selected.

### Web Scraping for Reviews

The recommendation endpoint uses the Tavily API to search the web for product reviews and relevant information about specific products for particular dog breeds and ages. This information is then analyzed to determine the suitability of each product.

### Recommendation Engine

The API implements a recommendation engine using pydantic-ai agents that:

1. Searches for products on Pet Express based on the query term
2. Scrapes the web for reviews and information about each product
3. Analyzes the product information and reviews to determine suitability for the specified dog breed and age
4. Generates personalized recommendations with suitability scores
5. Provides a human-readable summary of the recommendations

### Suitability Scoring

Products are scored on a scale of 0-10 based on their compatibility with the specified dog breed and age:

- Products specifically mentioning the breed and age receive highest scores (8-10)
- Products with positive reviews for the breed or age receive medium scores (6-8)
- Products with limited specific information receive lower scores (4-6)
- Products with indications of unsuitability receive very low scores (0-4)

### Relevance Scoring

The search functionality implements relevance scoring to prioritize the most relevant results:
- Products with the exact search term in the title receive a high score (10 points)
- Products with partial matches of the search term in the title receive a medium score (5 points)
- Results are sorted by relevance score in descending order

### Pagination

All endpoints that return multiple items support pagination through the `page` and `limit` parameters.

## Technical Requirements

### Dependencies

- Python 3.8+ with the following packages:
  - fastapi
  - uvicorn
  - requests
  - beautifulsoup4
  - html5lib
  - httpx
  - python-dotenv
  - pydantic-ai
  - tavily-python

### Installation

Using uv (recommended):
```bash
uv add fastapi uvicorn requests beautifulsoup4 html5lib httpx python-dotenv pydantic-ai tavily-python
```

### Running the API

Using uv:
```bash
cd pet_express_scraper
uv run main.py
```

Alternatively, you can also use uvicorn directly:
```bash
cd pet_express_scraper
uv pip install uvicorn
uv run -m uvicorn main:app --reload
```

## Limitations

- The API is subject to rate limiting and availability of the Pet Express website
- Image URLs contain a `{width}` placeholder that needs to be replaced with an actual width value
- Search results are limited to what's available on the Pet Express website search functionality
- The recommendation system requires a Tavily API key for web searches, without which it falls back to mock reviews
- Web scraping for product reviews may not always find breed-specific information for all products

## Future Enhancements

- Add filtering capabilities (by price range, brand, etc.)
- Implement more sophisticated relevance scoring
- Add caching to improve performance
- Add more detailed product information
- Expand recommendation system to support other pet types (cats, birds, etc.)
- Implement user feedback loops to improve recommendation quality over time
- Add support for more granular age categories (senior, young adult, etc.)
- Incorporate additional data sources for more comprehensive product recommendations
