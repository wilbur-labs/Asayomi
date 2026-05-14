#!/bin/bash
set -e
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$PROJECT_ROOT/logs"

echo "🚀 Starting Asayomi..."

# Backend
cd "$PROJECT_ROOT/backend"
if [ ! -d "venv" ]; then
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
else
  source venv/bin/activate
fi

uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$PROJECT_ROOT/logs/backend.log" 2>&1 &
echo $! > "$PROJECT_ROOT/logs/backend.pid"
echo "✅ Backend started (PID: $(cat $PROJECT_ROOT/logs/backend.pid))"

# Frontend
cd "$PROJECT_ROOT/frontend"
[ ! -d "node_modules" ] && npm install
npm run dev > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
echo $! > "$PROJECT_ROOT/logs/frontend.pid"
echo "✅ Frontend started (PID: $(cat $PROJECT_ROOT/logs/frontend.pid))"

echo ""
echo "📍 Frontend: http://localhost:5173"
echo "📍 Backend:  http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
