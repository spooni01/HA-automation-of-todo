"""Add/delete notifications for Local To-do integration."""

from homeassistant.core import HomeAssistant


class Notify:
    """Notification handler."""

    def __init__(self, hass: HomeAssistant):
        self.hass = hass

    async def add_notification(self, title: str, message: str):
        """Creates notification."""

        await self.hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": title,
                "message": message,
            },
        )
