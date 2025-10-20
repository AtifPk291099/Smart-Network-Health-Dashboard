-- Optional sample data
INSERT INTO system_metrics(hostname, ts, cpu_percent, mem_percent, disk_percent)
VALUES
('server-local', '2025-10-20 10:00:00', 35.2, 62.0, 71.0),
('server-local', '2025-10-20 10:05:00', 82.0, 70.5, 72.0),
('server-local', '2025-10-20 10:10:00', 40.1, 65.0, 73.0);

INSERT INTO network_metrics(target_name, target_ip, ts, latency_ms, reachable)
VALUES
('Gateway', '192.168.1.1', '2025-10-20 10:00:00', 2.5, 1),
('DNS', '8.8.8.8', '2025-10-20 10:00:00', 35.0, 1),
('AppServer', '192.168.1.50', '2025-10-20 10:00:00', -1.0, 0);

INSERT INTO ai_insights(ts, entity, type, message, score)
VALUES
('2025-10-20 10:10:00', 'server-local', 'anomaly', 'Anomaly: unusual CPU spike detected.', -0.25),
('2025-10-20 10:10:00', 'server-local', 'forecast', 'Forecast: Disk usage may reach ~78.0% soon.', 78.0);