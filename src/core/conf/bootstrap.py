import os
from typing import Dict, List

from dotenv import load_dotenv
from infisical_sdk import InfisicalSDKClient

_BOOTSTRAPPED = False


def _should_bootstrap() -> bool:
    return all(
        [
            os.getenv("INFISICAL_TOKEN"),
            os.getenv("INFISICAL_HOST"),
            os.getenv("ENVIRONMENT_SLUG"),
        ]
    )


def _load_project_secrets(project_slug: str) -> Dict[str, str]:
    client = InfisicalSDKClient(
        host=os.environ["INFISICAL_HOST"],
        token=os.environ["INFISICAL_TOKEN"],
        cache_ttl=300,
    )

    resp = client.secrets.list_secrets(
        project_slug=project_slug,
        environment_slug=os.environ["ENVIRONMENT_SLUG"],
        secret_path="/",
    )

    data = resp.to_dict()
    secrets = data.get("secrets") or {}

    out: Dict[str, str] = {}

    for s in secrets:
        k = s.get("secretKey")
        v = s.get("secretValue")
        if isinstance(k, str) and isinstance(v, str):
            out[k] = v

    return out


def bootstrap_env() -> None:
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return

    # 1️⃣ всегда сначала .env
    load_dotenv()

    # 2️⃣ если включён Infisical
    if _should_bootstrap():
        try:
            projects: List[str] = [
                "shared-market",
                "market-product",
            ]

            merged: Dict[str, str] = {}

            # порядок важен
            for slug in projects:
                secrets = _load_project_secrets(slug)
                merged.update(secrets)
            # user-market перезапишет shared
            os.environ.update(merged)

        except Exception as e:
            print("Infisical bootstrap failed:", e)

    _BOOTSTRAPPED = True
