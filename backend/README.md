# 🌱 CarbonTrack Backend API

A comprehensive FastAPI-based backend for tracking and reducing carbon footprints with AWS Cognito authentication.

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Authentication](#-authentication)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

## 🚀 Features

- **User Authentication**: AWS Cognito integration with JWT tokens
- **Carbon Tracking**: Log and track various types of carbon emissions
- **Analytics**: Comprehensive analytics and reporting
- **Goals & Achievements**: Gamification features to encourage eco-friendly behavior
- **🆕 CSRD Compliance Module**: EU Corporate Sustainability Reporting Directive support
  - Automated ESRS E1-E5 environmental reporting
  - Scope 1, 2, 3 emissions categorization
  - PDF generation with compliance validation
  - XBRL export for regulatory filing
  - Multi-year trend analysis and forecasting
  - Audit trail for third-party verification
- **RESTful API**: Well-documented REST API with OpenAPI/Swagger (19 CSRD endpoints)
- **Type Safety**: Full type hints with Pydantic models
- **Testing**: Comprehensive test suite with pytest
- **Production Ready**: Structured for scalability and maintainability on AWS Lambda

## 🛠 Tech Stack

- **Framework**: FastAPI 0.104.1
- **Authentication**: AWS Cognito + JWT
- **Validation**: Pydantic 2.5.0
- **Server**: Uvicorn
- **Testing**: Pytest
- **Code Quality**: Black, isort, flake8
- **Cloud**: AWS (Cognito, Lambda-ready with Mangum)

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py          # Main API router
│   │       ├── auth.py         # Authentication routes
│   │       ├── carbon.py       # Carbon tracking routes
│   │       ├── csrd.py         # CSRD compliance routes (NEW)
│   │       ├── gamification.py # Achievements & leaderboards
│   │       └── recommendations.py # AI-powered recommendations
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration settings
│   │   └── middleware.py       # Authentication middleware
│   ├── models/
│   │   ├── __init__.py
│   │   └── csrd.py            # CSRD database models (NEW)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication schemas
│   │   ├── carbon.py          # Carbon tracking schemas
│   │   └── csrd.py            # CSRD compliance schemas (NEW)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py    # Authentication business logic
│   │   ├── carbon_service.py  # Carbon calculation logic
│   │   └── csrd/              # CSRD module (NEW)
│   │       ├── __init__.py
│   │       ├── pdf_generator.py       # PDF report generation
│   │       ├── compliance_validator.py # ESRS validation
│   │       └── xbrl_exporter.py       # XBRL export
│   └── utils/
│       ├── __init__.py
│       └── carbon_calculator.py # Carbon calculation utilities
├── tests/
│   ├── conftest.py            # Test configuration
│   ├── test_auth.py           # Authentication tests
│   ├── test_carbon.py         # Carbon tracking tests
│   └── test_csrd.py           # CSRD module tests (NEW)
├── docs/
│   ├── POSTMAN_TESTING_GUIDE.md
│   └── CarbonTrack_Postman_Collection.json
├── scripts/
│   └── test_api.sh            # API testing script
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/CarbonTrack.git
cd CarbonTrack/backend
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Run the Development Server

```bash
# From the backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Documentation

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health check

### Authentication (`/api/v1/auth`)
- `POST /register` - Register new user
- `POST /login` - User login
- `POST /refresh` - Refresh access token
- `POST /reset-password` - Initiate password reset
- `POST /confirm-reset-password` - Confirm password reset
- `GET /me` - Get current user info
- `POST /logout` - Logout user

### Carbon Tracking (`/api/v1/carbon-emissions`)
- `GET /` - Get user's emissions (with filtering)
- `POST /` - Create new emission entry
- `PUT /{emission_id}` - Update emission entry
- `DELETE /{emission_id}` - Delete emission entry
- `GET /analytics` - Get analytics and insights

### Goals (`/api/v1/goals`)
- `GET /` - Get user's goals
- `POST /` - Create new goal

### Achievements (`/api/v1/achievements`)
- `GET /` - Get user's achievements

### Gamification (`/api/v1/gamification`)
- `GET /profile` - Get user gamification profile
- `GET /achievements` - Get achievement progress
- `GET /leaderboards` - Get leaderboard rankings

### Recommendations (`/api/v1/recommendations`)
- `GET /` - Get personalized carbon reduction recommendations
- `GET /stats` - Get recommendation statistics

### 🆕 CSRD Compliance (`/api/v1/csrd`)
**Reports Management**
- `POST /reports` - Create new CSRD report
- `GET /reports` - List all reports for organization
- `GET /reports/{report_id}` - Get specific report details
- `PUT /reports/{report_id}` - Update report information
- `DELETE /reports/{report_id}` - Delete report
- `GET /reports/{report_id}/export/pdf` - Export report as PDF
- `GET /reports/{report_id}/export/xbrl` - Export report as XBRL

**Emissions Data**
- `POST /reports/{report_id}/emissions` - Add emissions data entry
- `GET /reports/{report_id}/emissions` - Get all emissions for report
- `PUT /emissions/{emission_id}` - Update emissions entry
- `DELETE /emissions/{emission_id}` - Delete emissions entry

**ESRS Metrics**
- `POST /reports/{report_id}/esrs-metrics` - Add ESRS metric
- `GET /reports/{report_id}/esrs-metrics` - Get all metrics for report
- `PUT /esrs-metrics/{metric_id}` - Update ESRS metric
- `DELETE /esrs-metrics/{metric_id}` - Delete ESRS metric

**Validation & Analysis**
- `POST /reports/{report_id}/validate` - Validate report compliance
- `GET /reports/{report_id}/analysis` - Get emissions analysis and trends
- `GET /organizations/{org_id}/summary` - Get organization-wide summary
- `GET /deadlines` - Get upcoming CSRD compliance deadlines

## 🔐 Authentication

The API uses JWT-based authentication with AWS Cognito integration.

### Development Mode

In development, mock authentication is used by default. You can test endpoints with these tokens:
- `mock_jwt_token` - Regular user
- `mock_admin` - Admin user  
- Any token starting with `mock_` - Creates a test user

### Production Setup

For production with real AWS Cognito:

1. **Set up AWS Cognito infrastructure:**
   ```bash
   cd infra
   ./setup-cognito.sh
   ```

2. **Update environment variables:**
   ```bash
   # Copy generated config to .env
   cp aws-cognito-config.txt .env.cognito
   # Update .env with real values
   ```

3. **Configure credentials in `.env`:**
   ```bash
   DEBUG=False
   COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX  # Get from AWS Cognito Console
   COGNITO_CLIENT_ID=your_client_id_here     # Get from App Integration tab
   COGNITO_CLIENT_SECRET=your_secret_here    # Generate in App clients
   AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE    # Optional: if not using IAM role
   AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY  # Optional
   ```

4. **Test authentication:**
   ```bash
   ./scripts/test-auth.sh
   ```

### AWS Cognito Setup

For detailed AWS Cognito setup instructions, see: [AWS Cognito Setup Guide](../infra/AWS_COGNITO_SETUP.md)

## 🛠 Development

### Code Formatting

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### API Testing

Use the provided scripts and Postman collection:

```bash
# Quick API test
./scripts/test_api.sh

# Or use Postman with the provided collection
# Import: docs/CarbonTrack_Postman_Collection.json
```

## 🚀 Deployment

### Local Production

```bash
# Using Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Docker (future)
docker build -t carbontrack-api .
docker run -p 8000:8000 carbontrack-api
```

### AWS Lambda

The application is ready for AWS Lambda deployment using Mangum:

```python
# lambda_handler.py
from mangum import Mangum
from app.main import app

handler = Mangum(app)
```

### Environment-Specific Configuration

Create different `.env` files for different environments:
- `.env.development`
- `.env.staging`
- `.env.production`

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test category
pytest tests/test_auth.py

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Test Categories

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test API endpoints
3. **Authentication Tests**: Test auth flows
4. **Validation Tests**: Test Pydantic schemas

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write tests for new features
- Update documentation as needed
- Use meaningful commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

- **Documentation**: http://localhost:8000/docs
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

## 🔮 Future Enhancements

- [✅] ~~Database integration (DynamoDB)~~ **COMPLETED**
- [✅] ~~Real-time notifications~~ **COMPLETED (Gamification)**
- [✅] ~~Advanced analytics with ML~~ **COMPLETED (AI Recommendations)**
- [🔄] CSRD Compliance Module **85% COMPLETE - Launching Q1 2026**
  - [✅] Backend API (19 endpoints)
  - [✅] Database schema (DynamoDB tables)
  - [✅] PDF generation & XBRL export
  - [✅] Compliance validation logic
  - [🔄] Frontend UI (in progress)
  - [ ] Third-party verification workflows
- [ ] Social features and team challenges
- [ ] Mobile app integration
- [ ] Third-party integrations (ERP, accounting systems)
- [ ] Carbon offset marketplace
- [ ] Corporate multi-tenant dashboard
- [ ] SSO/SAML enterprise authentication
- [ ] White-label options for B2B customers

### 🎯 Production Status

**Current Environment**: AWS Lambda + API Gateway (eu-central-1)
- **API Endpoint**: https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod
- **CloudFront CDN**: https://d2z2og1o0b9esb.cloudfront.net
- **Domain**: carbontracksystem.com (launching Q1 2026)
- **Uptime**: 99.9% SLA
- **Active Users**: Growing steadily
- **Branch**: `main` (production), `feature/csrd-compliance-module` (CSRD development)

---

Built with ❤️ for a sustainable future 🌍
# Backend deployment trigger
