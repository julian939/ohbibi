import database.sqlmanager as sql

class User:

    def __init__(self, discord_id):
        self.user_id = discord_id

        if self.exists() == False:
            self.create()

    def exists(self) -> bool:
        result = sql.SQL().fetchone(f"SELECT EXISTS(SELECT 1 FROM users WHERE id={self.user_id})")[0]
        if result == 1:
            return True
        else:
            return False

    def create(self, tokens=0, season_points=0):
        if not self.exists():
            print("CREATE")
            sql.SQL().execute(f"INSERT INTO users (id, tokens, season_points) VALUES ({self.user_id}, {tokens}, {season_points})")

    def delete(self):
        if self.exists():
            sql.SQL().execute(f"DELETE FROM users WHERE id={self.user_id}")
            #add backup db

    '''
        GETTER
    '''

    def get_tokens(self) -> int:
        result = sql.SQL().fetchone(f"SELECT tokens FROM users WHERE id={self.user_id}")
        return result[0]

    def get_season_points(self) -> int:
        result = sql.SQL().fetchone(f"SELECT season_points FROM users WHERE id={self.user_id}")
        return result[0]

    '''
        SETTER
    '''

    def set_tokens(self, value) -> None:
        sql.SQL().execute(f"UPDATE users SET tokens={value} WHERE id={self.user_id}")

    def set_season_points(self, value) -> None:
        sql.SQL().execute(f"UPDATE users SET season_points={value} WHERE id={self.user_id}")

    '''
        UTILS
    '''

    def change_tokens(self, amount: int) -> int:
        value = self.get_tokens() + amount
        sql.SQL().execute(f"UPDATE users SET tokens={value} WHERE id={self.user_id}")
        return value

    def change_season_points(self, amount: int) -> int:
        value = self.get_season_points() + amount
        sql.SQL().execute(f"UPDATE users SET season_points={value} WHERE id={self.user_id}")
        return value
    
class Users:

    def __init__(self) -> None:
        pass

    def get_users_season_points_leaderboard(self):
        ...
    
    def get_user_tokens_leaderboard(self):
        ...
