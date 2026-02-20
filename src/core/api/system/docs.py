from fastapi import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import HTMLResponse

from src.core.api.fastapi_conf import app_server

docs_router = APIRouter(
    tags=['Система']
)

@docs_router.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    html = get_swagger_ui_html(
        openapi_url=app_server.openapi_url,
        title="Docs",
        swagger_ui_parameters={
            "persistAuthorization": True,
        },
    )

    custom_js = """
    <script>
    document.addEventListener("click", function(event) {

        if (event.target && event.target.innerText === "Authorize") {

            setTimeout(() => {

                const username = document.querySelector("input[type='text']");
                const password = document.querySelector("input[type='password']");

                if (!username || !password) return;

                const setNativeValue = (element, value) => {
                    const valueSetter = Object.getOwnPropertyDescriptor(
                        element.__proto__,
                        "value"
                    ).set;

                    valueSetter.call(element, value);

                    element.dispatchEvent(new Event("input", { bubbles: true }));
                    element.dispatchEvent(new Event("change", { bubbles: true }));
                };

                setNativeValue(username, "+79991234567");
                setNativeValue(password, "string");

            }, 300);
        }
    });
    </script>
    """

    return HTMLResponse(html.body.decode() + custom_js)