#!/usr/bin/env python3

import json
import re

from constants import MAX_ROWS

from db import get_db_conn
from llm import OllamaLLM
from template import SQL_PROMPT_TEMPLATE

from utils.safe_sql import is_safe_sql
from utils.fetch_schema import fetch_schema_text
from utils.run_sql import run_select
from utils.table import print_table

def main():
    question = input("> ").strip()
    if not question:
        print(json.dumps({"error": "No question provided on stdin"}))
        return

    # connect to DB and produce schema
    try:
        conn = get_db_conn()
    except Exception as e:
        print(json.dumps({"error": f"DB connection failed: {e}"}))
        return

    try:
        schema_text = fetch_schema_text(conn)
    except Exception as e:
        conn.close()
        print(json.dumps({"error": f"Failed to fetch schema: {e}"}))
        return

    # create LLM and prompt
    llm = OllamaLLM()
    prompt = SQL_PROMPT_TEMPLATE.format(schema=schema_text, question=question, max_rows=MAX_ROWS)

    # call LLM
    try:
        print("Invoking LLM. Please wait...")
        res = llm.invoke(prompt)
        # sanitize whitespace/newlines: keep single-line
        sql = " ".join(res.strip().splitlines()).strip()
        # remove deepseek thinking output
        sql = re.sub(r"\<think\>.*\<\/think\>", "", sql)
    except Exception as e:
        conn.close()
        print(json.dumps({"error": f"LLM call failed: {e}"}))
        return

    # Basic safety
    if not is_safe_sql(sql):
        conn.close()
        print(json.dumps({"error": "Generated SQL considered unsafe. Aborting.", "generated_sql": sql}))
        return

    # Execute
    try:
        cols, rows = run_select(conn, sql, limit=MAX_ROWS)
        rows_list = [list(r) for r in rows]

        print_table(cols, rows_list)
    except Exception as e:
        print(json.dumps({"error": f"SQL execution failed: {e}", "generated_sql": sql}))
    finally:
        conn.close()

if __name__ == "__main__":
    main()
