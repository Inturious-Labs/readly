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

## Production Deployment (Linode)

### 1. Install system dependencies

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

### 2. Clone and setup

```bash
git clone <repo> /opt/readly
cd /opt/readly/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
playwright install-deps  # Install system dependencies for Chromium
```

### 3. Create systemd service

```bash
sudo nano /etc/systemd/system/readly.service
```

```ini
[Unit]
Description=Readly API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/readly/backend
ExecStart=/opt/readly/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable readly
sudo systemctl start readly
```

### 4. Configure nginx

```bash
sudo nano /etc/nginx/sites-available/readly
```

```nginx
server {
    listen 80;
    server_name api.readly.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/readly /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Add SSL with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.readly.example.com
```
