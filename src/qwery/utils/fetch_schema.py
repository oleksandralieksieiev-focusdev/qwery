def fetch_schema_text(conn) -> str:
    # produce a simple schema description: tables and columns + types for public schema
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type='BASE TABLE'
        ORDER BY table_name;
    """)
    tables = [r[0] for r in cur.fetchall()]
    parts = []
    for t in tables:
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name=%s
            ORDER BY ordinal_position;
        """, (t,))
        cols = cur.fetchall()
        col_lines = [f"  - {c[0]}: {c[1]}" for c in cols]
        parts.append(f"Table {t}:\n" + "\n".join(col_lines))
    cur.close()
    if not parts:
        return "No tables found in public schema."
    return "\n\n".join(parts)
