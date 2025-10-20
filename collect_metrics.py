#!/usr/bin/env python3
"""
Collect system and network metrics, write to SQLite.
- System: CPU, Memory, Disk
- Network: Ping selected targets
"""

import psutil
import sqlite3
import time
import datetime
import subprocess
import csv
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "db" / "health.db"
TARGETS_CSV = Path(__file__).resolve().parent / "sample_network_targets.csv"

def ensure_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS system_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT,
        ts DATETIME,
        cpu_percent REAL,
        mem_percent REAL,
        disk_percent REAL
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS network_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_name TEXT,
        target_ip TEXT,
        ts DATETIME,
        latency_ms REAL,
        reachable INTEGER
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ai_insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts DATETIME,
        entity TEXT,         -- hostname or target ip
        type TEXT,           -- anomaly | forecast
        message TEXT,
        score REAL
    )""")
    con.commit()
    con.close()

def collect_system_metrics():
    hostname = psutil.users()[0].name if psutil.users() else "server-local"
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return hostname, cpu, mem, disk

def ping(ip: str, count=1, timeout=1):
    # Cross-platform ping (Windows uses -n, Linux/Mac use -c)
    import platform
    param = "-n" if platform.system().lower().startswith("win") else "-c"
    cmd = ["ping", param, str(count), "-W", str(timeout), ip]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        success = out.returncode == 0
        latency = None
        if success:
            # Try to parse latency from output
            for line in out.stdout.splitlines():
                if "time=" in line:
                    try:
                        latency = float(line.split("time=")[1].split()[0].replace("ms",""))
                        break
                    except:
                        pass
        return success, latency if latency is not None else -1.0
    except Exception:
        return False, -1.0

def read_targets():
    targets = []
    with open(TARGETS_CSV, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            targets.append((row["name"], row["ip"]))
    return targets

def insert_system(con, hostname, cpu, mem, disk):
    con.execute("INSERT INTO system_metrics(hostname, ts, cpu_percent, mem_percent, disk_percent) VALUES (?,?,?,?,?)",
                (hostname, datetime.datetime.utcnow(), cpu, mem, disk))

def insert_network(con, name, ip, latency_ms, reachable):
    con.execute("INSERT INTO network_metrics(target_name, target_ip, ts, latency_ms, reachable) VALUES (?,?,?,?,?)",
                (name, ip, datetime.datetime.utcnow(), latency_ms, 1 if reachable else 0))

def main():
    ensure_db()
    con = sqlite3.connect(DB_PATH)

    # System metrics
    hostname, cpu, mem, disk = collect_system_metrics()
    insert_system(con, hostname, cpu, mem, disk)

    # Network metrics
    for name, ip in read_targets():
        ok, latency = ping(ip)
        insert_network(con, name, ip, latency, ok)

    con.commit()
    con.close()
    print("Metrics collected and stored.")

if __name__ == "__main__":
    main()