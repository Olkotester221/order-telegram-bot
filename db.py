import sqlite3

def init_db():
    conn = sqlite3.connect("orders.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            service TEXT,
            client_name TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_order(user_id, username, service, client_name, phone):
    conn = sqlite3.connect("orders.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (user_id, username, service, client_name, phone) VALUES (?, ?, ?, ?, ?)",
        (user_id, username, service, client_name, phone)
    )
    conn.commit()
    conn.close()