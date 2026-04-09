#!/usr/bin/env python3
"""Reset stuck maestro provisioning.

Usage:
    python reset_maestro.py query <phonenumber>
    python reset_maestro.py bpm-cleanup <ticket_ids>
    python reset_maestro.py maestro-cleanup <trans_ids>
"""

import sys
import os

# Try to import oracledb, prompt user to install if missing
try:
    import oracledb
except ImportError:
    print("ERROR: oracledb module not found.")
    print("Please install it with:")
    print("  uv pip install --system oracledb")
    print("or if sudo is required:")
    print("  sudo uv pip install --system oracledb")
    sys.exit(1)

# Get the directory where this script is located (go up one level to find assets/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
CONN_FILE = os.path.join(PARENT_DIR, "assets", "CONNECTIONS.md")
QUERIES_FILE = os.path.join(PARENT_DIR, "assets", "QUERIES.md")


def get_connection_config():
    """Read connection config from CONNECTIONS.md file."""
    config = {}
    if not os.path.exists(CONN_FILE):
        raise FileNotFoundError(f"Connection config not found: {CONN_FILE}")

    with open(CONN_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("- "):
                parts = line[2:].split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()
                    if key == "host":
                        config["host"] = value
                    elif key == "port":
                        config["port"] = int(value)
                    elif key == "service":
                        config["service"] = value
                    elif key == "username":
                        config["user"] = value
                    elif key == "pasword":
                        config["password"] = value

    required = ["host", "port", "service", "user", "password"]
    missing = [k for k in required if k not in config]
    if missing:
        raise ValueError(f"Missing connection config: {missing}")

    return config


def get_queries():
    """Read queries from QUERIES.md file."""
    if not os.path.exists(QUERIES_FILE):
        raise FileNotFoundError(f"Queries file not found: {QUERIES_FILE}")

    with open(QUERIES_FILE, "r") as f:
        content = f.read()
    return content


def get_connection():
    """Create database connection using config from CONNECTIONS.md."""
    config = get_connection_config()
    dsn = oracledb.makedsn(
        config["host"], config["port"], service_name=config["service"]
    )
    return oracledb.connect(user=config["user"], password=config["password"], dsn=dsn)


def query_results(phonenumber):
    """Query maestro results for a phone number."""
    sql = """
SELECT
    bel.ticket_id AS ticket_id,
    bel.id AS event_id, 
    bel.bpm_process_name AS event, 
    bel.process_status AS event_status, 
    TO_CHAR(bel.start_time, 'YYYY-MM-DD HH:MI:SS') AS event_start, 
    TO_CHAR(bel.end_time, 'YYYY-MM-DD HH:MI:SS') AS event_end,
    replace(replace(bel.log_msg1,'[','_'),']','_') as log_msg1, 
    replace(replace(bel.log_msg2,'[','_'),']','_') as log_msg2, 
    replace(replace(bel.log_msg3,'[','_'),']','_') AS log_msg3, 
    bel.bpm_process_id, 
    bel.bpm_parent_process_id AS bpm_parent_id, 
    bel.manual_task, 
    bel.manual_task_id, 
    bel.manual_task_reason, 
    bel.server_host_name,
    mt.id AS trans_id, 
    mt.external_system AS source, 
    mt.member_phone, 
    mt.status AS trans_status, 
    mt.environment
FROM bpm_event_log bel
LEFT OUTER JOIN maestro_transactions mt ON bel.MAESTRO_ID = mt.ID
WHERE (mt.MEMBER_PHONE = :phone OR substr(bel.log_msg3, 5, 10) = :phone)
ORDER BY bel.start_time DESC
"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, {"phone": phonenumber})
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def bpm_cleanup(ticket_ids):
    """Reset BPM event log entries."""
    if not ticket_ids:
        return 0
    sql = """
UPDATE bpm_event_log 
SET process_status = 'FAILURE', end_time = start_time, log_msg1 = 'Internal provisioning error'
WHERE ticket_id IN ({}) AND process_status IN ('IN_PROGRESS','RETRY')
""".format(",".join(["'{}'".format(t) for t in ticket_ids]))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return rows


def maestro_cleanup(trans_ids):
    """Reset maestro transaction entries."""
    if not trans_ids:
        return 0
    sql = """
UPDATE maestro_transactions 
SET status = 'FAILURE', is_complete = 'Y', message = 'Manual completion', last_modified_date = SYSDATE
WHERE id IN ({})
""".format(",".join(["'{}'".format(t) for t in trans_ids]))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return rows


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "query":
        if len(sys.argv) < 3:
            print("Usage: python reset_maestro.py query <phonenumber>")
            sys.exit(1)
        phonenumber = sys.argv[2]
        results = query_results(phonenumber)
        for row in results:
            print(row)

    elif cmd == "bpm-cleanup":
        if len(sys.argv) < 3:
            print("Usage: python reset_maestro.py bpm-cleanup <ticket_ids>")
            sys.exit(1)
        # ticket_ids passed as comma-separated: id1,id2,id3
        ticket_ids = sys.argv[2].split(",")
        rows = bpm_cleanup(ticket_ids)
        print(f"Rows updated: {rows}")

    elif cmd == "maestro-cleanup":
        if len(sys.argv) < 3:
            print("Usage: python reset_maestro.py maestro-cleanup <trans_ids>")
            sys.exit(1)
        # trans_ids passed as comma-separated: id1,id2,id3
        trans_ids = sys.argv[2].split(",")
        rows = maestro_cleanup(trans_ids)
        print(f"Rows updated: {rows}")

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
