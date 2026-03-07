from dataclasses import dataclass
from typing import Optional

from src.cms.domain.events.base import DomainEvent


@dataclass
class PageCreatedEvent(DomainEvent):
    page_id: int
    slug: str
    title: str


@dataclass
class PagePublishedEvent(DomainEvent):
    page_id: int
    slug: str


@dataclass
class PageUnpublishedEvent(DomainEvent):
    page_id: int
    slug: str


@dataclass
class PageTitleChangedEvent(DomainEvent):
    page_id: int
    old_title: str
    new_title: str


@dataclass
class PageSlugChangedEvent(DomainEvent):
    page_id: int
    old_slug: str
    new_slug: str


@dataclass
class PageBlockAddedEvent(DomainEvent):
    page_id: int
    block_id: int
    block_type: str
    order: int


@dataclass
class PageBlockRemovedEvent(DomainEvent):
    page_id: int
    block_id: int


@dataclass
class PageBlockReorderedEvent(DomainEvent):
    page_id: int
    block_id: int
    new_order: int


@dataclass
class PageBlockDataChangedEvent(DomainEvent):
    page_id: int
    block_id: int
    old_data: dict
    new_data: dict


@dataclass
class FaqCreatedEvent(DomainEvent):
    faq_id: int
    question: str
    category: Optional[str]


@dataclass
class FaqUpdatedEvent(DomainEvent):
    faq_id: int
    old_question: str
    new_question: str


@dataclass
class FaqDeletedEvent(DomainEvent):
    faq_id: int


@dataclass
class EmailTemplateCreatedEvent(DomainEvent):
    template_id: int
    key: str


@dataclass
class EmailTemplateUpdatedEvent(DomainEvent):
    template_id: int
    key: str


@dataclass
class FeatureFlagChangedEvent(DomainEvent):
    flag_id: int
    key: str
    old_enabled: bool
    new_enabled: bool


@dataclass
class SeoUpdatedEvent(DomainEvent):
    seo_id: int
    page_slug: str
