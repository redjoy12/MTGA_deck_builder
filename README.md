# MTGA AI Deck Builder

The MTGA AI Deck Builder is an advanced web application that uses AI and large language models to create optimized Magic: The Gathering Arena decks. It combines AI-powered recommendations with deep game knowledge to offer personalized deck building, strategic insights, and interactive deck management features.

## Table of Contents
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Features

- **AI-Powered Deck Generation**: Leverage LangChain and LLMs to generate optimized decks based on strategy and preferences
- **Interactive Deck Builder**: Intuitive Angular interface for creating and managing decks
- **Card Search & Filtering**: Search cards by name, color, type, and other attributes
- **Deck Analysis**: Get strategic insights and recommendations for your decks
- **User Authentication**: Secure JWT-based authentication system
- **State Management**: NgRx for predictable state management on the frontend
- **Real-time Updates**: Efficient data synchronization between frontend and backend
- **Resource Management**: Track wildcards, gold, and gems
- **Deck History**: Save and manage multiple deck configurations

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis
- **AI/LLM**: LangChain, LangGraph, LangSmith, Groq
- **Authentication**: JWT with bcrypt password hashing
- **Migrations**: Alembic

### Frontend
- **Framework**: Angular 18
- **UI Components**: Angular Material, PrimeNG
- **State Management**: NgRx with Effects
- **Charts**: Chart.js
- **Styling**: SCSS
- **Testing**: Jasmine & Karma

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **PostgreSQL**: 13 or higher
- **Redis**: 6 or higher (optional, for caching)
- **npm**: 9 or higher
- **Angular CLI**: 18 or higher

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/redjoy12/MTGA_deck_builder.git
cd MTGA_deck_builder
```

### 2. Backend Setup

#### a. Create and activate a virtual environment

```bash
cd backend
python -m venv venv

# On Linux/macOS
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

#### b. Install Python dependencies

```bash
pip install -r requirements.txt
```

#### c. Configure environment variables

Edit the `.env` file in the `backend` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/mtga_deckbuilder
POSTGRES_SERVER=localhost
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=mtga_deckbuilder
POSTGRES_PORT=5432

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# AI Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Security
SECRET_KEY=your-secure-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
ENVIRONMENT=development
```

#### d. Set up the database

```bash
# Create the PostgreSQL database
createdb mtga_deckbuilder

# Run database migrations
alembic upgrade head

# (Optional) Initialize with sample data
python init_db.py
```

### 3. Frontend Setup

#### a. Navigate to frontend directory

```bash
cd ../frontend/mtga-deck-builder
```

#### b. Install Node dependencies

```bash
npm install
```

#### c. Configure API endpoint (optional)

If your backend runs on a different host/port, update `proxy.conf.json`:

```json
{
  "/api": {
    "target": "http://localhost:8000",
    "secure": false
  }
}
```

## Usage

### Starting the Application

#### 1. Start the Backend Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at: `http://localhost:8000`

#### 2. Start the Frontend Development Server

In a new terminal:

```bash
cd frontend/mtga-deck-builder
npm start
```

The frontend will be available at: `http://localhost:4200`

### First-Time User Setup

#### 1. Register a new account

Navigate to `http://localhost:4200` and create a new account, or use the API directly:

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "yourname",
    "email": "your@email.com",
    "password": "SecurePass123"
  }'
```

#### 2. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "yourname",
    "password": "SecurePass123"
  }'
```

You'll receive a JWT token:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 3. Use the Application

- Browse and search for Magic cards
- Create new decks using the deck builder
- Use AI-powered suggestions to optimize your decks
- Save and manage multiple deck configurations
- Analyze deck strategies and get recommendations

## API Documentation

### Interactive API Docs

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login (OAuth2 form data)
- `POST /api/auth/login/json` - Login (JSON)
- `GET /api/auth/me` - Get current user info

#### Cards
- `GET /cards` - List all cards
- `GET /cards/{card_id}` - Get card details
- `GET /cards/search` - Search cards

#### Decks
- `GET /decks` - List decks (public)
- `POST /decks` - Create new deck (requires auth)
- `GET /decks/{deck_id}` - Get deck details
- `PUT /decks/{deck_id}` - Update deck (requires auth)
- `DELETE /decks/{deck_id}` - Delete deck (requires auth)
- `POST /api/decks/generate` - Generate deck with AI (requires auth)

### Example: Creating a Deck with Authentication

```bash
# First, login to get a token
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{"username": "yourname", "password": "SecurePass123"}' \
  | jq -r '.access_token')

# Create a deck
curl -X POST "http://localhost:8000/decks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Azorius Control",
    "format": "Standard",
    "colors": ["W", "U"],
    "strategy": "control"
  }'
```

## Project Structure

```
MTGA_deck_builder/
├── backend/                    # Python/FastAPI backend
│   ├── alembic/               # Database migrations
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core functionality (auth, config)
│   │   ├── models/            # SQLAlchemy models
│   │   ├── routes/            # API routes
│   │   ├── services/          # Business logic
│   │   └── main.py           # FastAPI application entry point
│   ├── tests/                # Backend tests
│   ├── .env                  # Environment variables
│   ├── requirements.txt      # Python dependencies
│   └── README.md            # Backend documentation
│
├── frontend/                   # Angular frontend
│   └── mtga-deck-builder/
│       ├── src/
│       │   ├── app/
│       │   │   ├── core/     # Core services, guards
│       │   │   ├── features/ # Feature modules
│       │   │   ├── shared/   # Shared components
│       │   │   └── store/    # NgRx state management
│       │   ├── assets/       # Static assets
│       │   └── environments/ # Environment configs
│       ├── package.json      # Node dependencies
│       └── angular.json      # Angular configuration
│
├── .gitignore
├── LICENSE
└── README.md                  # This file
```

## Development

### Running Tests

#### Backend Tests
```bash
cd backend
pytest tests/ -v
```

#### Frontend Tests
```bash
cd frontend/mtga-deck-builder
npm test
```

### Code Quality

#### Backend Linting
```bash
cd backend
pylint app/
```

#### Frontend Linting
```bash
cd frontend/mtga-deck-builder
ng lint
```

### Database Migrations

#### Create a new migration
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

#### Apply migrations
```bash
alembic upgrade head
```

#### Rollback migration
```bash
alembic downgrade -1
```

### Building for Production

#### Backend
```bash
cd backend
# Set environment variables for production
export ENVIRONMENT=production
export DEBUG=False
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend/mtga-deck-builder
ng build --configuration production
```

The production build will be in `dist/mtga-deck-builder/`.

## Environment Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `ANTHROPIC_API_KEY` | Anthropic API key for AI features | - |
| `SECRET_KEY` | JWT secret key | - |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |
| `DEBUG` | Debug mode | False |
| `ENVIRONMENT` | Environment name | production |

### Frontend Environment Configuration

Edit `src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',
  wsUrl: 'ws://localhost:8000'
};
```

## Authentication

The application uses JWT (JSON Web Token) based authentication. See [backend/AUTHENTICATION.md](backend/AUTHENTICATION.md) for detailed information about:

- Password requirements
- Token management
- Protected endpoints
- Security features

## Troubleshooting

### Common Issues

**Database connection error:**
- Ensure PostgreSQL is running: `sudo systemctl status postgresql`
- Check database credentials in `.env`
- Verify database exists: `psql -l`

**Frontend proxy issues:**
- Check `proxy.conf.json` configuration
- Ensure backend is running on the correct port
- Clear browser cache and restart dev server

**Module import errors:**
- Backend: Reinstall dependencies: `pip install -r requirements.txt`
- Frontend: Delete `node_modules` and run `npm install`

**Migration errors:**
- Check database connection
- Review migration files in `backend/alembic/versions/`
- Try: `alembic downgrade -1` then `alembic upgrade head`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use Angular style guide for TypeScript
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Magic: The Gathering and MTGA are property of Wizards of the Coast
- Card data provided by Scryfall API
- AI powered by Anthropic Claude and LangChain

## Support

For issues, questions, or contributions, please:
- Open an issue on GitHub
- Check existing documentation in `backend/README.md` and `frontend/mtga-deckbuilder-readme.md`
- Review the API documentation at http://localhost:8000/docs

---

Built with passion for Magic: The Gathering Arena players
