# Event Management System

A full-stack event management system that parses unstructured event text into structured calendar events, detects conflicts, and manages event lifecycles.

## Architecture

- **Backend**: FastAPI with async architecture and JSON file storage
- **Frontend**: Next.js 14 with Tailwind CSS
- **Infrastructure**: Docker Compose for local development

## Project Structure

```
event-management-system/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI application
│   │   ├── models.py       # Data models
│   │   ├── services.py     # Business logic
│   │   └── api/
│   │       ├── __init__.py
│   │       └── routes.py   # API endpoints
│   ├── data/               # JSON file storage
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx    # Homepage
│   │   │   └── layout.tsx  # Root layout
│   │   ├── components/     # React components
│   │   ├── lib/           # Utilities and API client
│   │   └── types/         # TypeScript types
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml      # Local development setup
└── README.md
```

## Features

- **Event Parsing**: Convert unstructured text to structured events
- **Conflict Detection**: Identify scheduling conflicts
- **Event Lifecycle Management**: Create, update, delete events
- **JSON Storage**: Simple file-based data persistence
- **Modern UI**: Clean, responsive interface with Tailwind CSS

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd event-management-system
   ```

2. **Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/events` - List all events
- `POST /api/events` - Create new event
- `PUT /api/events/{id}` - Update event
- `DELETE /api/events/{id}` - Delete event
- `POST /api/events/parse` - Parse unstructured event text

## Technologies Used

- **Backend**: FastAPI, Pydantic, Uvicorn
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Infrastructure**: Docker, Docker Compose
- **Storage**: JSON files (for simplicity)

## Next Steps

This foundation is ready for implementing:
- Natural language event parsing
- Conflict detection algorithms
- Advanced event management features
- Real-time updates
- User authentication 