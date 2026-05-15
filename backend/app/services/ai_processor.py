"""Azure OpenAI による記事処理サービス（要約・分類・スコア・翻訳）"""
import json
import logging
from typing import Optional

from openai import AzureOpenAI
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import SessionLocal
from ..models.article import Article
from ..utils.tags import normalize_tag_string

logger = logging.getLogger(__name__)

CATEGORIES = ["総合", "テクノロジー", "経済・ビジネス", "国際"]

SYSTEM_PROMPT_JA = """あなたは日本のニュース分析アシスタントです。日本語の記事を分析し、JSON で回答してください：
- summary: 100文字以内の日本語要約
- category: 「総合」「テクノロジー」「経済・ビジネス」「国際」のいずれか
- score: 0-10 の重要度（10が最重要）
- tags: カンマ区切りで最大3つの日本語タグ

形式: {"summary": "...", "category": "...", "score": 7, "tags": "タグ1,タグ2,タグ3"}"""

SYSTEM_PROMPT_EN = """あなたは英日翻訳・ニュース分析アシスタントです。英語の記事を読み、JSON で回答してください：
- translated_title: 英語タイトルの自然な日本語訳
- summary: 100文字以内の日本語要約
- category: 「総合」「テクノロジー」「経済・ビジネス」「国際」のいずれか
- score: 0-10 の重要度（10が最重要）
- tags: カンマ区切りで最大3つの日本語タグ

形式: {"translated_title": "...", "summary": "...", "category": "...", "score": 7, "tags": "タグ1,タグ2,タグ3"}"""


def get_client() -> Optional[AzureOpenAI]:
    if not settings.azure_openai_api_key or not settings.azure_openai_endpoint:
        return None
    return AzureOpenAI(
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        azure_endpoint=settings.azure_openai_endpoint,
    )


def _build_user_content(article: Article) -> str:
    body = article.full_content or article.original_content or ""
    return f"タイトル: {article.original_title or article.title}\n本文:\n{body[:4000]}"


def process_article(client: AzureOpenAI, article: Article) -> bool:
    """1記事をAI処理。英語記事は日本語に翻訳。"""
    is_english = article.language == "en"
    system_prompt = SYSTEM_PROMPT_EN if is_english else SYSTEM_PROMPT_JA

    try:
        response = client.chat.completions.create(
            model=settings.azure_openai_deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": _build_user_content(article)},
            ],
            temperature=0.3,
            max_tokens=400,
            response_format={"type": "json_object"},
        )
        # 用量記録
        try:
            from .usage import record_usage
            usage = response.usage
            if usage:
                record_usage(
                    operation="translate" if is_english else "summarize",
                    model=settings.azure_openai_deployment_name,
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                )
        except Exception:
            pass
        result = json.loads(response.choices[0].message.content)
        if is_english and result.get("translated_title"):
            article.title = result["translated_title"]  # 表示用を翻訳後に更新
        article.summary = result.get("summary", "")
        article.category = result.get("category", article.category)
        article.importance_score = float(result.get("score", 5))
        article.tags = normalize_tag_string(result.get("tags", ""))
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
        articles = (
            db.query(Article)
            .filter(Article.processed == False, Article.is_duplicate == False)
            .order_by(Article.collected_at.desc())
            .limit(limit)
            .all()
        )
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
