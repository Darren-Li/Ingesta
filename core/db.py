import sqlite3
from datetime import datetime

DB_NAME = "app.db"

def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS dv_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        schema_json TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS dg_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        desc TEXT,
        schema_json TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS dv_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        template_id INTEGER,
        status TEXT,
        error TEXT,
        file_name TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS dg_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        template_id INTEGER,
        rows INTEGER,
        cost DOUBLE,
        file_name TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def delete_task(table, task_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"DELETE FROM {table} WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

def delete_template(table, template_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"DELETE FROM {table} WHERE id=?", (template_id,))
    conn.commit()
    conn.close()
