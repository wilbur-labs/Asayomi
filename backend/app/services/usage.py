"""API 用量追跡サービス（Azure OpenAI コスト推定込み）"""
import logging
from typing import Optional

from sqlalchemy.orm import Session

from ..core.database import SessionLocal
from ..models.api_usage import ApiUsage

logger = logging.getLogger(__name__)

# 100万トークンあたりの USD 価格（gpt-4o-mini, 2024 公開価格を参考）
PRICE_PER_1M = {
    "gpt-4o-mini":           {"prompt": 0.150,  "completion": 0.600},
    "gpt-4o":                {"prompt": 2.500,  "completion": 10.00},
    "gpt-4-turbo":           {"prompt": 10.00,  "completion": 30.00},
    "gpt-3.5-turbo":         {"prompt": 0.500,  "completion": 1.500},
    "text-embedding-3-small":{"prompt": 0.020,  "completion": 0.0},
    "text-embedding-3-large":{"prompt": 0.130,  "completion": 0.0},
}


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    if not model:
        return 0.0
    # モデル名にプレフィックスが入っていても対応
    key = next((k for k in PRICE_PER_1M if k in (model or "")), None)
    if not key:
        return 0.0
    p = PRICE_PER_1M[key]
    return (prompt_tokens * p["prompt"] + completion_tokens * p["completion"]) / 1_000_000


def record_usage(
    operation: str,
    model: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    db: Optional[Session] = None,
) -> None:
    """API 利用を 1 件記録"""
    own = False
    if db is None:
        db = SessionLocal()
        own = True
    try:
        cost = estimate_cost(model, prompt_tokens, completion_tokens)
        u = ApiUsage(
            operation=operation,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost_usd=cost,
        )
        db.add(u)
        if own:
            db.commit()
    except Exception as e:
        logger.warning(f"用量記録失敗: {e}")
        if own:
            db.rollback()
    finally:
        if own:
            db.close()
