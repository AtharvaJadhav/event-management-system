# Event Management System

A full-stack, AI-powered event management system that parses unstructured event text, detects conflicts, and manages your calendar in real time.

## Features

- **LLM-Powered Parsing:** Converts natural language (emails, texts, etc.) into structured events using OpenAI GPT-3.5-turbo.
- **Smart Date Handling:** The system interprets 'today' and other relative dates as your real current date, so events are always scheduled relative to when you use the app.
- **Conflict Detection:** Prevents double-booking and highlights scheduling conflicts.
- **Async Streaming:** Simulates real-time event ingestion (like emails/SMS) with a streaming processor.
- **Modern UI:** Built with Next.js 14 and Tailwind CSS for a beautiful, responsive experience.
- **Live System Stats:** See total events, recent creations, and more in real time.

## Tech Stack
- **Backend:** FastAPI, Python, OpenAI API
- **Frontend:** Next.js 14, React, Tailwind CSS
- **Persistence:** JSON file storage (easy to demo, no DB required)

## How to Run

1. **Clone the repo:**
   ```sh
   git clone <your-repo-url>
   cd event-management-system
   ```
2. **Set up OpenAI API Key:**
   - Create a `.env` file in the project root:
     ```env
     OPENAI_API_KEY=sk-...
     ```
3. **Start the backend:**
   ```sh
   cd backend
   python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. **Start the frontend:**
   ```sh
   cd frontend
   npm install
   npm run dev
   ```
5. **Open the app:**
   - Go to [http://localhost:3000](http://localhost:3000)

## Demo Flow

1. **Try the Event Parser:**
   - Enter text like `Meeting today at 2pm` or `Lunch with Sarah Friday noon` and click **Parse Events**.
   - **Note:** The system will interpret 'today' as the real current date, so events are always scheduled relative to your system clock.
   - The system will use AI to extract event details and check for conflicts.
2. **Start Stream Processing:**
   - Click **Start Processing** in the Stream Processing card.
   - Watch as the system ingests a stream of realistic event messages in real time, parsing and creating events automatically.
3. **See Live Stats:**
   - Check the System Stats card for total events, recent creations, and more.
4. **Spot Conflicts & Highlights:**
   - Conflicting events are flagged, and newly created events are highlighted for 30 seconds.
5. **Delete Events:**
   - Use the trash icon to remove events instantly.

---

**Built for demo impact.** 