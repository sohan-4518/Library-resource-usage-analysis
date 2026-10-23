import os
from pathlib import Path
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
def connect():
    return psycopg.connect(host=os.getenv("DB_HOST","localhost"),port=int(os.getenv("DB_PORT","5432")),
      dbname=os.getenv("DB_NAME","library_analysis"),user=os.getenv("DB_USER","postgres"),
      password=os.getenv("DB_PASSWORD",""),row_factory=dict_row,connect_timeout=5)
def all_rows(sql,params=()):
    with connect() as c:
        with c.cursor() as cur:
            cur.execute(sql,params); return cur.fetchall()
def one_row(sql,params=()):
    with connect() as c:
        with c.cursor() as cur:
            cur.execute(sql,params); return cur.fetchone()
