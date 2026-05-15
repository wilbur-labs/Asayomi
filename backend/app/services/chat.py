"""ニュースを文脈にした AI 対話サービス"""
import logging
from datetime import datetime, timezone, timedelta
from typing import List

from openai import AzureOpenAI
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import SessionLocal
from ..models.article import Article
from .ai_processor import get_client

logger = logging.getLogger(__name__)

SYSTEM = """あなたは Asayomi の専属ニュースアシスタントです。直近の日本のニュースを文脈として、ユーザの質問に日本語で簡潔に答えてください。
- 関連する記事には [1] [2] のように番号を振り、回答末尾に出典リストを付けてください。
- 推測ではなく、提示された記事のみに基づいて回答してください。
- 記事に答えが無い場合は「提供された記事には情報がありません」と明示してください。"""


def _gather_recent(limit: int = 25) -> List[Article]:
    db: Session = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=2)
        return (
            db.query(Article)
            .filter(
                Article.collected_at >= cutoff,
                Article.processed == True,
                Article.is_duplicate == False,
            )
            .order_by(Article.importance_score.desc())
            .limit(limit)
            .all()
        )
    finally:
        db.close()


def _format_context(articles: List[Article]) -> str:
    lines = []
    for i, a in enumerate(articles, 1):
        # Python operator precedence trap: `A or B if C else D` parses as
        # `(A or B) if C else D`, which would drop summary when
        # original_content is None. Parenthesize the conditional so summary
        # is always preferred when present.
        snippet = a.summary or (a.original_content[:120] if a.original_content else "")
        lines.append(
            f"[{i}] ({a.category}) {a.title}\n"
            f"   要約: {snippet}\n"
            f"   URL: {a.url}"
        )
    return "\n".join(lines)


def chat(question: str) -> dict:
    """ユーザ質問に対してニュース文脈付きで回答"""
    client = get_client()
    if not client:
        return {"answer": "Azure OpenAI が設定されていません。.env を確認してください。", "sources": []}

    articles = _gather_recent()
    if not articles:
        return {"answer": "まだ AI 処理済みのニュースがありません。先に「AI処理」を実行してください。", "sources": []}

    context = _format_context(articles)
    try:
        resp = client.chat.completions.create(
            model=settings.azure_openai_deployment_name,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"## 直近のニュース\n{context}\n\n## 質問\n{question}"},
            ],
            temperature=0.4,
            max_tokens=600,
        )
        # 用量記録
        try:
            from .usage import record_usage
            u = resp.usage
            if u:
                record_usage("chat", settings.azure_openai_deployment_name, u.prompt_tokens, u.completion_tokens)
        except Exception:
            pass

        answer = resp.choices[0].message.content
        return {
            "answer": answer,
            "sources": [
                {"id": a.id, "title": a.title, "url": a.url, "category": a.category}
                for a in articles
            ],
        }
    except Exception as e:
        logger.error(f"chat エラー: {e}")
        return {"answer": f"エラー: {e}", "sources": []}
