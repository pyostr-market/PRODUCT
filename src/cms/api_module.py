from fastapi import FastAPI

from src.cms.api.api_v1.email_template import email_template_router
from src.cms.api.api_v1.faq import faq_router
from src.cms.api.api_v1.feature_flag import feature_flag_router
from src.cms.api.api_v1.page import page_router
from src.cms.api.api_v1.seo import seo_router


class CmsApiModule:
    """CMS API модуль."""

    name = "cms"
    order = 15
    mount_paths = ["/cms"]

    def mount(self, app: FastAPI) -> None:
        # Специфичные роутеры регистрируем ПЕРЕД page_router чтобы избежать конфликтов
        # page_router имеет маршрут /{slug} который перехватывает все запросы

        # FAQ endpoints (должен быть ПЕРЕД page_router)
        app.include_router(faq_router, prefix="/cms/faq")

        # Email template endpoints (должен быть ПЕРЕД page_router)
        app.include_router(email_template_router, prefix="/cms/email-templates")

        # Feature flag endpoints (должен быть ПЕРЕД page_router)
        app.include_router(feature_flag_router, prefix="/cms/feature-flags")

        # SEO endpoints (должен быть ПЕРЕД page_router)
        app.include_router(seo_router, prefix="/cms/seo")

        # Page endpoints (в конце, т.к. имеет общий маршрут /{slug})
        app.include_router(page_router, prefix="/cms")
