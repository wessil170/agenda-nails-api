import sqlite3

def get_connection():
    return sqlite3.connect("database.db")

def criar_tabela():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            data TEXT,
            horario TEXT,
            servico TEXT
        )
    """)

    conn.commit()
    conn.close()
