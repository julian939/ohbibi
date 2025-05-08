import database.sqlmanager as sql

class Tournament:
    def __init__(self, tournament_id: int):
        self.db = sql.SQL()
        self.tournament_id = tournament_id
        self.team_size = None
        self.date = None
        self.title = None
        self.is_official = None
        self._load()

    def _load(self):
        result = self.db.fetchone(
            "SELECT team_size, date, title, is_official FROM tournaments WHERE tournament_id = ?",
            (self.tournament_id,)
        )
        if result:
            self.team_size, self.date, self.title, self.is_official = result

    def exists(self) -> bool:
        result = self.db.fetchone("SELECT EXISTS(SELECT 1 FROM tournaments WHERE tournament_id = ?)", (self.tournament_id,))
        return result and result[0] == 1

    def create(self, team_size: int, date: int, title: str, is_official: int = 0):
        self.db.execute(
            "INSERT INTO tournaments (tournament_id, team_size, date, title, is_official) VALUES (?, ?, ?, ?, ?)",
            (self.tournament_id, team_size, date, title, is_official)
        )
        self._load()

    def delete(self):
        self.db.execute("DELETE FROM tournaments WHERE tournament_id = ?", (self.tournament_id,))
