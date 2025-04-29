import sqlite3
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DB_NAME = "eight_queens.db"

def init_db():
    logger.debug(f"Initializing database: {DB_NAME}")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        c.execute('''
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solution TEXT UNIQUE,
                recognized_by TEXT,
                recognized INTEGER DEFAULT 0
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS times (
                method TEXT PRIMARY KEY,
                time_taken REAL
            )
        ''')

        conn.commit()
        logger.debug("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        conn.close()

def save_solution(solution):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO solutions (solution) VALUES (?)", (solution,))
    conn.commit()
    conn.close()

def record_time(method, time_taken):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO times (method, time_taken) VALUES (?, ?)", (method, time_taken))
    conn.commit()
    conn.close()

def recognize_solution(solution, player_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT recognized FROM solutions WHERE solution = ?", (solution,))
    row = c.fetchone()

    if row is None:
        conn.close()
        return False, "Solution not found."

    if row[0] == 1:
        conn.close()
        return False, "Solution already recognized."

    c.execute("UPDATE solutions SET recognized = 1, recognized_by = ? WHERE solution = ?", (player_name, solution))
    conn.commit()
    conn.close()
    return True, "Solution recognized!"

def all_solutions_recognized():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM solutions WHERE recognized = 0")
    count = c.fetchone()[0]
    conn.close()
    return count == 0

def reset_solutions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE solutions SET recognized = 0, recognized_by = NULL")
    conn.commit()
    conn.close()

# New function to get all stored data
def get_stored_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT solution, recognized_by, recognized FROM solutions")
    rows = c.fetchall()
    conn.close()
    
    # Return the stored data as a list of dictionaries for easier handling
    stored_data = []
    for row in rows:
        stored_data.append({
            'solution': row[0],
            'recognized_by': row[1],
            'recognized': row[2]
        })
    
    return stored_data
def get_stored_solutions():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT solution, recognized_by, recognized FROM solutions")
    rows = c.fetchall()
    conn.close()
    return rows
