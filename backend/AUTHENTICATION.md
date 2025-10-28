# JWT Authentication Implementation

This document describes the JWT-based authentication system implemented for the MTGA Deck Builder API.

## Overview

The authentication system provides secure user registration and login functionality using JWT (JSON Web Tokens) and bcrypt password hashing.

## Components

### 1. User Model (`app/models/user.py`)
- SQLAlchemy model for storing user data
- Fields: id, username, email, hashed_password, is_active, is_superuser, created_at, updated_at
- Passwords are never stored in plain text

### 2. Authentication Utilities (`app/core/auth.py`)
- Password hashing with bcrypt
- JWT token generation and validation
- Token expiration: 30 minutes (configurable in .env)

### 3. Authentication Dependencies (`app/core/dependencies.py`)
- `get_current_user`: Extract and validate user from JWT token
- `get_current_active_user`: Ensure user is active
- `get_current_superuser`: Verify superuser privileges

### 4. Authentication Routes (`app/routes/auth.py`)
- `POST /api/auth/register`: Register a new user
- `POST /api/auth/login`: Login with form data (OAuth2 compatible)
- `POST /api/auth/login/json`: Login with JSON payload
- `GET /api/auth/me`: Get current user information

### 5. Auth Schemas (`app/models/auth_schemas.py`)
- UserCreate: Registration data with password validation
- UserLogin: Login credentials
- UserResponse: User data without password
- Token: JWT token response
- TokenData: Token payload

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Update `backend/.env` with a secure SECRET_KEY:
```
SECRET_KEY=<your-secure-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Run Database Migration
```bash
cd backend
alembic upgrade head
```

This creates the `users` table in your PostgreSQL database.

## Usage

### Register a New User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

Password requirements:
- Minimum 8 characters
- At least one letter
- At least one digit

### Login (Form Data - OAuth2 Compatible)
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePass123"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Login (JSON)
```bash
curl -X POST "http://localhost:8000/api/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123"
  }'
```

### Access Protected Endpoints
Include the JWT token in the Authorization header:

```bash
curl -X POST "http://localhost:8000/decks" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Deck",
    "format": "Standard",
    "colors": ["U", "B"]
  }'
```

### Get Current User Info
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Protected Endpoints

The following endpoints now require authentication:

### Deck Endpoints
- `POST /decks` - Create deck
- `PUT /decks/{deck_id}` - Update deck
- `DELETE /decks/{deck_id}` - Delete deck
- `POST /api/decks/generate` - Generate deck with AI
- `POST /api/decks/build` - Build deck workflow

### Public Endpoints (No Authentication Required)
- `GET /decks` - List decks
- `GET /decks/{deck_id}` - Get deck details
- `GET /cards` - List cards
- `GET /cards/{card_id}` - Get card details
- `GET /health` - Health check
- `GET /` - API root

## Security Features

1. **Password Hashing**: Uses bcrypt with automatic salt generation
2. **JWT Tokens**: Secure token-based authentication
3. **Token Expiration**: Tokens expire after 30 minutes
4. **Email Validation**: Valid email format required
5. **Password Strength**: Enforced minimum requirements
6. **User Status**: Support for active/inactive users
7. **Role-Based Access**: Support for superuser privileges

## Database Schema

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_superuser BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ix_users_id ON users(id);
CREATE UNIQUE INDEX ix_users_username ON users(username);
CREATE UNIQUE INDEX ix_users_email ON users(email);
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: User registered successfully
- `400 Bad Request`: Invalid input (duplicate username/email, weak password)
- `401 Unauthorized`: Invalid credentials or expired token
- `403 Forbidden`: Insufficient privileges
- `404 Not Found`: Resource not found

## Testing

### Using FastAPI Docs
1. Start the server: `uvicorn app.main:app --reload`
2. Open http://localhost:8000/docs
3. Use the "Authorize" button to login
4. Test protected endpoints with the authenticated session

### Using Python
```python
import requests

# Register
response = requests.post(
    "http://localhost:8000/api/auth/register",
    json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123"
    }
)
print(response.json())

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login/json",
    json={
        "username": "testuser",
        "password": "SecurePass123"
    }
)
token = response.json()["access_token"]

# Access protected endpoint
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "http://localhost:8000/decks",
    headers=headers,
    json={
        "name": "My Deck",
        "format": "Standard",
        "colors": ["U", "B"]
    }
)
print(response.json())
```

## Future Enhancements

Potential improvements for the authentication system:

1. Refresh tokens for extended sessions
2. Password reset functionality
3. Email verification
4. OAuth2 integration (Google, GitHub, etc.)
5. Rate limiting for login attempts
6. User-specific deck ownership
7. Two-factor authentication
8. Session management
