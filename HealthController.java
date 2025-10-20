package com.atif.dashboard;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.sql.*;
import java.util.*;

@RestController
public class HealthController {

    @Value("${dashboard.db.path}")
    private String dbPath;

    private Connection connect() throws SQLException {
        String url = "jdbc:sqlite:" + dbPath;
        return DriverManager.getConnection(url);
    }

    @GetMapping("/api/system")
    public List<Map<String, Object>> system() throws SQLException {
        try (Connection con = connect();
             PreparedStatement ps = con.prepareStatement(
                     "SELECT hostname, ts, cpu_percent, mem_percent, disk_percent FROM system_metrics ORDER BY ts DESC LIMIT 20");
             ResultSet rs = ps.executeQuery()) {
            List<Map<String, Object>> list = new ArrayList<>();
            while (rs.next()) {
                Map<String, Object> row = new HashMap<>();
                row.put("hostname", rs.getString(1));
                row.put("ts", rs.getString(2));
                row.put("cpu", rs.getDouble(3));
                row.put("mem", rs.getDouble(4));
                row.put("disk", rs.getDouble(5));
                list.add(row);
            }
            return list;
        }
    }

    @GetMapping("/api/network")
    public List<Map<String, Object>> network() throws SQLException {
        try (Connection con = connect();
             PreparedStatement ps = con.prepareStatement(
                     "SELECT target_name, target_ip, ts, latency_ms, reachable FROM network_metrics ORDER BY ts DESC LIMIT 20");
             ResultSet rs = ps.executeQuery()) {
            List<Map<String, Object>> list = new ArrayList<>();
            while (rs.next()) {
                Map<String, Object> row = new HashMap<>();
                row.put("name", rs.getString(1));
                row.put("ip", rs.getString(2));
                row.put("ts", rs.getString(3));
                row.put("latency", rs.getDouble(4));
                row.put("reachable", rs.getInt(5) == 1);
                list.add(row);
            }
            return list;
        }
    }

    @GetMapping("/api/ai")
    public List<Map<String, Object>> ai() throws SQLException {
        try (Connection con = connect();
             PreparedStatement ps = con.prepareStatement(
                     "SELECT ts, entity, type, message, score FROM ai_insights ORDER BY ts DESC LIMIT 20");
             ResultSet rs = ps.executeQuery()) {
            List<Map<String, Object>> list = new ArrayList<>();
            while (rs.next()) {
                Map<String, Object> row = new HashMap<>();
                row.put("ts", rs.getString(1));
                row.put("entity", rs.getString(2));
                row.put("type", rs.getString(3));
                row.put("message", rs.getString(4));
                row.put("score", rs.getObject(5));
                list.add(row);
            }
            return list;
        }
    }

    @GetMapping("/")
    public String home() {
        return """
            <html>
              <head>
                <title>Smart Network Health Dashboard</title>
                <style>
                  body { font-family: Arial, sans-serif; background: #0f2027; color: #fff; }
                  .card { background: #243b55; border-radius: 8px; padding: 16px; margin: 12px; }
                  h1 { text-align: center; }
                  h2 { color: #00d4ff; }
                  table { width: 100%; border-collapse: collapse; }
                  th, td { padding: 8px; border-bottom: 1px solid #40607a; }
                  .grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
                </style>
              </head>
              <body>
                <h1>Smart Network Health Dashboard</h1>
                <div class="grid">
                  <div class="card">
                    <h2>System Metrics</h2>
                    <iframe src="/api/system" style="width:100%;height:220px;background:#0f2027;color:#fff;"></iframe>
                  </div>
                  <div class="card">
                    <h2>Network Metrics</h2>
                    <iframe src="/api/network" style="width:100%;height:220px;background:#0f2027;color:#fff;"></iframe>
                  </div>
                  <div class="card">
                    <h2>AI Insights</h2>
                    <iframe src="/api/ai" style="width:100%;height:220px;background:#0f2027;color:#fff;"></iframe>
                  </div>
                </div>
                <p style="text-align:center;margin-top:20px;color:#9bd1ff">
                  Data updates when collectors run. Try scheduling Python & PowerShell scripts.
                </p>
              </body>
            </html>
            """;
    }
}