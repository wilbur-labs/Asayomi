#!/bin/bash
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "📊 Asayomi Status"
echo "=================="

for name in backend frontend; do
  pidfile="$PROJECT_ROOT/logs/${name}.pid"
  if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
    echo "✅ $name: running (PID $(cat "$pidfile"))"
  else
    echo "❌ $name: stopped"
  fi
done
