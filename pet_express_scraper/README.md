# Pet Express Scraper API

A modern REST API for scraping product data from the Pet Express website (https://www.petexpress.com.ph/).

## Features

- Asynchronous web scraping with FastAPI
- Product listing with pagination and filtering
- Detailed product information retrieval
- Category listing and navigation 
- Clean API responses in JSON format

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pet_express_scraper
```

2. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the API server

Run the application with uvicorn:

```bash
python main.py
```

Or directly with uvicorn:

```bash
uvicorn main:app --reload
```

The API will be available at http://127.0.0.1:8000

### API Documentation

Once the server is running, you can access the auto-generated Swagger documentation at:
http://127.0.0.1:8000/docs

### API Endpoints

- **GET /api/products** - Get a list of products
  - Query parameters:
    - `category` (optional): Filter by category
    - `page` (optional, default=1): Page number for pagination
    - `limit` (optional, default=20): Number of products per page

- **GET /api/product/{product_id}** - Get detailed information about a specific product

- **GET /api/categories** - Get all product categories

## Example Requests

### Get all products
```
GET /api/products
```

### Get products from a specific category
```
GET /api/products?category=dog-food&page=1&limit=20
```

### Get detailed product information
```
GET /api/product/royal-canin-mini-adult
```

### Get all categories
```
GET /api/categories
```

## Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "count": 20,
  "page": 1,
  "limit": 20,
  "data": [
    // Array of product/category objects
  ]
}
```

## Legal Disclaimer

This scraper is for educational purposes only. Always respect the website's robots.txt and terms of service. Consider using rate limiting and caching to minimize the load on the target website.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
