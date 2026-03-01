from typing import Any, Dict

import jwt

from src.core.conf.settings import get_settings

# ===============================
# JWT ACCESS TOKEN
# ===============================


def decode_token(token: str) -> Dict[str, Any]:
    settings = get_settings()

    return jwt.decode(
        token,
        settings.JWT_PUBLIC_KEY,
        algorithms=["ES256"],
    )
