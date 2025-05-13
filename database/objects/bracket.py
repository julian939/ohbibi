import database.sqlmanager as sql
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Bracket:
    def __init__(self, bracket_id: int):
        self.db = sql.SQL()
        self.bracket_id = bracket_id
        self.round_amount = None
        self._load()

    def _load(self):
        result = self.db.fetchone("SELECT round_amount FROM brackets WHERE bracket_id = ?", (self.bracket_id,))
        if result:
            self.round_amount = result[0]

    def exists(self) -> bool:
        result = self.db.fetchone("SELECT EXISTS(SELECT 1 FROM brackets WHERE bracket_id = ?)", (self.bracket_id,))
        return result and result[0] == 1

    def create(self, round_amount: int):
        self.db.execute("INSERT INTO brackets (bracket_id, round_amount) VALUES (?, ?)", (self.bracket_id, round_amount))
        self.round_amount = round_amount

    def delete(self):
        self.db.execute("DELETE FROM brackets WHERE bracket_id = ?", (self.bracket_id,))

    def get_round_amount(self) -> int:
        return self.round_amount

    def set_round_amount(self, new_round_amount: int):
        try:
            self.db.execute("UPDATE brackets SET round_amount = ? WHERE discord_id = ?", (new_round_amount, self.discord_id))
            self.round_amount = new_round_amount
            logger.info(f"Round amount updated to '{new_round_amount}' for Discord ID {self.discord_id}")
        except Exception as e:
            logger.error(f"Error updating round amount: {e}")
