#!/usr/bin/env python3
"""
AI: Anomaly detection + simple forecasting on stored metrics.
- IsolationForest to flag anomalies in CPU/MEM/DISK
- Linear regression to forecast disk usage trend
Writes AI insights back into SQLite.
"""

import sqlite3
import datetime
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "db" / "health.db"

def fetch_system_metrics(hostname=None, limit=200):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    if hostname:
        cur.execute("SELECT ts, cpu_percent, mem_percent, disk_percent FROM system_metrics WHERE hostname=? ORDER BY ts DESC LIMIT ?", (hostname, limit))
    else:
        cur.execute("SELECT ts, cpu_percent, mem_percent, disk_percent FROM system_metrics ORDER BY ts DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    con.close()
    return rows

def write_insight(entity, type_, message, score=None):
    con = sqlite3.connect(DB_PATH)
    con.execute("INSERT INTO ai_insights(ts, entity, type, message, score) VALUES (?,?,?,?,?)",
                (datetime.datetime.utcnow(), entity, type_, message, None if score is None else float(score)))
    con.commit()
    con.close()

def detect_anomalies(hostname="server-local"):
    rows = fetch_system_metrics(hostname=hostname, limit=100)
    if len(rows) < 20:
        return  # not enough data

    X = np.array([[cpu, mem, disk] for _, cpu, mem, disk in rows])
    model = IsolationForest(contamination=0.1, random_state=42)
    preds = model.fit_predict(X)
    scores = model.decision_function(X)

    # Flag last point if anomalous
    last_pred = preds[0]
    last_score = scores[0]
    last_ts = rows[0][0]
    if last_pred == -1:
        msg = f"Anomaly at {last_ts}: unusual CPU/MEM/DISK pattern."
        write_insight(hostname, "anomaly", msg, last_score)

def forecast_disk(hostname="server-local"):
    rows = list(reversed(fetch_system_metrics(hostname=hostname, limit=50)))  # chronological
    if len(rows) < 10:
        return

    y = np.array([disk for _, _, _, disk in rows])
    X = np.arange(1, len(y)+1).reshape(-1, 1)

    model = LinearRegression().fit(X, y)
    future_idx = np.array([[len(y)+3]])  # forecast 3 steps ahead
    pred = model.predict(future_idx)[0]

    msg = f"Forecast: Disk usage may reach ~{pred:.1f}% in 3 intervals."
    write_insight(hostname, "forecast", msg, pred)

def main():
    detect_anomalies()
    forecast_disk()
    print("AI insights updated.")

if __name__ == "__main__":
    main()