from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class PageBlockDTO:
    upload_id: Optional[int] = None
    ordering: int = 0
    data: Optional[dict[str, Any]] = None


@dataclass
class PageCreateDTO:
    slug: str
    title: str
    is_published: bool = False
    blocks: Optional[list[PageBlockDTO]] = None


@dataclass
class PageUpdateDTO:
    slug: Optional[str] = None
    title: Optional[str] = None
    is_published: Optional[bool] = None


@dataclass
class PageBlockReadDTO:
    id: int
    page_id: int
    block_type: str
    order: int
    data: dict[str, Any]
    is_active: bool


@dataclass
class PageReadDTO:
    id: int
    slug: str
    title: str
    is_published: bool
    blocks: list[PageBlockReadDTO]


@dataclass
class FaqCreateDTO:
    question: str
    answer: str
    category: Optional[str] = None
    order: int = 0
    is_active: bool = True


@dataclass
class FaqUpdateDTO:
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


@dataclass
class FaqReadDTO:
    id: int
    question: str
    answer: str
    category: Optional[str]
    order: int
    is_active: bool


@dataclass
class EmailTemplateCreateDTO:
    key: str
    subject: str
    body_html: str
    body_text: Optional[str] = None
    variables: Optional[list[str]] = None
    is_active: bool = True


@dataclass
class EmailTemplateUpdateDTO:
    subject: Optional[str] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    variables: Optional[list[str]] = None
    is_active: Optional[bool] = None


@dataclass
class EmailTemplateReadDTO:
    id: int
    key: str
    subject: str
    body_html: str
    body_text: Optional[str]
    variables: list[str]
    is_active: bool


@dataclass
class FeatureFlagCreateDTO:
    key: str
    enabled: bool = False
    description: Optional[str] = None


@dataclass
class FeatureFlagUpdateDTO:
    enabled: Optional[bool] = None
    description: Optional[str] = None


@dataclass
class FeatureFlagReadDTO:
    id: int
    key: str
    enabled: bool
    description: Optional[str]


@dataclass
class SeoCreateDTO:
    page_slug: str
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[list[str]] = None
    og_image_id: Optional[int] = None


@dataclass
class SeoUpdateDTO:
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[list[str]] = None
    og_image_id: Optional[int] = None


@dataclass
class SeoReadDTO:
    id: int
    page_slug: str
    title: Optional[str]
    description: Optional[str]
    keywords: list[str]
    og_image_id: Optional[int]
