"""Azure OpenAI による記事処理サービス"""
import json
import logging
from typing import Optional

from openai import AzureOpenAI
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import SessionLocal
from ..models.article import Article

logger = logging.getLogger(__name__)

CATEGORIES = ["総合", "テクノロジー", "経済・ビジネス", "国際"]

SYSTEM_PROMPT = """あなたは日本のニュース分析アシスタントです。以下のタスクを実行してください：
1. 記事の日本語要約（100文字以内）
2. カテゴリ分類（総合/テクノロジー/経済・ビジネス/国際）
3. 重要度スコア（0-10、10が最重要）
4. タグ（カンマ区切り、最大3つ）

JSON形式で回答してください：
{"summary": "...", "category": "...", "score": 7, "tags": "タグ1,タグ2"}"""


def get_client() -> Optional[AzureOpenAI]:
    if not settings.azure_openai_api_key or not settings.azure_openai_endpoint:
        return None
    return AzureOpenAI(
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        azure_endpoint=settings.azure_openai_endpoint,
    )


def process_article(client: AzureOpenAI, article: Article) -> bool:
    """1記事をAI処理"""
    try:
        content = f"タイトル: {article.title}\n内容: {article.original_content or ''}"
        response = client.chat.completions.create(
            model=settings.azure_openai_deployment_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content[:2000]},
            ],
            temperature=0.3,
            max_tokens=300,
        )
        result = json.loads(response.choices[0].message.content)
        article.summary = result.get("summary", "")
        article.category = result.get("category", article.category)
        article.importance_score = float(result.get("score", 5))
        article.tags = result.get("tags", "")
        article.processed = True
        return True
    except Exception as e:
        logger.error(f"AI処理エラー [{article.title[:30]}]: {e}")
        return False


def process_unprocessed(limit: int = 20) -> int:
    """未処理記事をバッチ処理"""
    client = get_client()
    if not client:
        logger.warning("Azure OpenAI 未設定。スキップします。")
        return 0

    db = SessionLocal()
    try:
        articles = db.query(Article).filter(Article.processed == False).limit(limit).all()
        count = 0
        for article in articles:
            if process_article(client, article):
                count += 1
        db.commit()
        logger.info(f"AI処理完了: {count}/{len(articles)} 件")
        return count
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    process_unprocessed()
