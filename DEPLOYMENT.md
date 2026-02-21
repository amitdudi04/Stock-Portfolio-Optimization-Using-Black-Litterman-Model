# 🚀 Production Deployment Guide

**Portfolio Optimization System - Deployment & Architecture**

---

## 📦 Deployment Options

### Option 1: Streamlit Cloud (Easiest - Free)

Perfect for quick deployment without infrastructure.

**Steps:**

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect your GitHub repository
4. Select `dashboard.py` as main file
5. Deploy in 2 clicks

**Pros:**
- Free tier available
- No infrastructure management
- Auto HTTPS
- Easy to share

**Cons:**
- Limited resources
- No persistent storage
- 1GB RAM limit

---

### Option 2: AWS Deployment (Scalable)

#### 2a. EC2 + Nginx

**Architecture:**
```
Client → CloudFront/ALB → Nginx → Gunicorn (FastAPI)
                       → Streamlit
```

**Steps:**

1. **Launch EC2 Instance**
   ```bash
   # Ubuntu 22.04 LTS, t3.medium
   ```

2. **Install Dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-venv nginx postgresql
   ```

3. **Setup Application**
   ```bash
   cd /opt
   git clone https://github.com/your-repo.git portfolio
   cd portfolio
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure Gunicorn**
   ```bash
   pip install gunicorn
   ```

   Create `/opt/portfolio/gunicorn_config.py`:
   ```python
   bind = "127.0.0.1:8000"
   workers = 4
   worker_class = "uvicorn.workers.UvicornWorker"
   ```

5. **Create SystemD Service**
   Create `/etc/systemd/system/portfolio-api.service`:
   ```ini
   [Unit]
   Description=Portfolio API
   After=network.target

   [Service]
   Type=notify
   User=ubuntu
   WorkingDirectory=/opt/portfolio
   Environment="PATH=/opt/portfolio/venv/bin"
   ExecStart=/opt/portfolio/venv/bin/gunicorn -c gunicorn_config.py api:app
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable portfolio-api
   sudo systemctl start portfolio-api
   ```

6. **Configure Nginx**
   Create `/etc/nginx/sites-available/portfolio`:
   ```nginx
   upstream fastapi {
       server 127.0.0.1:8000;
   }

   server {
       listen 80;
       server_name your-domain.com;

       client_max_body_size 100M;

       location / {
           proxy_pass http://fastapi;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /ws {
           proxy_pass http://fastapi;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
       }
   }
   ```

   ```bash
   sudo ln -s /etc/nginx/sites-available/portfolio /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

7. **Setup SSL (Let's Encrypt)**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

**Cost:** ~$10-50/month for t3.medium

---

#### 2b. AWS Lambda (Serverless)

**Steps:**

1. **Create Lambda Function**
   - Runtime: Python 3.11
   - Handler: `api.handler`

2. **Use ASGI Adapter**
   ```python
   # api.py wrapper
   from mangum import Mangum
   handler = Mangum(app)
   ```

3. **Set Layer with Dependencies**
   ```bash
   mkdir -p python
   pip install -r requirements.txt -t python/
   zip -r layer.zip python/
   # Upload as Lambda Layer
   ```

4. **Connect to API Gateway**
   - Create REST API
   - Configure CORS
   - Deploy stage

5. **Frontend on CloudFront**
   - Cache static assets
   - Compress responses

**Cost:** Pay per execution (~$0.20 per 1M requests)

---

### Option 3: Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run both services with supervisor
CMD ["sh", "-c", "python api.py & streamlit run dashboard.py --server.port=8501"]
```

**Docker Compose:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/portfolio
    depends_on:
      - db
    restart: always

  dashboard:
    build: .
    ports:
      - "8501:8501"
    depends_on:
      - api
    restart: always

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=portfolio_user
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=portfolio_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

**Deploy to Docker Hub:**
```bash
docker build -t username/portfolio-opt:1.0 .
docker push username/portfolio-opt:1.0
```

---

### Option 4: Render/Heroku (Simple Cloud)

**For Streamlit:**
```bash
# render.yaml
services:
  - type: web
    name: portfolio-dashboard
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run dashboard.py --server.port=$PORT
    envVars:
      - key: STREAMLIT_SERVER_HEADLESS
        value: true
      - key: STREAMLIT_SERVER_PORT
        value: $PORT
```

**Deploy:**
```bash
git push  # Auto deploys
```

**Cost:** $7/month starting

---

## 🗄️ Database Setup

### PostgreSQL (Production)

```sql
-- Create database
CREATE DATABASE portfolio_db;

-- Create tables
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    tickers TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE optimization_results (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id),
    model_type VARCHAR(50),
    weights JSONB,
    metrics JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id),
    sharpe_ratio FLOAT,
    max_drawdown FLOAT,
    win_rate FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_portfolio_created ON portfolios(created_at);
CREATE INDEX idx_results_portfolio ON optimization_results(portfolio_id);
CREATE INDEX idx_backtest_portfolio ON backtest_results(portfolio_id);
```

### SQLite (Development)

Already used in project - automatic file-based storage.

---

## 🔒 Security Best Practices

### 1. Environment Variables
```bash
# .env file (never commit)
DATABASE_URL=postgresql://user:pass@localhost/portfolio
API_KEY=your-secret-key
STREAMLIT_SERVER_HEADLESS=true
```

### 2. API Authentication
```python
# Add to api.py
from fastapi.security import HTTPBearer
from fastapi import Depends

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    if credentials.credentials != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid token")
    return credentials
```

### 3. Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/optimize")
@limiter.limit("10/minute")
async def optimize_portfolio(request):
    ...
```

### 4. CORS Configuration
```python
CORSMiddleware(
    app,
    allow_origins=["your-domain.com"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

### 5. HTTPS/SSL
- Use Let's Encrypt (free)
- Auto-renewal with certbot
- Always use HTTPS in production

---

## 📊 Monitoring & Logging

### Log Aggregation (AWS CloudWatch)
```python
import logging
from watchtower import CloudWatchLogHandler

logging.basicConfig(handlers=[
    CloudWatchLogHandler()
])
```

### Metrics (Prometheus)
```python
from prometheus_client import Counter, Histogram

request_count = Counter('requests_total', 'Total requests')
optimization_time = Histogram('optimization_seconds', 'Optimization time')
```

### Health Checks
```python
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "database": check_db_connection(),
        "cache": check_cache(),
        "timestamp": datetime.now()
    }
```

---

## 🚦 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest
      - run: black . --check
      - name: Deploy to AWS
        run: |
          aws deploy push --application-name portfolio \
            --s3-location s3://my-bucket/portfolio.zip \
            --ignore-hidden-files
```

---

## 📈 Scaling Strategies

### Horizontal Scaling
- Load balancer distributes traffic
- Multiple API instances
- Database connection pooling

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_market_data(ticker, date):
    return fetch_from_api(ticker, date)
```

### Asynchronous Jobs
```python
from celery import Celery

celery_app = Celery('portfolio')

@celery_app.task
def run_backtest_async(tickers, start_date):
    # Long-running task
    return backtest_results
```

---

## 💰 Cost Estimation

| Option | Monthly Cost | Scalability | Ease |
|--------|-------------|-------------|------|
| **Streamlit Cloud** | $0-20 | Low | ⭐⭐⭐⭐⭐ |
| **Heroku/Render** | $7-50 | Medium | ⭐⭐⭐⭐ |
| **AWS Lambda** | $0.20 per 1M req | Very High | ⭐⭐⭐ |
| **EC2** | $10-50 | Medium | ⭐⭐⭐ |
| **Docker/K8s** | $50+ | Very High | ⭐⭐ |

---

## ✅ Production Checklist

- [ ] Environment variables configured
- [ ] Database backups scheduled
- [ ] Monitoring/alerts set up
- [ ] Error logging enabled
- [ ] Rate limiting configured
- [ ] HTTPS/SSL enabled
- [ ] CORS properly configured
- [ ] Input validation added
- [ ] Unit tests written
- [ ] Load testing performed
- [ ] Documentation updated
- [ ] Security audit completed
- [ ] Disaster recovery plan
- [ ] Performance baseline set

---

## 🚀 Quick Start Commands

```bash
# Local development
streamlit run dashboard.py
python api.py

# Docker
docker build -t portfolio-opt .
docker run -p 8000:8000 -p 8501:8501 portfolio-opt

# Production (Gunicorn)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app

# With SSL
sudo certbot --nginx -d your-domain.com
```

---

**Ready for production deployment! 🚀**
