"""The Local To-do integration."""

from __future__ import annotations
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.components.websocket_api import async_register_command
from homeassistant.components.websocket_api.decorators import websocket_command
from homeassistant.util import slugify
import logging

from .const import (
    CONF_STORAGE_KEY,
    CONF_TODO_LIST_NAME,
    DOMAIN,
)
from .store import LocalTodoListStore
from .rules import RulesManager

PLATFORMS: list[Platform] = [Platform.TODO]

STORAGE_PATH = ".storage/local_todo.{key}.ics"

type LocalTodoConfigEntry = ConfigEntry[LocalTodoListStore]

_LOGGER = logging.getLogger(__name__)


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

    rules_manager = RulesManager()
    hass.data["local_todo"]["rules_manager"] = rules_manager
    async_register_command(hass, async_get_local_todo_rules)

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


@websocket_command({"type": "get_local_todo_rules"})
def async_get_local_todo_rules(hass: HomeAssistant, connection, msg: dict) -> None:
    """Handle get_local_todo_rules WebSocket request."""
    rules_manager: RulesManager = hass.data["local_todo"]["rules_manager"]
    connection.send_result(msg["id"], {"payload": rules_manager.get_rules()})
