# src/core/auth/dependencies.py

import time

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.core.auth.exceptions import ForbiddenError, UnauthorizedError
from src.core.auth.schemas.user import TokenSchema, User, UserPermissionSchema
from src.core.auth.security import decode_token
from src.core.system.authorizationApi import (
    AuthorizationApiClient,
    AuthorizationApiError,
)
from src.core.system.permission_cache import PermissionCacheService

# 🔐 OAuth2 схема
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="https://market-user.open-gpt.ru/auth/login"
)

# Глобальные экземпляры сервисов (singleton)
_permission_cache = PermissionCacheService()
_auth_api_client: AuthorizationApiClient | None = None


def _get_auth_api_client() -> AuthorizationApiClient:
    global _auth_api_client
    if _auth_api_client is None:
        _auth_api_client = AuthorizationApiClient()
    return _auth_api_client


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
    version = payload.get("version")
    fio = payload.get("fio")

    if not sub:
        raise UnauthorizedError("Некорректный токен")

    if exp and exp < int(time.time()):
        raise UnauthorizedError("Токен истёк")

    user_id = int(sub)
    token_version = str(version) if version is not None else "default"

    # Проверяем кэш
    cached_permissions = await _permission_cache.get(
        user_id=user_id,
        token_version=token_version,
    )

    if cached_permissions is not None:
        # Права найдены в кэше
        permissions = cached_permissions
    else:
        # Прав нет в кэше — запрашиваем через API
        auth_client = _get_auth_api_client()
        try:
            permissions = await auth_client.get_user_permissions(token)
        except AuthorizationApiError as e:
            raise UnauthorizedError(e.message)

        # Сохраняем в кэш (старые версии автоматически удаляются)
        await _permission_cache.set(
            user_id=user_id,
            token_version=token_version,
            permissions=permissions,
        )

    return User(
        id=user_id,
        token_data=TokenSchema(
            exp=exp,
            iat=iat,
            type=payload.get("type"),
            fio=fio,
            version=version,
        ),
        permissions=[
            UserPermissionSchema(id=p.id, name=p.name)
            for p in permissions
        ],
        fio=fio,
    )


def require_permissions(*required: str):
    def _has_permission(user_permissions: set[str], permission: str) -> bool:
        if permission in user_permissions:
            return True

        resource, separator, _ = permission.partition(":")
        if separator and resource in user_permissions:
            return True

        return False

    async def dependency(
        user: User = Depends(get_current_user),
    ):
        user_permissions = {p.name for p in user.permissions}

        for perm in required:
            if not _has_permission(user_permissions, perm):
                raise ForbiddenError()

        return True

    return dependency
