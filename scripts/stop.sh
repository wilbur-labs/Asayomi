#!/bin/bash
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🛑 Stopping Asayomi..."

for pidfile in "$PROJECT_ROOT/logs/backend.pid" "$PROJECT_ROOT/logs/frontend.pid"; do
  if [ -f "$pidfile" ]; then
    pid=$(cat "$pidfile")
    kill "$pid" 2>/dev/null && echo "Stopped PID $pid"
    rm -f "$pidfile"
  fi
done

echo "✅ Done"
