"""通知サービス：メール / Webhook / Slack / Discord"""
import json
import logging
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape as html_escape
from typing import Optional

import httpx

from ..core.config import settings
from ..core.database import SessionLocal
from ..models.article import DailyBriefing
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def send_email(subject: str, html: str, to: Optional[str] = None) -> bool:
    """SMTP でメール送信。設定が無ければ False。"""
    host = settings.smtp_host
    port = settings.smtp_port
    user = settings.smtp_username
    pwd = settings.smtp_password
    from_addr = settings.smtp_from_email or user
    to_addr = to or settings.notify_email

    if not all([host, user, pwd, from_addr, to_addr]):
        logger.info("SMTP 未設定、メール送信スキップ")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.starttls()
            server.login(user, pwd)
            server.sendmail(from_addr, [to_addr], msg.as_string())
        logger.info(f"メール送信成功: {to_addr}")
        return True
    except Exception as e:
        logger.error(f"メール送信失敗: {e}")
        return False


def send_webhook(payload: dict, url: Optional[str] = None) -> bool:
    """汎用 Webhook 送信"""
    target = url or settings.webhook_url
    if not target:
        return False
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(target, json=payload)
            r.raise_for_status()
        logger.info(f"Webhook 送信成功: {target}")
        return True
    except Exception as e:
        logger.error(f"Webhook 送信失敗: {e}")
        return False


def send_slack(text: str, url: Optional[str] = None) -> bool:
    target = url or settings.slack_webhook_url
    if not target:
        return False
    return send_webhook({"text": text}, url=target)


def send_discord(content: str, url: Optional[str] = None) -> bool:
    target = url or settings.discord_webhook_url
    if not target:
        return False
    return send_webhook({"content": content[:2000]}, url=target)


_BOLD_PATTERN = re.compile(r"\*\*(.+?)\*\*")
_URL_PATTERN = re.compile(r"(https?://[^\s<]+)")


def _render_markdown_lite(content: str) -> str:
    # Briefing content interleaves RSS titles and AI-generated summaries —
    # escape first, then re-introduce only the markdown-lite features used
    # by briefing._build_lines (**bold**, bare URLs, newlines).
    safe = html_escape(content)
    safe = _BOLD_PATTERN.sub(r"<b>\1</b>", safe)
    safe = _URL_PATTERN.sub(r'<a href="\1">\1</a>', safe)
    return safe.replace("\n", "<br>")


def render_briefing_html(date_str: str) -> Optional[str]:
    """指定日のブリーフィングを HTML メール本文に整形"""
    db = SessionLocal()
    try:
        briefings = db.query(DailyBriefing).filter(DailyBriefing.date == date_str).all()
        if not briefings:
            return None
        body = [
            "<html><body style='font-family:sans-serif;max-width:680px;margin:auto;'>",
            f"<h1 style='color:#4f46e5;'>📰 Asayomi · {html_escape(date_str)}</h1>",
        ]
        for b in briefings:
            body.append(
                f"<h2 style='border-bottom:2px solid #c7d2fe;padding-bottom:6px;'>"
                f"{html_escape(b.category)}</h2>"
            )
            body.append(
                f"<div style='line-height:1.8;color:#374151;'>"
                f"{_render_markdown_lite(b.content)}</div>"
            )
        body.append("<hr><p style='color:#9ca3af;font-size:12px;'>Asayomi · Japan News Briefing</p>")
        body.append("</body></html>")
        return "".join(body)
    finally:
        db.close()


def send_daily_briefing_notifications(date_str: Optional[str] = None) -> dict:
    """毎日ブリーフィングを各チャンネルへ送信"""
    if not date_str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    html = render_briefing_html(date_str)
    if not html:
        return {"sent": False, "reason": "no briefing"}

    text_summary = f"Asayomi {date_str} のブリーフィングが届きました。詳細はメール本文をご確認ください。"
    results = {
        "email": send_email(f"Asayomi · {date_str}", html),
        "slack": send_slack(text_summary),
        "discord": send_discord(text_summary),
        "webhook": send_webhook({"date": date_str, "summary": text_summary}),
    }
    logger.info(f"通知送信結果: {results}")
    return {"sent": True, "channels": results}
