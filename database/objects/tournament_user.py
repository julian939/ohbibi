import database.sqlmanager as sql

class TournamentUser:
    def __init__(self, discord_id: int, tournament_id: int):
        self.db = sql.SQL()
        self.discord_id = discord_id
        self.tournament_id = tournament_id

    def create(self):
        self.db.execute(
            "INSERT INTO tournament_user (discord_id, tournament_id) VALUES (?, ?)",
            (self.discord_id, self.tournament_id)
        )

    def delete(self):
        self.db.execute(
            "DELETE FROM tournament_user WHERE discord_id = ? AND tournament_id = ?",
            (self.discord_id, self.tournament_id)
        )
