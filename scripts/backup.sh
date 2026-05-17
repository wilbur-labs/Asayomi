#!/usr/bin/env bash
# Asayomi データベース バックアップスクリプト
# 使い方: ./scripts/backup.sh
set -euo pipefail

cd "$(dirname "$0")/.."
ROOT=$(pwd)
TS=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$ROOT/backups"
mkdir -p "$BACKUP_DIR"

echo "▶ WAL を主データベースにマージします..."
if docker ps --format '{{.Names}}' | grep -q '^asayomi-backend$'; then
    docker exec asayomi-backend python -c "
from app.core.database import engine
from sqlalchemy import text
with engine.begin() as conn:
    conn.execute(text('PRAGMA wal_checkpoint(TRUNCATE)'))
print('checkpoint OK')
" || echo "  (スキップ: コンテナ内 checkpoint 失敗、ファイルコピーで継続)"
else
    echo "  (バックエンドが停止中、そのままコピーします)"
fi

DB_BAK="$BACKUP_DIR/asayomi_$TS.db"
TAR_BAK="$BACKUP_DIR/asayomi_full_$TS.tar.gz"

echo "▶ DB をコピー..."
sudo cp "$ROOT/data/asayomi.db" "$DB_BAK"
sudo chown "$USER:$USER" "$DB_BAK"

echo "▶ DB + 設定をパッケージ化..."
sudo tar czf "$TAR_BAK" \
    -C "$ROOT" \
    data/asayomi.db \
    .env \
    backend/.env 2>/dev/null || true
sudo chown "$USER:$USER" "$TAR_BAK"

echo ""
echo "✅ バックアップ完了"
echo "   $DB_BAK"
echo "   $TAR_BAK"
echo ""
echo "📊 内容確認:"
sqlite3 "$DB_BAK" "SELECT COUNT(*) AS articles, SUM(CASE WHEN summary IS NOT NULL THEN 1 ELSE 0 END) AS with_summary, SUM(CASE WHEN key_points IS NOT NULL THEN 1 ELSE 0 END) AS with_keypoints FROM articles;" -header -column

echo ""
echo "💾 既存バックアップ:"
ls -lht "$BACKUP_DIR" | head -10
