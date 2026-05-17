"""記事画像 URL 抽出ユーティリティ"""
import logging
import re
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
TIMEOUT = 8.0

# 明らかに広告/トラッキング/アイコンっぽい画像 URL を除外
_BLOCKED_PATTERNS = re.compile(
    r"(spacer|pixel|blank|1x1|tracking|advert|logo|icon|favicon|sprite|emoji)",
    re.IGNORECASE,
)


def _is_valid_image_url(url: Optional[str]) -> bool:
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return False
    if _BLOCKED_PATTERNS.search(url):
        return False
    # data:image など除外済み
    return True


def extract_image_from_entry(entry) -> Optional[str]:
    """feedparser の entry からサムネイル画像 URL を抽出する。

    優先順:
      1. media_thumbnail / media_content (Media RSS)
      2. enclosure (image/* の links)
      3. summary / content の <img>
    """
    # 1. Media RSS
    for key in ("media_thumbnail", "media_content"):
        items = entry.get(key) or []
        for item in items:
            url = item.get("url") if isinstance(item, dict) else None
            if _is_valid_image_url(url):
                return url

    # 2. enclosure (links 経由)
    for link in entry.get("links", []) or []:
        if not isinstance(link, dict):
            continue
        if link.get("rel") == "enclosure":
            mime = (link.get("type") or "").lower()
            href = link.get("href")
            if mime.startswith("image/") and _is_valid_image_url(href):
                return href

    # 3. summary / content から最初の <img>
    html_candidates = []
    if entry.get("summary"):
        html_candidates.append(entry["summary"])
    for c in entry.get("content", []) or []:
        if isinstance(c, dict) and c.get("value"):
            html_candidates.append(c["value"])

    for html in html_candidates:
        try:
            soup = BeautifulSoup(html, "html.parser")
            img = soup.find("img")
            if img:
                src = img.get("src") or img.get("data-src")
                if _is_valid_image_url(src):
                    return src
        except Exception:  # pragma: no cover
            continue

    return None


def fetch_og_image(url: str) -> Optional[str]:
    """ページから og:image / twitter:image を取得（フォールバック用）。"""
    try:
        with httpx.Client(
            timeout=TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            r = client.get(url)
            r.raise_for_status()
            html = r.text
    except Exception as e:
        logger.debug(f"og:image 取得失敗 {url}: {e}")
        return None

    soup = BeautifulSoup(html, "html.parser")
    for prop in ("og:image", "og:image:url", "twitter:image", "twitter:image:src"):
        tag = soup.find("meta", attrs={"property": prop}) or soup.find(
            "meta", attrs={"name": prop}
        )
        if tag and tag.get("content"):
            candidate = tag["content"].strip()
            # 相対 URL を絶対 URL に変換
            if candidate.startswith("//"):
                candidate = urlparse(url).scheme + ":" + candidate
            elif candidate.startswith("/"):
                candidate = urljoin(url, candidate)
            if _is_valid_image_url(candidate):
                return candidate
    return None
