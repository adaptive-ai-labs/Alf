# Alf Pet Services Platform

This project consists of two main components:

1. **Pet Express Scraper API (Backend)**: A FastAPI service for scraping pet product data
2. **Dog Upload Form (Frontend)**: A Next.js web application for uploading and managing dog information

## Project Structure

```
Alf/
├── pet_express_scraper/  # Backend API service
└── dog-upload-form/      # Frontend web application
```

## Backend Setup (Pet Express Scraper API)

### Prerequisites

- Python 3.8 or higher
- uv (Fast Python package manager, written in Rust)

### Installing uv

If you don't have uv installed, you can install it with:

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### Installation

1. Navigate to the backend directory:

```bash
cd pet_express_scraper
```

2. Set up a virtual environment and install dependencies with uv:

```bash
# Create virtual environment and install dependencies in one step
uv pip sync requirements.txt

# Activate the virtual environment
# On macOS/Linux
source .venv/bin/activate

# On Windows
# .venv\Scripts\activate
```

   Note: uv automatically creates a virtual environment in .venv if one doesn't exist

3. Set up environment variables:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your configuration
# Fill in required API keys and settings
```

### Running the Backend

Start the API server using one of the following methods:

```bash
# Method 1: Run with Python
python main.py

# Method 2: Run with Uvicorn directly
uvicorn main:app --reload

# Method 3: Run using uv's script execution (if configured in pyproject.toml)
uv run main
```

The API will be available at http://127.0.0.1:8000

API documentation (Swagger UI) will be available at http://127.0.0.1:8000/docs

## Frontend Setup (Dog Upload Form)

### Prerequisites

- Node.js 16 or higher
- npm or yarn package manager

### Installation

1. Navigate to the frontend directory:

```bash
cd dog-upload-form
```

2. Install dependencies:

```bash
# Using npm
npm install

# OR using yarn
yarn install
```

### Running the Frontend

Start the Next.js development server:

```bash
# Using npm
npm run dev

# OR using yarn
yarn dev
```

The web application will be available at http://localhost:3000

## Running the Full Stack

For the complete application experience, you need to run both the backend and frontend simultaneously:

1. Start the backend server in one terminal following the backend setup instructions above
2. Start the frontend development server in another terminal following the frontend setup instructions above
3. The frontend application will connect to the backend API for data retrieval and processing

## Environment Variables

### Backend (.env)

Ensure you configure the following variables in your pet_express_scraper/.env file:

```
# Example environment variables (check .env.example for complete list)
OPENAI_API_KEY=your_openai_api_key
DEBUG=True
```

## Development Workflow

1. Make changes to the frontend or backend code
2. The development servers will automatically reload when changes are detected
3. Test your changes in the browser

## Production Deployment

### Backend

To deploy the backend to a production environment:

```bash
cd pet_express_scraper

# Build Docker image (if using Docker)
docker build -t pet-express-api .

# Run Docker container
docker run -p 8000:8000 -d pet-express-api
```

### Frontend

To deploy the frontend to a production environment:

```bash
cd dog-upload-form

# Build for production
npm run build
# or
yarn build

# Start production server
npm start
# or
yarn start
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
