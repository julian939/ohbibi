import database.sqlmanager as sql
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    def get_team_size(self):
        return self.team_size

    def set_team_size(self, new_team_size: int):
        try:
            self.db.execute("UPDATE tournaments SET team_size = ? WHERE tournament_id = ?", (new_team_size, self.tournament_id))
            self.team_size = new_team_size
            logger.info(f"team_size updated to '{new_team_size}' for tournament_id {self.tournament_id}")
        except Exception as e:
            logger.error(f"Error updating team_size: {e}")

    def get_title(self):
        return self.title

    def set_title(self, new_title: str):
        try:
            self.db.execute("UPDATE tournaments SET title = ? WHERE tournament_id = ?", (new_title, self.tournament_id))
            self.title = new_title
            logger.info(f"title updated to '{new_title}' for tournament_id {self.tournament_id}")
        except Exception as e:
            logger.error(f"Error updating title: {e}")

    def get_date(self):
        return self.date

    def set_date(self, new_date: int):
        try:
            self.db.execute("UPDATE tournaments SET date = ? WHERE tournament_id = ?", (new_date, self.tournament_id))
            self.date = new_date
            logger.info(f"date updated to '{new_date}' for tournament_id {self.tournament_id}")
        except Exception as e:
            logger.error(f"Error updating date: {e}")

    def get_is_official(self):
        return self.is_official

    def set_is_official(self, new_is_official: int):
        try:
            self.db.execute("UPDATE tournaments SET is_official = ? WHERE tournament_id = ?", (new_is_official, self.tournament_id))
            self.is_official = new_is_official
            logger.info(f"is_official updated to '{new_is_official}' for tournament_id {self.tournament_id}")
        except Exception as e:
            logger.error(f"Error updating is_official: {e}")