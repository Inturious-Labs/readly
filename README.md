# Readly

Convert WeChat articles to PDF and EPUB for reading on e-readers and any device.

## What it does

Paste a WeChat article URL, get PDF and EPUB files. Simple as that.

- Works with any WeChat Official Account (公众号) article
- Outputs both PDF and EPUB formats
- Optimized for e-ink readers (Kindle, Kobo, etc.)
- No account required

## Architecture

```
Frontend (Vercel/Cloudflare)     Backend (VPS)
┌─────────────────────┐          ┌─────────────────────────┐
│  Static HTML/JS     │  ──────> │  FastAPI + Playwright   │
│  URL input form     │          │  PDF/EPUB generation    │
│  Stripe payment     │          │                         │
└─────────────────────┘          └─────────────────────────┘
```

## Tech Stack

**Frontend:**
- Static HTML/CSS/JS
- Hosted on Vercel or Cloudflare Pages

**Backend:**
- Python + FastAPI
- Playwright (headless browser for WeChat scraping)
- ebooklib (EPUB generation)
- Hosted on any VPS (Linode, DigitalOcean, etc.)

**Payments:**
- Stripe + Alipay

## Local Development

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend

Just open `frontend/index.html` in a browser, or:

```bash
cd frontend
python3 -m http.server 3000
```

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

### Prerequisites

- A Linux VPS (Ubuntu/Debian recommended)
- Domain name pointed to your server
- nginx and certbot installed

### 1. Clone and setup

```bash
git clone https://github.com/Inturious-Labs/readly.git ~/readly
cd ~/readly/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
playwright install-deps
```

### 2. Setup systemd service

Edit the service file and replace `YOUR_USER` with your Linux username:
```bash
sed -i 's/YOUR_USER/your_actual_username/g' ~/readly/deploy/readly.service
```

Copy and enable the service:
```bash
sudo cp ~/readly/deploy/readly.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable readly
sudo systemctl start readly
```

Check status:
```bash
sudo systemctl status readly
```

### 3. Setup nginx with SSL

Create nginx config:
```bash
sudo nano /etc/nginx/sites-available/readly
```

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and get SSL:
```bash
sudo ln -s /etc/nginx/sites-available/readly /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d api.yourdomain.com
```

### Common commands

```bash
# View logs
sudo journalctl -u readly -f

# Restart service
sudo systemctl restart readly

# After code updates
cd ~/readly && git pull && sudo systemctl restart readly
```

## License

[MIT](LICENSE)
