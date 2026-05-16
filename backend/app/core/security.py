"""Authentication primitives for admin-only routes.

Currently a single shared-secret header check (`X-Asayomi-Admin-Token`).
Used as a FastAPI dependency:

    from .core.security import require_admin_token
    app.include_router(system_router, dependencies=[Depends(require_admin_token)])

The /system/* endpoints can trigger Azure OpenAI batch processing,
external RSS fetches, and email/Slack/Discord notifications. They
must NOT be reachable by anonymous callers — leaving them open in
even a "trusted internal network" scenario means any other process
on the same host can drain the OpenAI budget.

Behavior:
- If ADMIN_TOKEN is not configured → 503 (fail closed). Operators
  must opt-in explicitly. Forgetting to set the token locks the
  routes rather than silently leaving them open.
- If header missing or wrong → 401.
"""
from fastapi import Header, HTTPException, status

from .config import settings


def require_admin_token(
    x_asayomi_admin_token: str | None = Header(default=None),
) -> None:
    expected = settings.admin_token
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin endpoints disabled: ADMIN_TOKEN is not configured.",
        )
    if x_asayomi_admin_token != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Asayomi-Admin-Token header.",
        )
