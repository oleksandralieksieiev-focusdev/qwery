def is_safe_sql(sql: str) -> bool:
    # very basic safety checks: only allow single SELECT statement, deny modifying keywords
    s = sql.strip().lower()
    # require statement begins with select
    if not s.startswith("select"):
        return False
    # disallow dangerous keywords
    forbidden = ["insert ", "update ", "delete ", "drop ", "alter ", "create ", "truncate ", "grant ", "revoke ", "replace "]
    if any(k in s for k in forbidden):
        return False
    return True
