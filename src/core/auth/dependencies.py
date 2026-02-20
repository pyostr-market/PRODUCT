# src/core/auth/dependencies.py

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
import time

from src.core.auth.security import decode_token
from src.core.auth.schemas.user import User, TokenSchema, UserPermissionSchema
from src.core.auth.exceptions import UnauthorizedError, ForbiddenError


# 🔐 OAuth2 схема
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="https://market-user.open-gpt.ru/auth/login"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> User:

    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Токен истёк")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Невалидный токен")

    exp = payload.get("exp")
    iat = payload.get("iat")
    sub = payload.get("sub")
    permissions = payload.get("permissions", [])

    if not sub:
        raise UnauthorizedError("Некорректный токен")

    if exp and exp < int(time.time()):
        raise UnauthorizedError("Токен истёк")

    return User(
        id=int(sub),
        token_data=TokenSchema(
            exp=exp,
            iat=iat,
            type=payload.get("type"),
        ),
        permissions=[
            UserPermissionSchema(id=p["id"], name=p["name"])
            for p in permissions
        ],
    )


def require_permissions(*required: str):
    async def dependency(
        user: User = Depends(get_current_user),
    ):
        user_permissions = {p.name for p in user.permissions}

        for perm in required:
            if perm not in user_permissions:
                raise ForbiddenError()

        return True

    return dependency