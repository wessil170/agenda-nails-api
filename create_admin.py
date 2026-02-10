import sqlite3
from passlib.context import CryptContext

# contexto bcrypt correto
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

EMAIL = "admin@teste.com"
SENHA = "123456"

hash_senha = pwd_context.hash(SENHA)

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# garante que a tabela existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password_hash TEXT
)
""")

# limpa admins antigos (ambiente de teste)
cursor.execute("DELETE FROM admins")

# cria admin novo
cursor.execute(
    "INSERT INTO admins (email, password_hash) VALUES (?, ?)",
    (EMAIL, hash_senha)
)

conn.commit()
conn.close()

print("✅ Admin recriado com sucesso")
print("Email:", EMAIL)
print("Senha:", SENHA)
