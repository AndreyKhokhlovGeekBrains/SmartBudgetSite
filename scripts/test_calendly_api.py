from pathlib import Path
from pprint import pprint
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.calendly.calendly_api_client import (
    list_webhook_subscriptions,
)


def main() -> None:
    """
    Test Calendly webhook subscriptions API.
    """

    subscriptions = list_webhook_subscriptions()
    pprint(subscriptions)


if __name__ == "__main__":
    main()
