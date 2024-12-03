from datetime import datetime, timezone
import sqlite3
from typing import TypedDict, Optional
from zoneinfo import ZoneInfo

def safe_convert_to_datetime(date_str):
    try:
        return datetime.fromisoformat(date_str).astimezone(timezone.utc) if isinstance(date_str, str) else None
    except ValueError:
        return None

class User(TypedDict):
    user_id: int
    lang_code: Optional[str]
    next_quote_time: Optional[datetime]
    settings: str

class UsersOrm:

    def __del__(self) -> None:
        self.conn.close()

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

        # Auxiliary columns "_is_null" for efficient indexing and querying of "NOT NULL" condition
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER NOT NULL,
                lang_code TEXT,
                next_quote_time TEXT,
                settings TEXT NOT NULL DEFAULT "{}",
                PRIMARY KEY (user_id)
            )
        ''')
        self.conn.commit()

        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_next_quote_time ON users (next_quote_time)')
        self.conn.commit()


    def get_user_by_id(self, user_id: int) -> User:
        """

        :rtype: object
        """
        self.cursor.execute("""SELECT
            user_id,
            lang_code,
            next_quote_time,
            settings
                FROM users WHERE user_id = ?""", (user_id,))
        return self._to_user_obj(self.cursor.fetchone(), user_id)

    def get_some_users_for_quote(self, limit: int) -> list[User]:
        cutoff_time = datetime.now(tz=timezone.utc).isoformat()
        self.cursor.execute("""SELECT
            user_id,
            lang_code,
            next_quote_time,
            settings
                FROM users WHERE next_quote_time < ? LIMIT ?""",
                            (cutoff_time, limit))
        return [self._to_user_obj(row, row[0]) for row in self.cursor.fetchall()]

    def _to_user_obj(self, param, user_id: int):
        if param is None:
            # return default user object
            return User(
                user_id=user_id,
                lang_code="ru",
                next_quote_time=None,
                settings=""
            )
        return User(
            user_id=param[0],
            lang_code=param[1],
            next_quote_time=safe_convert_to_datetime(param[2]),
            settings=param[3]
        )
    def remove_user(self, user_id: int):
        self.cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        self.conn.commit()

    def upsert_user(self, user: User):
        self.cursor.execute('''
            INSERT INTO users (
                user_id, 
                lang_code,
                next_quote_time, 
                settings
                ) VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                lang_code = excluded.lang_code,
                next_quote_time = excluded.next_quote_time,
                settings = excluded.settings
        ''', (
            user['user_id'],
            user['lang_code'],

            # SQLite doesn't support timezone-aware datetime objects. Let's keep it UTC
            # for portability (if we need to run the bot on a different server)
            user['next_quote_time'].astimezone(ZoneInfo('UTC')).isoformat() if user['next_quote_time'] is not None else None,

            user['settings']
        ))
        self.conn.commit()



