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
from .notify import Notify
from .coordinator import Coordinator

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

    rules_manager = RulesManager(hass.config.path())
    hass.data["local_todo"]["rules_manager"] = rules_manager
    async_register_command(hass, async_get_local_todo_rules)
    async_register_command(hass, async_set_local_todo_rule)
    async_register_command(hass, async_delete_local_todo_rule)

    coordinator = Coordinator(hass)

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


@websocket_command(
    {
        "type": "set_local_todo_rule",
        "name": str,
        "description": str,
        "entity_id": str,
        "entity_type_of_change": str,
        "entity_change_value": str,
    }
)
def async_set_local_todo_rule(hass: HomeAssistant, connection, msg: dict) -> None:
    """Handle set_local_todo_rule WebSocket request."""
    name = msg.get("name")
    description = msg.get("description")
    entity_id = msg.get("entity_id")
    entity_type_of_change = msg.get("entity_type_of_change")
    entity_change_value = msg.get("entity_change_value")

    rules_manager: RulesManager = hass.data["local_todo"]["rules_manager"]
    hass.async_create_task(
        rules_manager.add_rule(
            name, description, entity_id, entity_type_of_change, entity_change_value
        )
    )
    connection.send_result(msg["id"], {"status": "success"})


@websocket_command(
    {
        "type": "delete_local_todo_rule",
        "rule_id": int,
    }
)
def async_delete_local_todo_rule(hass: HomeAssistant, connection, msg: dict) -> None:
    """Handle delete_local_todo_rule WebSocket request."""
    rule_id = msg.get("rule_id")

    rules_manager: RulesManager = hass.data["local_todo"]["rules_manager"]
    rules_manager.delete_rule(rule_id)
    connection.send_result(msg["id"], {"status": "success"})
