# Event Management System - Project Summary

## 🎯 Project Overview

A complete full-stack event management system that parses unstructured event text into structured calendar events, detects conflicts, and manages event lifecycles. Built for a 2-3 hour coding challenge focusing on architecture and product thinking.

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async architecture
- **Storage**: JSON file-based storage (no database required)
- **Features**:
  - RESTful API with automatic OpenAPI documentation
  - Natural language event parsing
  - Conflict detection
  - Full CRUD operations for events
  - CORS enabled for frontend communication
  - Health check endpoints

### Frontend (Next.js 14)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom components
- **Features**:
  - Modern, responsive UI
  - Real-time event parsing interface
  - Event management dashboard
  - TypeScript for type safety
  - API client with error handling

### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose for local development
- **Networking**: Custom bridge network for service communication

## 📁 Project Structure

```
event-management-system/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI application entry point
│   │   ├── models.py       # Pydantic data models
│   │   ├── services.py     # Business logic & JSON storage
│   │   └── api/
│   │       ├── __init__.py
│   │       └── routes.py   # API endpoints
│   ├── data/               # JSON file storage
│   │   └── .gitkeep
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Backend container
│   └── test_main.py       # API test script
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx    # Homepage component
│   │   │   ├── layout.tsx  # Root layout
│   │   │   └── globals.css # Global styles
│   │   ├── components/     # React components
│   │   │   ├── EventCard.tsx
│   │   │   └── EventParser.tsx
│   │   ├── lib/           # Utilities
│   │   │   └── api.ts     # API client
│   │   └── types/         # TypeScript types
│   │       └── event.ts
│   ├── package.json       # Node.js dependencies
│   ├── tailwind.config.js # Tailwind configuration
│   ├── next.config.js     # Next.js configuration
│   ├── tsconfig.json      # TypeScript configuration
│   └── Dockerfile         # Frontend container
├── scripts/               # Development scripts
│   ├── setup.sh          # Dependency installation
│   └── dev.sh            # Development server startup
├── docker-compose.yml     # Service orchestration
├── .gitignore            # Git ignore rules
├── README.md             # Project documentation
└── PROJECT_SUMMARY.md    # This file
```

## 🚀 Key Features Implemented

### 1. Natural Language Event Parsing
- Parses unstructured text like "Chuck's soccer game moved to Thursday at 3:30pm"
- Supports multiple date/time formats
- Handles relative dates (tomorrow, next week, day names)
- Extracts event title, time, and date automatically

### 2. Conflict Detection
- Identifies scheduling conflicts between events
- Time overlap detection
- Returns detailed conflict information
- Prevents creation of conflicting events

### 3. Event Management
- Full CRUD operations (Create, Read, Update, Delete)
- Event status tracking (scheduled, cancelled, completed)
- Priority levels (low, medium, high)
- Location and description support

### 4. Modern UI/UX
- Clean, responsive design with Tailwind CSS
- Real-time event parsing interface
- Event cards with visual indicators
- Loading states and error handling
- Mobile-friendly layout

## 📦 Dependencies

### Backend Dependencies
- `fastapi==0.104.1` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `pydantic==2.5.0` - Data validation
- `python-multipart==0.0.6` - Form data handling
- `python-dateutil==2.8.2` - Date parsing utilities

### Frontend Dependencies
- `next==14.0.4` - React framework
- `react==^18` - UI library
- `axios==^1.6.2` - HTTP client
- `date-fns==^2.30.0` - Date utilities
- `lucide-react==^0.294.0` - Icons
- `tailwindcss==^3.3.0` - CSS framework

## 🛠️ Running the Project

### Option 1: Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development
```bash
# Setup dependencies
./scripts/setup.sh

# Start development servers
./scripts/dev.sh
```

### Option 3: Manual Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (in new terminal)
cd frontend
npm install
npm run dev
```

## 🧪 Testing

### Backend API Testing
```bash
cd backend
python test_main.py
```

### Manual Testing
1. **Event Parsing**: Try entering "Team meeting tomorrow at 2pm" in the parser
2. **Conflict Detection**: Create overlapping events to see conflict detection
3. **CRUD Operations**: Create, edit, and delete events through the UI

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/events` | List all events |
| GET | `/api/events/{id}` | Get specific event |
| POST | `/api/events` | Create new event |
| PUT | `/api/events/{id}` | Update event |
| DELETE | `/api/events/{id}` | Delete event |
| POST | `/api/events/parse` | Parse unstructured text |
| POST | `/api/events/parse-and-create` | Parse and create events |

## 🎨 UI Components

### EventCard
- Displays event details with icons
- Shows priority and status badges
- Edit and delete actions
- Responsive design

### EventParser
- Text input for unstructured events
- Real-time parsing results
- Conflict detection display
- One-click event creation

## 🔧 Configuration

### Environment Variables
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000)
- `PYTHONUNBUFFERED` - Python output buffering (set to 1 for Docker)

### Ports
- Frontend: 3000
- Backend: 8000

## 🚀 Deployment Ready

The project is structured for easy deployment:
- Docker containers are production-ready
- Environment variables are configurable
- Health checks are implemented
- CORS is properly configured
- Static file serving is optimized

## 🔮 Future Enhancements

This foundation is ready for:
- **Advanced NLP**: Integration with spaCy or cloud NLP services
- **Real-time Updates**: WebSocket integration
- **User Authentication**: JWT-based auth system
- **Database Integration**: PostgreSQL or MongoDB
- **Calendar Integration**: Google Calendar, Outlook APIs
- **Mobile App**: React Native or Flutter
- **Advanced Conflict Resolution**: AI-powered suggestions

## 📊 Performance Considerations

- **Backend**: Async FastAPI for high concurrency
- **Frontend**: Next.js optimization and code splitting
- **Storage**: JSON files for simplicity (can be replaced with database)
- **Caching**: Ready for Redis integration
- **Monitoring**: Health checks and logging in place

## 🎯 Architecture Highlights

1. **Separation of Concerns**: Clear separation between UI, API, and business logic
2. **Type Safety**: Full TypeScript and Pydantic validation
3. **Extensibility**: Modular design for easy feature additions
4. **Developer Experience**: Hot reload, automatic API docs, comprehensive tooling
5. **Production Ready**: Docker, health checks, proper error handling

This implementation demonstrates modern full-stack development practices with a focus on clean architecture, extensibility, and developer experience. 