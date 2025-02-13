"""Rules handler for Local To-do integration."""

import os
import sqlite3

from .const import CONF_DB_PATH


class RulesManager:
    """Rules manager for a Local To-do integration."""

    def __init__(self, config_path):
        """Initialize database."""
        self.conn = sqlite3.connect(os.path.join(config_path, CONF_DB_PATH))
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                entity_id TEXT,
                entity_type_of_change TEXT,
                entity_change_value TEXT
            )
        """)

    async def add_rule(
        self, name, description, entity_id, entity_type_of_change, entity_change_value
    ):
        """Add rule to database."""
        self.cursor.execute(
            """
            INSERT INTO rules (name, description, entity_id, entity_type_of_change, entity_change_value)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, description, entity_id, entity_type_of_change, entity_change_value),
        )
        self.conn.commit()

    def get_rules(self):
        """Fetch all rules from the database."""
        self.cursor.execute(
            "SELECT id, name, description, entity_id, entity_type_of_change, entity_change_value FROM rules"
        )
        return self.cursor.fetchall()

    def delete_rule(self, rule_id):
        """Delete a rule by its ID."""
        self.cursor.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
        self.conn.commit()

    def delete_all_rules(self):
        """Delete all rules from the database."""
        self.cursor.execute("DELETE FROM rules")
        self.conn.commit()

    def update_rule(
        self,
        rule_id,
        name,
        description,
        entity_id,
        entity_type_of_change,
        entity_change_value,
    ):
        """Update an existing rule by its ID."""
        self.cursor.execute(
            """
            UPDATE rules
            SET name = ?, description = ?, entity_id = ?, entity_type_of_change = ?, entity_change_value = ?
            WHERE id = ?
            """,
            (
                name,
                description,
                entity_id,
                entity_type_of_change,
                entity_change_value,
                rule_id,
            ),
        )
        self.conn.commit()
