"""Azure OpenAI による記事処理サービス（要約・分類・スコア・翻訳）"""
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

# AI が返す可能性のあるカテゴリを正規の4カテゴリに正規化
CATEGORY_MAP = {
    "総合": "総合",
    "テクノロジー": "テクノロジー",
    "経済・ビジネス": "経済・ビジネス",
    "国際": "国際",
    "サイエンス": "テクノロジー",
    "科学": "テクノロジー",
    "IT": "テクノロジー",
    "スポーツ": "総合",
    "ライフ": "総合",
    "生活": "総合",
    "エンタメ": "総合",
    "芸能": "総合",
    "文化": "総合",
    "文化・芸術": "総合",
    "教育": "総合",
    "教育・キャリア": "総合",
    "医療・健康": "総合",
    "事件・事故": "総合",
    "社会": "総合",
    "政治": "総合",
    "経済": "経済・ビジネス",
    "ビジネス": "経済・ビジネス",
    "金融": "経済・ビジネス",
    "海外": "国際",
    "世界": "国際",
}


def normalize_category(cat: str) -> str:
    """AI が返したカテゴリを正規の4カテゴリに正規化"""
    if cat in CATEGORIES:
        return cat
    return CATEGORY_MAP.get(cat, "総合")

SYSTEM_PROMPT_JA = """あなたは日本のニュース分析アシスタントです。日本語の記事を分析し、JSON で回答してください：
- summary: 100文字以内の日本語要約
- key_points: 記事の要点を 3〜5 個、各 30 文字程度の簡潔な日本語の箇条書き（配列）
- category: 「総合」「テクノロジー」「経済・ビジネス」「国際」のいずれか
- score: 0-10 の重要度（10が最重要）
- tags: カンマ区切りで最大3つの日本語タグ

形式: {"summary": "...", "key_points": ["...", "...", "..."], "category": "...", "score": 7, "tags": "タグ1,タグ2,タグ3"}"""

SYSTEM_PROMPT_EN = """あなたは英日翻訳・ニュース分析アシスタントです。英語の記事を読み、JSON で回答してください：
- translated_title: 英語タイトルの自然な日本語訳
- summary: 100文字以内の日本語要約
- key_points: 記事の要点を 3〜5 個、各 30 文字程度の簡潔な日本語の箇条書き（配列）
- category: 「総合」「テクノロジー」「経済・ビジネス」「国際」のいずれか
- score: 0-10 の重要度（10が最重要）
- tags: カンマ区切りで最大3つの日本語タグ

形式: {"translated_title": "...", "summary": "...", "key_points": ["...", "...", "..."], "category": "...", "score": 7, "tags": "タグ1,タグ2,タグ3"}"""


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
        # key_points は配列で受け取るが、DB には JSON 文字列で保存
        kp = result.get("key_points")
        if isinstance(kp, list):
            article.key_points = json.dumps(kp, ensure_ascii=False)
        article.category = normalize_category(result.get("category", article.category))
        article.importance_score = float(result.get("score", 5))
        article.tags = result.get("tags", "")
        article.processed = True
        return True
    except Exception as e:
        logger.error(f"AI処理エラー [{article.title[:30]}]: {e}")
        return False


def process_unprocessed(limit: int = 20, missing_key_points: bool = False) -> int:
    """未処理記事をバッチ処理。

    missing_key_points=True の場合、key_points 未生成の処理済み記事も対象にする。
    """
    client = get_client()
    if not client:
        logger.warning("Azure OpenAI 未設定。スキップします。")
        return 0

    db = SessionLocal()
    try:
        q = db.query(Article).filter(Article.is_duplicate == False)
        if missing_key_points:
            q = q.filter(
                (Article.processed == False) | (Article.key_points.is_(None))
            )
        else:
            q = q.filter(Article.processed == False)
        articles = q.order_by(Article.collected_at.desc()).limit(limit).all()
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
