# 🚀 Installation & Deployment Guide

Complete guide for setting up CarbonTrack in development, staging, and production environments.

---

## 🎯 **Quick Start (5 Minutes)**

### **Prerequisites Checklist**
```bash
✅ Node.js 18+ installed
✅ Python 3.9+ installed  
✅ Git configured
✅ VS Code or preferred IDE
✅ Terminal/Command prompt access
```

### **Lightning Setup**
```bash
# Clone the repository
git clone https://github.com/ahmedul/CarbonTrack.git
cd CarbonTrack

# Install dependencies
cd frontend && npm install
cd ../backend && pip install -r requirements.txt

# Start development servers
npm run dev        # Frontend (port 3000)
python main.py     # Backend (port 8000)

# Open browser
open http://localhost:3000
```

🎉 **You're ready!** Login with `demo@carbontrack.dev` / `demo123`

---

## 🏗️ **Development Environment**

### **Frontend Setup (Vue.js)**
```bash
# Navigate to frontend directory
cd frontend/

# Install Node.js dependencies
npm install
# or using yarn
yarn install

# Available scripts
npm run dev          # Development server (hot reload)
npm run build        # Production build
npm run preview      # Preview production build
npm run test         # Run unit tests
npm run lint         # ESLint code checking
npm run format       # Prettier code formatting

# Environment configuration
cp .env.example .env.local
```

**`.env.local` Configuration:**
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT=10000

# Application Settings
VITE_APP_NAME=CarbonTrack
VITE_APP_VERSION=1.0.0
VITE_APP_ENV=development

# Feature Flags
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_NOTIFICATIONS=true
VITE_ENABLE_OFFLINE_MODE=false

# External Services
VITE_MAPBOX_API_KEY=your_mapbox_key_here
VITE_ANALYTICS_ID=your_analytics_id_here
```

### **Backend Setup (Python/FastAPI)**
```bash
# Navigate to backend directory
cd backend/

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Environment configuration
cp .env.example .env
```

**`.env` Configuration:**
```bash
# Application Settings
APP_NAME=CarbonTrack API
APP_VERSION=1.0.0
APP_ENV=development
DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///./carbontrack.db
# For PostgreSQL: postgresql://user:password@localhost:5432/carbontrack
# For MySQL: mysql://user:password@localhost:3306/carbontrack

# Security Settings
SECRET_KEY=your-super-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
CORS_ALLOW_CREDENTIALS=True

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@carbontrack.com

# External APIs
CARBON_FACTOR_API_KEY=your_api_key_here
WEATHER_API_KEY=your_weather_api_key_here

# AWS Configuration (For production)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET=carbontrack-storage
```

### **Database Setup**
```bash
# SQLite (Development - Default)
# Database file created automatically

# PostgreSQL (Recommended for production)
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib  # Ubuntu
brew install postgresql                         # macOS

# Create database and user
sudo -u postgres psql
CREATE DATABASE carbontrack;
CREATE USER carbontrack_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE carbontrack TO carbontrack_user;

# Run migrations
python scripts/create_tables.py
python scripts/seed_data.py  # Optional: Add sample data
```

---

## 🐳 **Docker Setup**

### **Docker Compose (Recommended)**
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build: 
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://carbontrack:password@db:5432/carbontrack
      - SECRET_KEY=docker-secret-key-change-me
    depends_on:
      - db
    volumes:
      - ./backend:/app

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=carbontrack
      - POSTGRES_USER=carbontrack
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

**Quick Docker Commands:**
```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Reset database
docker-compose down -v && docker-compose up --build
```

### **Individual Dockerfiles**

**Frontend Dockerfile:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Use nginx to serve static files
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ☁️ **Cloud Deployment**

### **AWS Deployment (Production Ready)**

#### **Architecture Overview**
```
┌─────────────────────────────────────────────┐
│                CloudFront                   │  ← CDN
├─────────────────────────────────────────────┤
│     S3 (Static Files) │ API Gateway         │  ← Frontend/API
├─────────────────────────────────────────────┤
│              Lambda Functions               │  ← Backend
├─────────────────────────────────────────────┤
│     DynamoDB      │    RDS PostgreSQL       │  ← Database
├─────────────────────────────────────────────┤
│        ElastiCache Redis │ SES Email        │  ← Services
└─────────────────────────────────────────────┘
```

#### **AWS CDK Deployment**
```typescript
// infrastructure/lib/carbontrack-stack.ts
import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';

export class CarbonTrackStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // S3 bucket for frontend
    const websiteBucket = new s3.Bucket(this, 'CarbonTrackWebsite', {
      websiteIndexDocument: 'index.html',
      publicReadAccess: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    // Lambda function for backend
    const backendFunction = new lambda.Function(this, 'CarbonTrackAPI', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'main.handler',
      code: lambda.Code.fromAsset('../backend'),
      environment: {
        DATABASE_URL: process.env.DATABASE_URL!,
        SECRET_KEY: process.env.SECRET_KEY!
      }
    });

    // API Gateway
    const api = new apigateway.RestApi(this, 'CarbonTrackAPIGateway', {
      restApiName: 'CarbonTrack API'
    });

    const apiIntegration = new apigateway.LambdaIntegration(backendFunction);
    api.root.addProxy({
      defaultIntegration: apiIntegration
    });
  }
}
```

**Deploy with CDK:**
```bash
# Install AWS CDK
npm install -g aws-cdk

# Navigate to infrastructure
cd infrastructure/

# Install dependencies
npm install

# Configure AWS credentials
aws configure

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy stack
cdk deploy CarbonTrackStack

# View outputs
cdk outputs
```

#### **Manual AWS Setup**

**1. S3 Static Website:**
```bash
# Create S3 bucket
aws s3 mb s3://carbontrack-frontend

# Configure static website hosting
aws s3 website s3://carbontrack-frontend \
  --index-document index.html \
  --error-document error.html

# Upload built files
cd frontend && npm run build
aws s3 sync dist/ s3://carbontrack-frontend

# Set public read policy
aws s3api put-bucket-policy \
  --bucket carbontrack-frontend \
  --policy file://s3-bucket-policy.json
```

**2. Lambda Function:**
```bash
# Package backend code
cd backend/
zip -r carbontrack-api.zip . -x "venv/*" "tests/*" "__pycache__/*"

# Create Lambda function
aws lambda create-function \
  --function-name CarbonTrackAPI \
  --runtime python3.11 \
  --role arn:aws:iam::account:role/lambda-execution-role \
  --handler main.handler \
  --zip-file fileb://carbontrack-api.zip

# Update environment variables
aws lambda update-function-configuration \
  --function-name CarbonTrackAPI \
  --environment Variables='{
    "DATABASE_URL":"postgresql://...",
    "SECRET_KEY":"your-secret-key"
  }'
```

### **Vercel Deployment (Simple)**
```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": { "distDir": "dist" }
    },
    {
      "src": "backend/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/main.py"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/dist/$1"
    }
  ],
  "env": {
    "DATABASE_URL": "@database-url",
    "SECRET_KEY": "@secret-key"
  }
}
```

**Deploy to Vercel:**
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Set environment variables
vercel env add DATABASE_URL
vercel env add SECRET_KEY

# Deploy to production
vercel --prod
```

### **Netlify Deployment**
```toml
# netlify.toml
[build]
  publish = "frontend/dist"
  command = "cd frontend && npm run build"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/api/*"
  to = "https://your-backend-api.com/api/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**Deploy to Netlify:**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Initialize site
netlify init

# Deploy
netlify deploy

# Deploy to production
netlify deploy --prod
```

---

## 🏢 **Production Configuration**

### **Environment Variables (Production)**
```bash
# Application Settings
APP_ENV=production
DEBUG=False
LOG_LEVEL=INFO

# Security (CRITICAL - Change these!)
SECRET_KEY=your-super-secure-random-key-here-256-bits
JWT_SECRET_KEY=different-jwt-secret-key-here

# Database (Use managed database service)
DATABASE_URL=postgresql://user:pass@prod-db.amazonaws.com:5432/carbontrack
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=0

# Redis Cache
REDIS_URL=redis://prod-redis.amazonaws.com:6379/0

# CORS (Restrict to your domains)
CORS_ORIGINS=["https://carbontrack.com", "https://www.carbontrack.com"]

# Email Service
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USE_TLS=True

# File Storage
AWS_S3_BUCKET=carbontrack-prod-storage
CDN_URL=https://cdn.carbontrack.com

# Monitoring
SENTRY_DSN=https://your-sentry-dsn-here
NEW_RELIC_LICENSE_KEY=your-newrelic-key

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600  # 1 hour
```

### **Performance Optimization**
```bash
# Frontend Optimization
npm run build          # Production build with minification
npm run analyze        # Bundle size analysis

# Backend Optimization
pip install gunicorn uvloop httptools  # Production server
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Database Optimization
# Create indexes for frequently queried fields
CREATE INDEX idx_user_emissions_date ON user_emissions(user_id, date);
CREATE INDEX idx_users_email ON users(email);

# Configure connection pooling
DATABASE_POOL_SIZE=20
DATABASE_POOL_RECYCLE=3600
```

### **SSL/TLS Configuration**
```nginx
# nginx.conf (if using nginx reverse proxy)
server {
    listen 443 ssl http2;
    server_name carbontrack.com www.carbontrack.com;

    # SSL Configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    # Frontend
    location / {
        root /var/www/carbontrack;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name carbontrack.com www.carbontrack.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 📊 **Monitoring & Logging**

### **Application Monitoring**
```python
# backend/monitoring.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Initialize Sentry
sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[
        FastApiIntegration(auto_enabling=True),
        SqlalchemyIntegration()
    ],
    traces_sample_rate=0.1,
    environment="production"
)

# Custom metrics
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Middleware for metrics
@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    REQUEST_COUNT.labels(
        method=request.method, 
        endpoint=str(request.url.path)
    ).inc()
    
    REQUEST_DURATION.observe(time.time() - start_time)
    return response
```

### **Logging Configuration**
```python
# backend/logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    # JSON formatter for structured logging
    logHandler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    logHandler.setFormatter(formatter)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(logging.INFO)
    
    # Configure specific loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Usage in main.py
setup_logging()
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("CarbonTrack API starting up", extra={
        "version": app.version,
        "environment": settings.APP_ENV
    })
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Frontend Issues**
```bash
# Issue: Build fails with memory error
export NODE_OPTIONS="--max-old-space-size=8192"
npm run build

# Issue: CORS errors in development
# Add to vite.config.js:
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})

# Issue: Environment variables not loading
# Ensure variables start with VITE_ prefix
VITE_API_BASE_URL=http://localhost:8000

# Issue: White screen on deployment
# Check browser console for JavaScript errors
# Verify build output in dist/ folder
# Check server MIME types for .js and .css files
```

#### **Backend Issues**
```bash
# Issue: Database connection failed
# Check DATABASE_URL format and credentials
# Ensure database server is running
# Test connection:
python -c "from sqlalchemy import create_engine; print(create_engine('your_db_url').connect())"

# Issue: CORS errors
# Verify CORS_ORIGINS includes frontend URL
# Check for trailing slashes in URLs
# Enable credentials if needed:
CORS_ALLOW_CREDENTIALS=True

# Issue: JWT token errors
# Ensure SECRET_KEY is set and consistent
# Check token expiration settings
# Verify token format in requests

# Issue: Import errors
# Ensure all dependencies are installed:
pip install -r requirements.txt
# Check Python path and virtual environment

# Issue: Permission denied on file operations
# Check file permissions
# Ensure correct user ownership
# Use absolute paths in configuration
```

#### **Deployment Issues**
```bash
# Issue: 502 Bad Gateway
# Check if backend service is running
# Verify proxy configuration
# Check service logs for errors

# Issue: Static files not loading
# Verify build output exists
# Check file permissions
# Configure proper MIME types
# Enable gzip compression

# Issue: Environment variables not set
# Check deployment platform variable configuration
# Verify variable names match code
# Use platform-specific variable syntax

# Issue: Database migrations failing
# Run migrations manually:
python scripts/create_tables.py
# Check database user permissions
# Verify schema exists
```

### **Performance Issues**
```bash
# Frontend Performance
# Enable production mode
npm run build -- --mode production

# Use CDN for static assets
# Enable gzip compression
# Implement code splitting
# Optimize images and fonts

# Backend Performance  
# Use production WSGI server
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Enable database connection pooling
# Implement Redis caching
# Optimize database queries
# Use async/await properly

# Monitor with tools:
# - Frontend: Lighthouse, WebPageTest
# - Backend: New Relic, Datadog
# - Database: pg_stat_statements, slow query log
```

---

## 📚 **Additional Resources**

### **Documentation Links**
- [Vue.js Documentation](https://vuejs.org/guide/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AWS Deployment Guide](https://aws.amazon.com/getting-started/)
- [Docker Documentation](https://docs.docker.com/)

### **Support Channels**
- **GitHub Issues**: [Report bugs and feature requests](https://github.com/ahmedul/CarbonTrack/issues)
- **Discussions**: [Community support and questions](https://github.com/ahmedul/CarbonTrack/discussions)
- **Email**: support@carbontrack.com
- **Documentation**: [Full documentation wiki](https://github.com/ahmedul/CarbonTrack/wiki)

---

**Ready to deploy?** Choose your platform and follow the appropriate guide above! 🚀

*Need help? Join our [community discussions](https://github.com/ahmedul/CarbonTrack/discussions) or reach out via email.*

---

**Last Updated**: September 30, 2025  
**Tested Environments**: Node.js 18+, Python 3.9+, AWS, Vercel, Netlify