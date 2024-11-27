"""The Local To-do integration."""

from __future__ import annotations

from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.util import slugify
from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.panel_custom import async_register_panel
import os

from .const import CONF_STORAGE_KEY, CONF_TODO_LIST_NAME
from .store import LocalTodoListStore

PLATFORMS: list[Platform] = [Platform.TODO]

STORAGE_PATH = ".storage/local_todo.{key}.ics"

type LocalTodoConfigEntry = ConfigEntry[LocalTodoListStore]


async def async_setup_entry(hass: HomeAssistant, entry: LocalTodoConfigEntry) -> bool:
    """Set up Local To-do from a config entry."""
    path = Path(hass.config.path(STORAGE_PATH.format(key=entry.data[CONF_STORAGE_KEY])))
    store = LocalTodoListStore(hass, path)
    try:
        await store.async_load()
    except OSError as err:
        raise ConfigEntryNotReady("Failed to load file {path}: {err}") from err

    entry.runtime_data = store

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Registration of panel.
    await async_register_panel(
        hass,
        frontend_url_path="local_todo",  
        webcomponent_name="my-task-panel",
        sidebar_title="Moje Úlohy", 
        sidebar_icon="mdi:clipboard-list", 
        module_url=f"/api/local_todo_panel/task_panel.js"  
    )
    hass.http.register_static_path(
        "/api/local_todo_panel/task_panel.js",
        os.path.join(os.path.dirname(__file__), "task_panel.js"),
        cache_headers=False
    )

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
