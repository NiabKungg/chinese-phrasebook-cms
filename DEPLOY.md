# Deploy Chinese Phrasebook on Ubuntu Server

## 1. Setup Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+ and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Nginx
sudo apt install nginx -y

# Install certbot (for HTTPS)
sudo apt install certbot python3-certbot-nginx -y
```

## 2. Create Project Directory

```bash
# Create user and directory
sudo useradd -m -s /bin/bash phrasebook
sudo mkdir -p /opt/chinese-phrasebook
sudo chown -R phrasebook:phrasebook /opt/chinese-phrasebook

# Copy the project (from your local machine)
# Option A: Using rsync from your local machine
#   rsync -avz ./ chinese-phrasebook-main/ user@your-server:/opt/chinese-phrasebook/
#
# Option B: Using git (if you push to a repo first)
#   sudo -u phrasebook git clone <repo-url> /opt/chinese-phrasebook
```

## 3. Setup Python Virtual Environment

```bash
sudo -u phrasebook bash
cd /opt/chinese-phrasebook/backend

# Create venv and activate
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install uvicorn
```

## 4. Configure Production Settings

```bash
# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
# Copy the output, e.g.: a1b2c3d4e5f6...

# Edit config
nano /opt/chinese-phrasebook/backend/app/config.py
```

Change in `config.py`:
```python
SECRET_KEY = "paste-your-generated-secret-key-here"
```

Change default admin password (optional but recommended):
```bash
# After first login via admin panel, change the password.
# Or you can edit seed.py before running it.
```

## 5. Seed Database & Generate Audio

```bash
cd /opt/chinese-phrasebook/backend
source venv/bin/activate
python seed.py
# This will create the DB and generate all 151 audio files (~5-10 minutes)
```

## 6. Create Systemd Service

```bash
sudo nano /etc/systemd/system/phrasebook.service
```

Paste:
```ini
[Unit]
Description=Chinese Phrasebook API
After=network.target

[Service]
User=phrasebook
Group=phrasebook
WorkingDirectory=/opt/chinese-phrasebook/backend
Environment="PATH=/opt/chinese-phrasebook/backend/venv/bin"
ExecStart=/opt/chinese-phrasebook/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl daemon-reload
sudo systemctl enable phrasebook
sudo systemctl start phrasebook

# Check status
sudo systemctl status phrasebook
```

## 7. Configure Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/phrasebook
```

Paste:
```nginx
server {
    listen 80;
    server_name your-domain.com;   # Change this

    # Frontend (static files)
    root /opt/chinese-phrasebook;
    index index.html;

    # Serve audio files
    location /audio/ {
        alias /opt/chinese-phrasebook/audio/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Serve admin panel
    location /admin/ {
        alias /opt/chinese-phrasebook/admin/;
        try_files $uri /admin/index.html;
    }

    # Proxy API requests
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;   # Long timeout for audio generation
    }

    # API docs
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/phrasebook /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default   # Remove default

# Test config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

## 8. Firewall

```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

## 9. HTTPS (Let's Encrypt)

```bash
# Ensure domain points to your server IP first
sudo certbot --nginx -d your-domain.com
# Follow prompts, choose redirect HTTP -> HTTPS
```

## 10. Update Frontend API URL

```bash
# Edit public frontend
nano /opt/chinese-phrasebook/index.html
```

Find and change:
```javascript
const API_BASE = 'http://localhost:8000/api/public';
// Change to:
const API_BASE = '/api/public';
```

```bash
# Edit admin panel
nano /opt/chinese-phrasebook/admin/index.html
```

Find and change:
```javascript
const API = 'http://localhost:8000/api';
// Change to:
const API = '/api';
```

## 11. Verify Everything

```bash
# Check service is running
sudo systemctl status phrasebook

# Test API locally
curl http://127.0.0.1:8000/api/health

# Test via domain
curl https://your-domain.com/api/health
curl https://your-domain.com/api/public/phrasebook
```

## Quick Reference

| What | URL |
|---|---|
| Public Site | `https://your-domain.com` |
| Admin Panel | `https://your-domain.com/admin/` |
| API Docs | `https://your-domain.com/docs` |
| Login | `admin` / `admin123` |

## Useful Commands

```bash
# View logs
sudo journalctl -u phrasebook -f

# Restart after code changes
sudo systemctl restart phrasebook

# Regenerate all audio
cd /opt/chinese-phrasebook/backend
sudo -u phrasebook venv/bin/python -c "
from app.database import SessionLocal
from app.models import Phrase
import asyncio, edge_tts

async def regen():
    db = SessionLocal()
    for p in db.query(Phrase).all():
        tts = edge_tts.Communicate(p.chinese, 'zh-CN-XiaoxiaoNeural', rate='-10%')
        await tts.save(f'../audio/phrase_{p.id}.mp3')
        p.audio_file = f'phrase_{p.id}.mp3'
    db.commit()
    db.close()
asyncio.run(regen())
"
```
