#!/usr/bin/env bash
# Asayomi データベース 復元スクリプト
# 使い方: ./scripts/restore.sh backups/asayomi_YYYYMMDD_HHMMSS.db
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "使い方: $0 <バックアップファイル.db>"
    echo ""
    echo "利用可能なバックアップ:"
    ls -lht "$(dirname "$0")/../backups/"*.db 2>/dev/null || echo "  なし"
    exit 1
fi

BACKUP_FILE="$1"
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ ファイルが見つかりません: $BACKUP_FILE"
    exit 1
fi

cd "$(dirname "$0")/.."
ROOT=$(pwd)
TS=$(date +%Y%m%d_%H%M%S)

echo "⚠️  現在の DB を data/asayomi.db.before_$TS にバックアップしてから復元します"
read -p "続行しますか? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "キャンセルしました"
    exit 0
fi

echo "▶ バックエンドを停止..."
docker compose stop backend

echo "▶ 現在の DB を退避..."
sudo cp "$ROOT/data/asayomi.db" "$ROOT/data/asayomi.db.before_$TS" 2>/dev/null || true
sudo rm -f "$ROOT/data/asayomi.db-wal" "$ROOT/data/asayomi.db-shm"

echo "▶ バックアップから復元..."
sudo cp "$BACKUP_FILE" "$ROOT/data/asayomi.db"
sudo chown root:root "$ROOT/data/asayomi.db"

echo "▶ バックエンドを再起動..."
docker compose start backend

sleep 2
echo ""
echo "✅ 復元完了"
sqlite3 "$ROOT/data/asayomi.db" "SELECT COUNT(*) FROM articles;" 2>&1 | head -3
