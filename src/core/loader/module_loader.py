import logging
from importlib import import_module
from typing import Any, List

from fastapi import FastAPI

logger = logging.getLogger(__name__)
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class LoadedModule:
    path: str
    module: Any
    enabled: bool = True
    reason: str | None = None


class ApiModuleLoadError(RuntimeError):
    pass


def _import_attr(path: str) -> Any:
    if ":" not in path:
        raise ApiModuleLoadError(
            f"Invalid API module path '{path}'. Use 'package.module:ClassName'"
        )

    module_path, attr = path.split(":", 1)

    module = import_module(module_path)
    return getattr(module, attr)


def load_modules() -> list[LoadedModule]:
    from src.core.conf.settings import get_settings

    settings = get_settings()
    raw = settings.API_MODULES or []

    loaded = []

    for path in raw:
        obj = _import_attr(path)
        module = obj()

        loaded.append(
            LoadedModule(
                path=path,
                module=module,
                enabled=True,
            )
        )

    loaded.sort(key=lambda x: (x.module.order, x.module.name))
    return loaded



def mount_all(app: FastAPI) -> None:
    loaded = load_modules()

    logger.info("\nAPI modules configuration:\n%s\n",
                _format_modules_table(loaded))

    enabled = [x for x in loaded if x.enabled]

    if not enabled:
        logger.warning("No enabled API modules configured.")
        return

    mounted = set()

    logger.info("Mounting %d module(s)...", len(enabled))

    for item in enabled:
        module = item.module

        if module.name in mounted:
            raise RuntimeError(
                f"Duplicate API module name: {module.name}"
            )

        logger.info(
            "Mounting module: name=%s order=%s source=%s",
            module.name,
            module.order,
            item.path,
        )

        module.mount(app)
        mounted.add(module.name)

    logger.info(
        "API modules mounted successfully: %s",
        ", ".join(m.module.name for m in enabled),
    )



def _normalize_mount_paths(module: Any) -> list[str]:
    raw = getattr(module, "mount_paths", ()) or ()
    if isinstance(raw, str):
        raw = [raw]

    out = []
    for p in raw:
        if not isinstance(p, str):
            continue
        p = p.strip()
        if not p:
            continue
        if not p.startswith("/"):
            p = "/" + p
        out.append(p)
    return out


def _format_modules_table(items: list[LoadedModule]) -> str:
    headers = ["name", "order", "enabled", "paths", "source"]
    rows = []

    for it in items:
        m = it.module
        paths = ", ".join(_normalize_mount_paths(m)) or "-"
        rows.append([
            getattr(m, "name", "-"),
            str(getattr(m, "order", "-")),
            "yes" if it.enabled else f"no({it.reason})",
            paths,
            it.path,
        ])

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    def fmt(row):
        return " | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row))

    separator = "-+-".join("-" * w for w in widths)

    output = [fmt(headers), separator]
    output.extend(fmt(row) for row in rows)
    return "\n".join(output)
