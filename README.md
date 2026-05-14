# 朝読み (Asayomi)

日本ニュース自動収集・AI分析システム

## 機能

- 📰 定時RSS収集（NHK、Yahoo!ニュース、ITmedia、Gigazine、東洋経済、Reuters Japan）
- 🤖 Azure OpenAI による要約・分類・重要度スコアリング
- 📋 毎日ブリーフィング自動生成
- 🌐 全日本語Web UI（React + Ant Design）
- 🗑️ 30日自動データクリーンアップ

## 技術スタック

- **バックエンド**: Python + FastAPI + SQLAlchemy + SQLite
- **フロントエンド**: React + TypeScript + Vite + Ant Design
- **AI**: Azure OpenAI (GPT-4o-mini)
- **スケジューラ**: APScheduler

## セットアップ

### バックエンド

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Azure OpenAI キーを設定
uvicorn app.main:app --reload
```

### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

## 運用コマンド

```bash
# 手動収集
cd backend && python -m app.services.data_collector

# AI処理
cd backend && python -m app.services.ai_processor

# ブリーフィング生成
cd backend && python -m app.services.briefing
```

## API

- `GET /api/v1/articles` - 記事一覧
- `GET /api/v1/briefings?date=YYYY-MM-DD` - ブリーフィング
- `GET /api/v1/stats` - 統計
- `POST /api/v1/system/collect` - 手動収集トリガー
- `POST /api/v1/system/process` - AI処理トリガー

## ライセンス

MIT
