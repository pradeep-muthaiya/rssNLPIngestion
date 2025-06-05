# RSS NLP Ingestion Service

A FastAPI service that ingests RSS feeds, extracts thesis statements using NLP, and organizes content into themes.

## Features

- RSS feed ingestion on schedule or on demand
- NLP-based thesis statement extraction
- Theme detection and organization
- RESTful API endpoints for theme exploration
- SQLite database for data persistence

## Prerequisites

- Python 3.8+
- Virtual environment (recommended)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd rss-nlp-ingestion
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (optional):
Create a `.env` file in the project root with the following variables:
```
SQLITE_DB_PATH=path/to/your/database.db  # Optional, defaults to rss_nlp.db in the current directory
```

5. Initialize the database:
```bash
alembic upgrade head
```

6. Configure RSS feeds:
Edit `app/core/config.py` and add your RSS feed URLs to the `RSS_FEEDS` list.

## Running the Service

Start the service with:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /themes` - List all themes with post counts
- `GET /themes/{id}` - Get a timeline view of posts for a specific theme

## API Documentation

Once the service is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

The project structure is organized as follows:
```
app/
├── core/           # Core configuration
├── db/            # Database configuration
├── models.py      # Database models
├── routers/       # API endpoints
├── services/      # Business logic
└── main.py        # Application entry point
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 