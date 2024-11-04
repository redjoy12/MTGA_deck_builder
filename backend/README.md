# MTGA AI Deck Builder - Development Status & Implementation Plan

## Current Progress (Completed Items)

### 1. Project Structure Setup ✓
```
mtga-ai-deckbuilder/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   ├── tests/
│   ├── data/
│   ├── requirements.txt
│   └── .env
├── frontend/
└── .gitignore
```

### 2. Environment Configuration ✓
- Virtual environment setup
- Dependencies installation
- Environment variables configuration
- Basic FastAPI application setup

### 3. Initial Dependencies ✓
```python
# Core dependencies configured and installed:
fastapi==0.109.1
uvicorn==0.27.0
langchain==0.0.352
langgraph==0.0.25
anthropic==0.9.1
langchain-community==0.0.19
langsmith==0.0.83
# ... (other dependencies)
```

## Next Steps (To Be Implemented)

### 1. Database Setup and Configuration
```python
# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost:5432/mtga_deckbuilder"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

#### 1.1 Database Models
```python
# backend/app/models/card.py
from sqlalchemy import Column, Integer, String, Float, JSON
from app.core.database import Base

class Card(Base):
    __tablename__ = "cards"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    mana_cost = Column(String)
    cmc = Column(Float)
    colors = Column(JSON)
    type_line = Column(String)
    oracle_text = Column(String)
    power = Column(String)
    toughness = Column(String)
    rarity = Column(String)
    set_code = Column(String)
    vector_embedding = Column(JSON)  # Store as JSON initially, migrate to proper vector type later
```

#### 1.2 Database Migrations
```bash
# Set up Alembic for migrations
alembic init alembic
```

### 2. Scryfall Integration Service
```python
# backend/app/services/scryfall.py
import aiohttp
from typing import List, Dict, Any

class ScryfallService:
    BASE_URL = "https://api.scryfall.com"
    
    async def get_card(self, card_id: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/cards/{card_id}") as response:
                return await response.json()
    
    async def search_cards(self, query: str) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/cards/search",
                params={"q": query}
            ) as response:
                data = await response.json()
                return data.get("data", [])
```

### 3. Agent System Implementation

#### 3.1 Base Agent Class
```python
# backend/app/core/agents/base.py
from langchain.chat_models import ChatAnthropic
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, llm: ChatAnthropic):
        self.llm = llm
    
    @abstractmethod
    async def process(self, input_data: dict) -> dict:
        pass
```

#### 3.2 Specialized Agents
```python
# backend/app/core/agents/
├── input_processor.py
├── card_analyzer.py
├── deck_constructor.py
├── strategy_analyzer.py
└── recommendation_engine.py
```

#### 3.3 Agent Orchestrator
```python
# backend/app/core/orchestrator.py
from langgraph.graph import Graph
from app.core.agents import *

class AgentOrchestrator:
    def __init__(self):
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> Graph:
        # Initialize all agents
        # Create graph
        # Define edges
        # Return configured workflow
        pass
```

### 4. API Endpoints Implementation

#### 4.1 Card Management
```python
# backend/app/api/endpoints/cards.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

@router.get("/cards/", response_model=List[CardResponse])
async def list_cards(
    session: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    pass

@router.get("/cards/{card_id}", response_model=CardResponse)
async def get_card(card_id: str, session: Session = Depends(get_db)):
    pass
```

#### 4.2 Deck Building
```python
# backend/app/api/endpoints/decks.py
@router.post("/decks/analyze")
async def analyze_deck(deck: DeckInput):
    pass

@router.post("/decks/build")
async def build_deck(requirements: DeckRequirements):
    pass
```

#### 4.3 Streaming Responses
```python
# backend/app/api/endpoints/stream.py
@router.websocket("/ws/deck-builder")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Process with agent system
        response = await process_deck_request(data)
        await websocket.send_text(response)
```

### 5. Frontend Development

#### 5.1 Project Setup
```bash
# Create React application
npx create-react-app frontend --template typescript
cd frontend
npm install @tailwindcss/forms @headlessui/react socket.io-client
```

#### 5.2 Key Components
```typescript
// frontend/src/components/
├── Chat/
│   ├── ChatInterface.tsx
│   ├── MessageList.tsx
│   └── MessageInput.tsx
├── DeckBuilder/
│   ├── DeckView.tsx
│   ├── CardList.tsx
│   └── ManaCurve.tsx
├── Analysis/
│   ├── DeckAnalysis.tsx
│   └── Recommendations.tsx
└── shared/
    ├── Card.tsx
    └── Loading.tsx
```

### 6. Testing Implementation

#### 6.1 Backend Tests
```python
# backend/tests/
├── conftest.py
├── test_api/
├── test_agents/
└── test_services/
```

#### 6.2 Frontend Tests
```typescript
// frontend/src/tests/
├── components/
└── integration/
```

### 7. Deployment Configuration

#### 7.1 Docker Setup
```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 7.2 Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: mtga_deckbuilder
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
  
  redis:
    image: redis:6
```

## Immediate Next Actions

1. **Database Setup**
   - [ ] Configure PostgreSQL connection
   - [ ] Create initial models
   - [ ] Set up migrations
   - [ ] Implement CRUD operations

2. **Scryfall Integration**
   - [ ] Implement card fetching
   - [ ] Set up data synchronization
   - [ ] Create caching layer

3. **Agent System**
   - [ ] Implement base agent class
   - [ ] Create specialized agents
   - [ ] Set up agent workflow
   - [ ] Configure Claude integration

4. **API Development**
   - [ ] Implement card endpoints
   - [ ] Create deck building endpoints
   - [ ] Set up WebSocket connection
   - [ ] Add authentication

## Project Timeline

1. **Week 1 (Current)**
   - Complete database setup
   - Implement Scryfall integration
   - Create basic agent structure

2. **Week 2**
   - Implement all agents
   - Set up agent workflow
   - Create API endpoints

3. **Week 3**
   - Start frontend development
   - Implement core components
   - Set up WebSocket connection

4. **Week 4**
   - Complete frontend features
   - Add tests
   - Deploy initial version

## Development Guidelines

1. **Code Style**
   - Follow PEP 8 for Python code
   - Use ESLint/Prettier for TypeScript
   - Document all functions and classes

2. **Git Workflow**
   - Create feature branches
   - Use conventional commits
   - Require PR reviews

3. **Testing Requirements**
   - Unit tests for all agents
   - API endpoint testing
   - Frontend component testing
   - Integration tests

4. **Documentation**
   - Update API documentation
   - Maintain README
   - Document deployment process

Would you like to focus on implementing any specific part from the next steps? We can start with:
1. Setting up the database and models
2. Implementing the Scryfall integration
3. Creating the base agent structure
4. Starting the frontend setup

Let me know which area you'd like to tackle first!
