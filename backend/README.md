# Readly Backend

FastAPI service that converts webpage URLs to PDF and EPUB.

## Setup

### 1. Create virtual environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright browsers

```bash
playwright install chromium
```

### 4. Run the server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /health
```

### Convert URL
```
POST /convert
Content-Type: application/json

{
    "url": "https://mp.weixin.qq.com/s/..."
}
```

Response:
```json
{
    "job_id": "abc12345",
    "title": "Article Title",
    "pdf_url": "/download/abc12345/pdf",
    "epub_url": "/download/abc12345/epub"
}
```

### Download File
```
GET /download/{job_id}/pdf
GET /download/{job_id}/epub
```

## Production Deployment

See `deploy/README.md` for server deployment instructions (systemd, nginx, SSL).
