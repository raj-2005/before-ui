# app/tools/file.py
'''
from pathlib import Path


def read_file(path: str) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return file_path.read_text()


def write_file(path: str, content: str) -> str:
    file_path = Path(path)

    file_path.write_text(content)

    return f"File written successfully to {path}"

'''

import sqlite3
from pathlib import Path
from typing import List, Dict, Any

# Database file will be created in your root directory
DB_PATH = "project_data.db"

# --- EXISTING FILE LOGIC (Preserved) ---

def read_file(path: str) -> str:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return file_path.read_text()


def write_file(path: str, content: str) -> str:
    file_path = Path(path)
    file_path.write_text(content)
    return f"File written successfully to {path}"


# --- NEW DATABASE LOGIC (Added) ---

def query_database(search_query: str) -> List[Dict[str, Any]]:
    """
    Connects to SQLite and searches for records matching the query.
    """
    conn = sqlite3.connect(DB_PATH)
    # This allows us to access columns by name like a dictionary
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    # Ensure table exists before querying
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, name TEXT, details TEXT)
    """)
    
    # Search in name, details, or category
    sql = "SELECT * FROM records WHERE name LIKE ? OR details LIKE ? OR category LIKE ?"
    param = f"%{search_query}%"
    cursor.execute(sql, (param, param, param))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert Row objects to standard Python dictionaries
    return [dict(row) for row in rows]


def write_to_db(category: str, name: str, details: str) -> str:
    """
    Inserts a new record into the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, name TEXT, details TEXT)
    """)
    
    cursor.execute(
        "INSERT INTO records (category, name, details) VALUES (?, ?, ?)",
        (category, name, details)
    )
    
    conn.commit()
    conn.close()
    return f"✅ Data for '{name}' successfully saved to database."