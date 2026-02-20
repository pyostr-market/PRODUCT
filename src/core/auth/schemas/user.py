from dataclasses import dataclass
from typing import List


@dataclass
class TokenSchema:
    exp: int
    iat: int
    type: str

@dataclass
class UserPermissionSchema:
    id: int
    name: str

@dataclass
class User:
    id: int
    token_data: TokenSchema
    permissions: List[UserPermissionSchema]