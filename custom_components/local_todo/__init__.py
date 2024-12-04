"""The Local To-do integration."""

from __future__ import annotations

from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.util import slugify
from homeassistant.components.frontend import async_register_built_in_panel
from homeassistant.components.http import StaticPathConfig
import os

from .const import DOMAIN, PANEL_URL, PANEL_TITLE, CONF_STORAGE_KEY, CONF_TODO_LIST_NAME
from .store import LocalTodoListStore
from .rules import RulesManager

PLATFORMS: list[Platform] = [Platform.TODO]

STORAGE_PATH = ".storage/local_todo.{key}.ics"

type LocalTodoConfigEntry = ConfigEntry[LocalTodoListStore]


async def async_setup_entry(hass: HomeAssistant, entry: LocalTodoConfigEntry) -> bool:
    """Set up Local To-do from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    path = Path(hass.config.path(STORAGE_PATH.format(key=entry.data[CONF_STORAGE_KEY])))
    store = LocalTodoListStore(hass, path)
    try:
        await store.async_load()
    except OSError as err:
        raise ConfigEntryNotReady("Failed to load file {path}: {err}") from err

    entry.runtime_data = store

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # rules_manager = RulesManager()
    await register_frontend(hass)
    await add_side_panel(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle removal of an entry."""
    key = slugify(entry.data[CONF_TODO_LIST_NAME])
    path = Path(hass.config.path(STORAGE_PATH.format(key=key)))

    def unlink(path: Path) -> None:
        path.unlink(missing_ok=True)

    await hass.async_add_executor_job(unlink, path)


async def register_frontend(hass):
    """Register frontend file."""
    path = os.path.join(os.path.dirname(__file__), "frontend")
    await hass.http.async_register_static_paths([
        StaticPathConfig(
            "/local_todo/frontend/panel.js",
            os.path.join(path, "panel.js"),
            True
        )
    ])


async def add_side_panel(hass):
    """Add the Local To-do side panel."""

    custom_panel_config = {
        "name": "ha-panel-local-todo",
        "module_url": f"/local_todo/frontend/panel.js",
    }
    panelconf = {}
    panelconf["_panel_custom"] = custom_panel_config
    panelconf[DOMAIN] = hass.data[DOMAIN]
    async_register_built_in_panel(
        hass,
        component_name="custom",
        frontend_url_path=PANEL_URL,
        sidebar_title=PANEL_TITLE,
        sidebar_icon="mdi:checkbox-marked-circle-auto-outline",
        config=panelconf,
        require_admin=False,
    )