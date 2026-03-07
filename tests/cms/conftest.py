"""Фикстуры и утилиты для тестов CMS модуля."""

import pytest
import pytest_asyncio
from sqlalchemy import text

from src.cms.infrastructure.models.email_template import CmsEmailTemplate
from src.cms.infrastructure.models.faq import CmsFaq
from src.cms.infrastructure.models.feature_flag import CmsFeatureFlag
from src.cms.infrastructure.models.page import CmsPage
from src.cms.infrastructure.models.page_block import CmsPageBlock
from src.cms.infrastructure.models.seo import CmsSeo


@pytest_asyncio.fixture(autouse=True)
async def cleanup_cms_data(engine):
    """Очистка данных CMS между тестами."""
    # Очищаем данные ПЕРЕД каждым тестом
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM cms_seo CASCADE"))
        await conn.execute(text("DELETE FROM cms_page_blocks CASCADE"))
        await conn.execute(text("DELETE FROM cms_pages CASCADE"))
        await conn.execute(text("DELETE FROM cms_faq CASCADE"))
        await conn.execute(text("DELETE FROM cms_email_templates CASCADE"))
        await conn.execute(text("DELETE FROM cms_feature_flags CASCADE"))

    yield

    # Очищаем данные ПОСЛЕ каждого теста (для безопасности)
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM cms_seo CASCADE"))
        await conn.execute(text("DELETE FROM cms_page_blocks CASCADE"))
        await conn.execute(text("DELETE FROM cms_pages CASCADE"))
        await conn.execute(text("DELETE FROM cms_faq CASCADE"))
        await conn.execute(text("DELETE FROM cms_email_templates CASCADE"))
        await conn.execute(text("DELETE FROM cms_feature_flags CASCADE"))


@pytest_asyncio.fixture
async def cms_page_data():
    """Данные для создания тестовой страницы."""
    return {
        "slug": "test-page",
        "title": "Тестовая страница",
        "is_published": True,
    }


@pytest_asyncio.fixture
async def cms_faq_data():
    """Данные для создания тестового FAQ."""
    return {
        "question": "Как сделать возврат?",
        "answer": "Возврат можно сделать в течение 14 дней.",
        "category": "returns",
        "order": 0,
        "is_active": True,
    }


@pytest_asyncio.fixture
async def cms_email_template_data():
    """Данные для создания тестового email шаблона."""
    return {
        "key": "welcome_email",
        "subject": "Добро пожаловать!",
        "body_html": "<h1>Привет, {{user_name}}!</h1>",
        "body_text": "Привет, {{user_name}}!",
        "variables": ["user_name"],
        "is_active": True,
    }


@pytest_asyncio.fixture
async def cms_feature_flag_data():
    """Данные для создания тестового feature flag."""
    return {
        "key": "chat_enabled",
        "enabled": True,
        "description": "Включение чата поддержки",
    }
