import uvicorn
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from api.routes import router as api_router

app = FastAPI(
    title="Pet Express Scraper API",
    description="API for searching and retrieving product recommendations from Pet Express website",
    version="1.1.0"
)

# CORS Middleware - explicitly allow localhost:3000 (our frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Pet Express Scraper API",
        "docs": "/docs",
        "endpoints": [
            "/api/search?query={search_term}",  # Basic search endpoint
            "/api/recommend?query={search_term}&dog_breed={breed}&age={puppy|adult}",  # Recommendation endpoint
            "/api/products",
            "/api/product/{product_id}",
            "/api/categories"
        ],
        "usage_examples": [
            "/api/search?query=treats&page=1&limit=20",
            "/api/recommend?query=dog%20food&dog_breed=Labrador&age=puppy"
        ]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
