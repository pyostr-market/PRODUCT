import pytest

from src.core.auth.dependencies import require_permissions
from src.core.auth.exceptions import ForbiddenError
from src.core.auth.schemas.user import TokenSchema, User, UserPermissionSchema


def _build_user(permission_names: list[str]) -> User:
    permissions = [
        UserPermissionSchema(id=index + 1, name=name)
        for index, name in enumerate(permission_names)
    ]
    return User(
        id=1,
        token_data=TokenSchema(exp=9999999999, iat=0, type="access"),
        permissions=permissions,
    )


@pytest.mark.asyncio
async def test_base_permission_grants_action_permission():
    dependency = require_permissions("category:create")
    user = _build_user(["category"])

    assert await dependency(user=user) is True


@pytest.mark.asyncio
async def test_action_permission_does_not_grant_base_permission():
    dependency = require_permissions("category")
    user = _build_user(["category:create"])

    with pytest.raises(ForbiddenError):
        await dependency(user=user)


@pytest.mark.asyncio
async def test_missing_permission_raises_forbidden():
    dependency = require_permissions("category:update")
    user = _build_user(["product"])

    with pytest.raises(ForbiddenError):
        await dependency(user=user)
