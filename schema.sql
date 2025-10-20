-- SQLite schema
CREATE TABLE IF NOT EXISTS system_metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  hostname TEXT,
  ts DATETIME,
  cpu_percent REAL,
  mem_percent REAL,
  disk_percent REAL
);

CREATE TABLE IF NOT EXISTS network_metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  target_name TEXT,
  target_ip TEXT,
  ts DATETIME,
  latency_ms REAL,
  reachable INTEGER
);

CREATE TABLE IF NOT EXISTS ai_insights (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts DATETIME,
  entity TEXT,
  type TEXT,
  message TEXT,
  score REAL
);