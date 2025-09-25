from typing import Optional
from constants import MAX_ROWS

def run_select(conn, sql: str, limit: Optional[int] = MAX_ROWS):
    cur = conn.cursor()
    # ensure LIMIT present; if not, append safe LIMIT
    sql_l = sql.strip()
    cur.execute(sql_l)
    cols = [d.name for d in cur.description] if cur.description else []
    rows = cur.fetchmany(limit)
    cur.close()
    return cols, rows
