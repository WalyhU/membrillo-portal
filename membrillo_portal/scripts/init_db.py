"""Fallback: carga schema + seed sin depender de docker init dir.
Util si MySQL ya existe sin pasar por /docker-entrypoint-initdb.d.
"""
import os
import sys
from pathlib import Path

import pymysql
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
SQL_FILES = [ROOT / "sql" / "01_schema.sql", ROOT / "sql" / "02_seed.sql"]

DB_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:membrillo@localhost:3306/membrillo_db")
# Parse simple: mysql+pymysql://user:pass@host:port/db
url = DB_URL.replace("mysql+pymysql://", "")
creds, rest = url.split("@", 1)
user, password = creds.split(":", 1)
hostport, db_name = rest.split("/", 1)
host, port = hostport.split(":") if ":" in hostport else (hostport, "3306")

print(f"Conectando a {host}:{port} db={db_name} user={user} ...")
conn = pymysql.connect(host=host, port=int(port), user=user, password=password, autocommit=True)
cur = conn.cursor()
cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4")
cur.execute(f"USE {db_name}")

for sql_file in SQL_FILES:
    print(f"Ejecutando {sql_file.name}...")
    sql_text = sql_file.read_text(encoding="utf-8")
    # split por ;
    for stmt in sql_text.split(";"):
        stmt = stmt.strip()
        if not stmt or stmt.startswith("--"):
            continue
        try:
            cur.execute(stmt)
        except pymysql.err.Warning:
            pass
        except Exception as e:
            print(f"  WARN al ejecutar: {stmt[:80]}... -> {e}")

cur.close()
conn.close()
print("Listo. BD cargada.")
