from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TokenSchema:
    exp: int
    iat: int
    type: str
    fio: Optional[str] = None

@dataclass
class UserPermissionSchema:
    id: int
    name: str

@dataclass
class User:
    id: int
    token_data: TokenSchema
    permissions: List[UserPermissionSchema]
    fio: Optional[str] = None