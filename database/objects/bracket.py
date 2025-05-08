import database.sqlmanager as sql

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
