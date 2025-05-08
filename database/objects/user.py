import database.sqlmanager as sql
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User:
    def __init__(
        self,
        discord_id: Optional[int] = None,
        ingame_name: Optional[str] = None,
        auto_create: bool = True
    ):
        self.db = sql.SQL()

        if not discord_id and not ingame_name:
            raise ValueError("Either 'discord_id' or 'ingame_name' must be provided.")

        self.discord_id = discord_id
        self.ingame_name = ingame_name
        self.mmr = 0

        try:
            if self.discord_id:
                self._load_by_discord_id()
            elif self.ingame_name:
                self._load_by_ingame_name()

            if not self.exists() and auto_create:
                if self.discord_id is not None and self.ingame_name:
                    self.create()
                else:
                    logger.warning("User does not exist and cannot be created – missing required fields.")
        except Exception as e:
            logger.error(f"Error initializing user: {e}")

    def _load_by_discord_id(self):
        result = self.db.fetchone(
            "SELECT discord_id, ingame_name, mmr FROM users WHERE discord_id = ?",
            (self.discord_id,)
        )
        if result:
            self.discord_id, self.ingame_name, self.mmr = result

    def _load_by_ingame_name(self):
        result = self.db.fetchone(
            "SELECT discord_id, ingame_name, mmr FROM users WHERE ingame_name = ?",
            (self.ingame_name,)
        )
        if result:
            self.discord_id, self.ingame_name, self.mmr = result

    def exists(self) -> bool:
        try:
            if self.discord_id:
                result = self.db.fetchone("SELECT EXISTS(SELECT 1 FROM users WHERE discord_id = ?)", (self.discord_id,))
            elif self.ingame_name:
                result = self.db.fetchone("SELECT EXISTS(SELECT 1 FROM users WHERE ingame_name = ?)", (self.ingame_name,))
            else:
                return False
            return result[0] == 1
        except Exception as e:
            logger.error(f"Error checking existence: {e}")
            return False

    def create(self):
        try:
            self.db.execute(
                "INSERT INTO users (discord_id, ingame_name, mmr) VALUES (?, ?, ?)",
                (self.discord_id, self.ingame_name, self.mmr)
            )
            self._load_by_discord_id()
            logger.info(f"User created: Discord ID {self.discord_id}, Ingame Name '{self.ingame_name}'")
        except Exception as e:
            logger.error(f"Error creating user: {e}")

    def delete(self):
        try:
            self.db.execute("DELETE FROM users WHERE discord_id = ?", (self.discord_id,))
            logger.info(f"User with Discord ID {self.discord_id} deleted.")
        except Exception as e:
            logger.error(f"Error deleting user: {e}")

    def get_ingame_name(self) -> Optional[str]:
        return self.ingame_name

    def set_ingame_name(self, new_name: str):
        try:
            self.db.execute("UPDATE users SET ingame_name = ? WHERE discord_id = ?", (new_name, self.discord_id))
            self.ingame_name = new_name
            logger.info(f"Ingame name updated to '{new_name}' for Discord ID {self.discord_id}")
        except Exception as e:
            logger.error(f"Error updating ingame name: {e}")

    def get_mmr(self) -> int:
        return self.mmr

    def set_mmr(self, value: int):
        try:
            self.db.execute("UPDATE users SET mmr = ? WHERE discord_id = ?", (value, self.discord_id))
            self.mmr = value
            logger.info(f"MMR set to {value} for Discord ID {self.discord_id}")
        except Exception as e:
            logger.error(f"Error setting MMR: {e}")

    def change_mmr(self, delta: int) -> int:
        try:
            new_mmr = self.mmr + delta
            self.set_mmr(new_mmr)
            return new_mmr
        except Exception as e:
            logger.error(f"Error changing MMR: {e}")
            return self.mmr
