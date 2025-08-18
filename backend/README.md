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
- **RESTful API**: Well-documented REST API with OpenAPI/Swagger
- **Type Safety**: Full type hints with Pydantic models
- **Testing**: Comprehensive test suite with pytest
- **Production Ready**: Structured for scalability and maintainability

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
│   │       └── carbon.py       # Carbon tracking routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration settings
│   │   └── middleware.py       # Authentication middleware
│   ├── models/
│   │   └── __init__.py         # Database models (future)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication schemas
│   │   └── carbon.py          # Carbon tracking schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth_service.py    # Authentication business logic
│   └── utils/
│       ├── __init__.py
│       └── carbon_calculator.py # Carbon calculation utilities
├── tests/
│   ├── conftest.py            # Test configuration
│   └── test_auth.py           # Authentication tests
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

## 🔐 Authentication

The API uses AWS Cognito for user management and JWT tokens for authentication.

### Environment Variables

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Cognito Configuration
COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
COGNITO_CLIENT_ID=your_client_id
COGNITO_CLIENT_SECRET=your_client_secret

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_change_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Protected Endpoints

Most endpoints require authentication. Include the JWT token in the Authorization header:

```bash
Authorization: Bearer <your_jwt_token>
```

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

- [ ] Database integration (PostgreSQL/DynamoDB)
- [ ] Real-time notifications
- [ ] Advanced analytics with ML
- [ ] Social features and team challenges
- [ ] Mobile app integration
- [ ] Third-party integrations (fitness trackers, etc.)
- [ ] Carbon offset marketplace
- [ ] Corporate dashboard

---

Built with ❤️ for a sustainable future 🌍
