"""記事全文取得サービス"""
import logging
import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Asayomi NewsBot; +https://github.com/wilbur-labs/Asayomi)"
TIMEOUT = 10.0
MAX_CONTENT_LENGTH = 10000  # 最大文字数（コスト制御）

# 一般的な本文コンテナのセレクタ（優先順）
CONTENT_SELECTORS = [
    "article",
    'main[role="main"]',
    "main",
    'div[itemprop="articleBody"]',
    ".article-body",
    ".post-content",
    ".entry-content",
    "#main-content",
    "#article-body",
]

# ノイズタグ（除去）
NOISE_TAGS = ["script", "style", "nav", "header", "footer", "aside", "form", "iframe"]


def fetch_full_text(url: str) -> Optional[str]:
    """URL から本文テキストを抽出"""
    try:
        with httpx.Client(timeout=TIMEOUT, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as client:
            r = client.get(url)
            r.raise_for_status()
            html = r.text
    except Exception as e:
        logger.warning(f"全文取得失敗 {url}: {e}")
        return None

    soup = BeautifulSoup(html, "html.parser")

    # ノイズ除去
    for tag in soup.find_all(NOISE_TAGS):
        tag.decompose()
    for tag in soup.find_all(attrs={"role": ["banner", "navigation", "complementary"]}):
        tag.decompose()

    # 本文候補を探す
    for sel in CONTENT_SELECTORS:
        node = soup.select_one(sel)
        if node:
            text = node.get_text(separator="\n", strip=True)
            if len(text) > 200:  # 本文と判定する最低文字数
                return _clean(text)

    # フォールバック: body 全体
    body = soup.body
    if body:
        text = body.get_text(separator="\n", strip=True)
        if len(text) > 200:
            return _clean(text)
    return None


def _clean(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text[:MAX_CONTENT_LENGTH]
