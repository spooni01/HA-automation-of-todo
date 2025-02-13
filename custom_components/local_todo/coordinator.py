"""Coordinator for Local To-do integration."""

from homeassistant.core import HomeAssistant
from datetime import datetime, timedelta

from .notify import Notify
from .rules import RulesManager


class Coordinator:
    """Handle a state change of entities."""

    def __init__(self, hass: HomeAssistant):
        """Starts listening to changes."""
        self.hass = hass
        config_path = self.hass.config.path()
        self.rules_manager = RulesManager(config_path)
        self.notify = Notify(self.hass)

        hass.bus.async_listen("state_changed", self.entity_state_changed)

    async def entity_state_changed(self, event):
        """Handle a state change of entity."""
        rules = self.rules_manager.get_rules()

        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")
        old_state = event.data.get("old_state")

        if new_state and old_state and new_state.state != old_state.state:
            for rule in rules:
                (
                    rule_id,
                    name,
                    description,
                    rule_entity_id,
                    entity_type_of_change,
                    entity_change_value,
                ) = rule
                if entity_id == rule_entity_id:
                    await self.add_task(name, description)
                    await self.notify.add_notification(name, description)

    async def add_task(self, name, description):
        """Add task to list."""
        due_date = datetime.now().date() + timedelta(days=1)
        await self.hass.services.async_call(
            "todo",
            "add_item",
            {
                "entity_id": "todo.automatizovane",
                "item": name,
                "description": description,
                "due_date": due_date.isoformat(),
            },
        )
