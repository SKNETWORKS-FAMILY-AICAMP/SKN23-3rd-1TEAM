import json
from utils.config import REMOTE_DB_PATH
from utils.ssh_utils import ssh_command


def fetch_remote_db(ip, query_type="users"):
    """SSH를 통해 원격 DB 정보를 조회"""
    if query_type == "users":
        sql = "SELECT * FROM users"
    elif query_type == "interviews":
        sql = "SELECT id, user_id, score, created_at FROM interviews ORDER BY id DESC LIMIT 10"
    else:
        return None

    # 원격에서 JSON으로 안전하게 응답받는 Python 스크립트 실행
    py_script = f"""
import sqlite3
import json
try:
    conn = sqlite3.connect('{REMOTE_DB_PATH}')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("{sql}")
    rows = cursor.fetchall()
    results = [dict(row) for row in rows]
    print(json.dumps(results))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
    py_cmd = f"python3 -c {json.dumps(py_script)}"
    out, err = ssh_command(ip, py_cmd)

    try:
        return json.loads(out)
    except Exception as e:
        return [{"error": "Parsing failed", "raw": out, "err": err}]


def run_remote_sql(ip, sql, args=None):
    """원격 DB 상에서 SQL 쿼리 실행
    SQL 인젝션 방지를 위해 args 파라미터 전달 기능 지원
    """

    # args가 튜플이나 딕셔너리로 넘어오는 경우 안전하게 직렬화하여 우회
    # (sqlite3.execute(sql, args) 방식 지원)
    args_json = json.dumps(args) if args else "None"

    py_script = f"""
import sqlite3
import json
try:
    conn = sqlite3.connect('{REMOTE_DB_PATH}')
    cursor = conn.cursor()
    args = json.loads('{args_json}')
    if args:
        cursor.execute("{sql}", args)
    else:
        cursor.execute("{sql}")
    conn.commit()
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {{str(e)}}")
"""
    py_cmd = f"python3 -c {json.dumps(py_script)}"
    out, _ = ssh_command(ip, py_cmd)

    return out.strip()
