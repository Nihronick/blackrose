import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
import sys

# Set encoding to avoid issues on Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent

# Load env from backend/.env
load_dotenv(ROOT / "backend" / ".env")

DATABASE_URL = os.getenv("DIRECT_URL") or os.getenv("DATABASE_URL")
SQL_FILE = SCRIPT_DIR / "import_neon_safe.sql"


def split_sql_statements(sql: str):
    """Split SQL text into statements, respecting quoted strings."""
    statements = []
    current = []
    in_single_quote = False
    i = 0

    while i < len(sql):
        ch = sql[i]

        if ch == "'":
            if in_single_quote:
                # Escaped single quote inside SQL string: ''
                if i + 1 < len(sql) and sql[i + 1] == "'":
                    current.append(ch)
                    current.append(sql[i + 1])
                    i += 2
                    continue
                in_single_quote = False
            else:
                in_single_quote = True
            current.append(ch)
            i += 1
            continue

        if ch == ";" and not in_single_quote:
            stmt = "".join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
            i += 1
            continue

        current.append(ch)
        i += 1

    tail = "".join(current).strip()
    if tail:
        statements.append(tail)

    return statements

def execute_sql():
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in backend/.env")
        return
    
    if not SQL_FILE.exists():
        print(f"Error: {SQL_FILE} not found")
        return
    
    print("Reading SQL file...")
    sql = SQL_FILE.read_text(encoding="utf-8")
    statements = split_sql_statements(sql)

    if not statements:
        print("Error: no SQL statements found")
        return

    print(f"Loaded {len(statements)} SQL statements")
    
    # Try full import with retries
    max_retries = 3
    for attempt in range(max_retries):
        conn = None
        cur = None
        executed_count = 0
        try:
            print(f"Connecting to database (attempt {attempt + 1}/{max_retries})...")
            conn = psycopg2.connect(DATABASE_URL, connect_timeout=30)
            conn.autocommit = False
            cur = conn.cursor()

            print("Executing SQL commands...")
            for idx, stmt in enumerate(statements, start=1):
                try:
                    cur.execute(stmt)
                    executed_count += 1
                    
                    # Commit frequently for stability  
                    if idx % 10 == 0:
                        conn.commit()
                        print(f"  [{idx}/{len(statements)}] Checkpoint saved", flush=True)
                        
                except Exception as e:
                    print(f"  Error at statement {idx}: {e}")
                    conn.rollback()
                    raise

            # Final commit
            conn.commit()
            print(f"SUCCESS: Database updated! Executed {executed_count}/{len(statements)} statements")
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            if cur is not None:
                try:
                    cur.close()
                except Exception:
                    pass
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            # Do not retry on SQL errors
            break
        except Exception as e:
            print(f"FAILURE: Error during execution: {e}")
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            if cur is not None:
                try:
                    cur.close()
                except Exception:
                    pass
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
            break

if __name__ == "__main__":
    execute_sql()
