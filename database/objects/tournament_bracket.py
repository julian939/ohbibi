import database.sqlmanager as sql

class TournamentBracket:
    def __init__(self, tournament_id: int, bracket_id: int):
        self.db = sql.SQL()
        self.tournament_id = tournament_id
        self.bracket_id = bracket_id

    def create(self):
        self.db.execute(
            "INSERT INTO tournament_bracket (tournament_id, bracket_id) VALUES (?, ?)",
            (self.tournament_id, self.bracket_id)
        )

    def delete(self):
        self.db.execute(
            "DELETE FROM tournament_bracket WHERE tournament_id = ? AND bracket_id = ?",
            (self.tournament_id, self.bracket_id)
        )
