import sqlite3
from db.config import DB_PATH

conn = sqlite3.connect(str(DB_PATH))
tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    ).fetchall()

print("DB: ", DB_PATH)
print("Tabelas: ", [t[0] for t in tables])
conn.close()