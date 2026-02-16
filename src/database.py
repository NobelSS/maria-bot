import sqlite3
import os

DB_FILE = 'maria.db'

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tracked_users (
                riot_id TEXT PRIMARY KEY,
                puuid TEXT NOT NULL,
                last_game_id TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                discord_user_id TEXT PRIMARY KEY
            )
        ''')
        conn.commit()

def add_user(riot_id, puuid):
    try:
        with get_connection() as conn:
            conn.execute('INSERT INTO tracked_users (riot_id, puuid) VALUES (?, ?)', (riot_id, puuid))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def remove_user(riot_id):
    with get_connection() as conn:
        cursor = conn.execute('DELETE FROM tracked_users WHERE riot_id = ?', (riot_id,))
        conn.commit()
        return cursor.rowcount > 0

def add_subscriber(discord_user_id):
    try:
        with get_connection() as conn:
            conn.execute('INSERT INTO subscribers (discord_user_id) VALUES (?)', (discord_user_id,))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def remove_subscriber(discord_user_id):
    with get_connection() as conn:
        cursor = conn.execute('DELETE FROM subscribers WHERE discord_user_id = ?', (discord_user_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_subscribers():
    with get_connection() as conn:
        cursor = conn.execute('SELECT discord_user_id FROM subscribers')
        return [row['discord_user_id'] for row in cursor.fetchall()]

def get_all_users():
    with get_connection() as conn:
        cursor = conn.execute('SELECT riot_id, puuid, last_game_id FROM tracked_users')
        return cursor.fetchall()

def update_last_game(riot_id, game_id):
    with get_connection() as conn:
        conn.execute('UPDATE tracked_users SET last_game_id = ? WHERE riot_id = ?', (game_id, riot_id))
        conn.commit()

# Initialize DB on module load
init_db()
