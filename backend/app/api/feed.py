"""自分の集約結果を RSS / Atom フィードとして出力"""
from datetime import datetime, timezone
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, Response, Query
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import get_db
from ..models.article import Article

router = APIRouter(prefix="/api/v1/feed", tags=["feed"])


def _rfc822(dt: datetime) -> str:
    if not dt:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


@router.get("/rss.xml")
def rss_feed(
    category: str | None = None,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Article).filter(Article.is_duplicate == False, Article.processed == True)
    if category:
        q = q.filter(Article.category == category)
    articles = q.order_by(Article.collected_at.desc()).limit(limit).all()

    site = settings.rss_site_url.rstrip("/")
    title = f"Asayomi · {category}" if category else "Asayomi · Japan News Briefing"
    items_xml = []
    for a in articles:
        desc = a.summary or a.original_content or ""
        items_xml.append(f"""    <item>
      <title>{escape(a.title)}</title>
      <link>{escape(a.url)}</link>
      <guid isPermaLink="true">{escape(a.url)}</guid>
      <description>{escape(desc)}</description>
      <category>{escape(a.category)}</category>
      <source>{escape(a.source)}</source>
      <pubDate>{_rfc822(a.published_at or a.collected_at)}</pubDate>
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{escape(title)}</title>
    <link>{site}</link>
    <description>AI が要約した日本のニュース</description>
    <language>ja</language>
    <lastBuildDate>{_rfc822(datetime.now(timezone.utc))}</lastBuildDate>
    <atom:link href="{site}/api/v1/feed/rss.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items_xml)}
  </channel>
</rss>"""
    return Response(content=rss, media_type="application/rss+xml; charset=utf-8")
