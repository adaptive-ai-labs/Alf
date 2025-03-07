from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Literal
import os

from scrapers.pet_express_scraper import (
    get_all_products,
    get_product_details,
    get_product_categories,
    search_products
)
from agents.recommendation_agent import get_product_recommendations

router = APIRouter()

@router.get("/search")
async def search(
    query: str = Query(..., description="Search term to find products"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Number of results per page")
):
    """
    Search for products across the entire Pet Express catalog based on a query term.
    This endpoint scrapes the entire Pet Express website and returns products matching the search term.
    
    Required query parameters:
    - query: Search term to find products (e.g., "treats", "dog food", "cat toys")
    
    Optional query parameters:
    - page: Page number for pagination (default: 1)
    - limit: Number of products per page (default: 20, max: 100)
    """
    try:
        products = await search_products(query, page, limit)
        return {
            "success": True,
            "query": query,
            "count": len(products),
            "page": page,
            "limit": limit,
            "data": products
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend")
async def recommend(
    query: str = Query(..., description="Search term to find products"),
    dog_breed: str = Query(..., description="Dog breed for recommendations"),
    age: Literal["puppy", "adult"] = Query(..., description="Age category of the dog (puppy or adult)"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(10, ge=1, le=20, description="Number of products per page"),
    max_recommendations: int = Query(5, ge=1, le=10, description="Maximum number of recommendations to generate"),
    include_groomers: bool = Query(True, description="Include groomer recommendations from petbacker.ph")
):
    """
    Search for products across the Pet Express catalog and generate personalized recommendations
    based on dog breed and age. This endpoint uses AI agents to scrape web reviews and analyze product
    suitability for the specified dog breed and age.
    
    Required query parameters:
    - query: Search term to find products (e.g., "dog food", "treats")
    - dog_breed: Dog breed for recommendations (e.g., "Labrador", "Golden Retriever")
    - age: Age category of the dog ("puppy" or "adult")
    
    Optional query parameters:
    - page: Page number for pagination (default: 1)
    - limit: Number of products per page (default: 10, max: 20)
    - max_recommendations: Maximum number of recommendations to generate (default: 5, max: 10)
    """
    try:
        # First, search for products on Pet Express
        products = await search_products(query, page, limit)
        
        if not products:
            return {
                "success": True,
                "query": query,
                "dog_breed": dog_breed,
                "age": age,
                "count": 0,
                "recommendations": [],
                "summary": f"No products found for search term '{query}'"
            }
        
        # Get API keys from environment variables
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Log API key availability
        print(f"Tavily API key available: {bool(tavily_api_key)}")
        print(f"OpenAI API key available: {bool(openai_api_key)}")
        
        if not tavily_api_key:
            print("WARNING: No Tavily API key found in environment variables. Review search will use mock data.")
        
        # Generate personalized recommendations using AI agents with Tavily for reviews
        print(f"Starting product recommendations search for {dog_breed} {age} with query: '{query}'")
        recommendations = await get_product_recommendations(
            products=products,
            query=query,
            dog_breed=dog_breed,
            age=age,
            tavily_api_key=tavily_api_key,
            openai_api_key=openai_api_key,
            max_products=max_recommendations,
            include_groomers=include_groomers
        )
        
        print(f"Found {len(recommendations.recommendations)} recommended products")
        if include_groomers and recommendations.groomer_recommendations:
            print(f"Found {len(recommendations.groomer_recommendations)} recommended groomers")
        
        # Convert RecommendationResponse object to a dictionary response for the API
        response = {
            "success": True,
            "query": query,
            "dog_breed": dog_breed,
            "age": age,
            "count": len(recommendations.recommendations),
            "recommendations": [rec.dict() for rec in recommendations.recommendations],
            "summary": recommendations.summary
        }
        
        # Add groomer recommendations if available
        if include_groomers and recommendations.groomer_recommendations:
            response["groomer_count"] = len(recommendations.groomer_recommendations)
            response["groomer_recommendations"] = [groomer.dict() for groomer in recommendations.groomer_recommendations]
            response["groomer_summary"] = recommendations.groomer_summary or ""
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products")
async def get_products(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get a list of products from Pet Express website.
    
    Optional query parameters:
    - category: Filter products by category
    - page: Page number for pagination
    - limit: Number of products per page
    """
    try:
        products = await get_all_products(category, page, limit)
        return {
            "success": True,
            "count": len(products),
            "page": page,
            "limit": limit,
            "data": products
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/product/{product_id}")
async def get_product(product_id: str):
    """
    Get detailed information about a specific product by ID.
    """
    try:
        product = await get_product_details(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return {
            "success": True,
            "data": product
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_categories():
    """
    Get all product categories from Pet Express website.
    """
    try:
        categories = await get_product_categories()
        return {
            "success": True,
            "count": len(categories),
            "data": categories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
