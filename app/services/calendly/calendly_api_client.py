import httpx
from fastapi import HTTPException

from app.core.config import settings


CALENDLY_API_BASE_URL = "https://api.calendly.com"


def get_current_user() -> dict:
    """
    Retrieve current Calendly user profile using Personal Access Token.

    Raises:
    - HTTPException when Calendly API token is missing.
    - HTTPException when Calendly API request fails.
    """

    if not settings.CALENDLY_PERSONAL_ACCESS_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="Calendly Personal Access Token is not configured.",
        )

    try:
        response = httpx.get(
            f"{CALENDLY_API_BASE_URL}/users/me",
            headers={
                "Authorization": (
                    f"Bearer {settings.CALENDLY_PERSONAL_ACCESS_TOKEN}"
                ),
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Calendly API request failed.",
        ) from exc

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail="Calendly API request failed.",
        ) from exc

    return response.json()


def list_webhook_subscriptions() -> dict:
    """
    Retrieve Calendly webhook subscriptions for the current organization.

    Raises:
    - HTTPException when Calendly API token is missing.
    - HTTPException when Calendly API request fails.
    """

    current_user = get_current_user()
    organization_uri = current_user["resource"]["current_organization"]

    try:
        response = httpx.get(
            f"{CALENDLY_API_BASE_URL}/webhook_subscriptions",
            params={
                "organization": organization_uri,
                "scope": "organization",
            },
            headers={
                "Authorization": (
                    f"Bearer {settings.CALENDLY_PERSONAL_ACCESS_TOKEN}"
                ),
                "Content-Type": "application/json",
            },
            timeout=10.0,
        )

        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="Calendly webhook subscriptions request failed.",
        ) from exc

    return response.json()