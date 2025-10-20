<#
.SYNOPSIS
  Collect Windows server metrics and insert into SQLite.
.DESCRIPTION
  CPU, Memory, Disk (C:), and optional basic reachability for DNS.
  Requires System.Data.SQLite or uses sqlite3.exe if available. For simplicity, we write to a CSV and a small helper insert.
.NOTES
  Author: Atif Khan
#>

# Config
$DbPath = Join-Path (Split-Path $PSScriptRoot -Parent) "db\health.db"
$HostName = $env:COMPUTERNAME
$Timestamp = (Get-Date).ToUniversalTime()

# Metrics
$cpu = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples[0].CookedValue
$cpu = [math]::Round($cpu,2)

$mem_committed = (Get-Counter '\Memory\% Committed Bytes In Use').CounterSamples[0].CookedValue
$mem_committed = [math]::Round($mem_committed,2)

$disk = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'"
$disk_used = (($disk.Size - $disk.FreeSpace) / $disk.Size) * 100
$disk_used = [math]::Round($disk_used,2)

# Insert via sqlite3 CLI if present; otherwise, show output
$sqlite = Get-Command sqlite3 -ErrorAction SilentlyContinue
if ($sqlite) {
  $ts = $Timestamp.ToString("yyyy-MM-dd HH:mm:ss")
  & $sqlite.Source $DbPath "CREATE TABLE IF NOT EXISTS system_metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, hostname TEXT, ts DATETIME, cpu_percent REAL, mem_percent REAL, disk_percent REAL);" | Out-Null
  & $sqlite.Source $DbPath "INSERT INTO system_metrics(hostname, ts, cpu_percent, mem_percent, disk_percent) VALUES('$HostName','$ts',$cpu,$mem_committed,$disk_used);" | Out-Null
  Write-Host "Inserted metrics into $DbPath"
} else {
  Write-Host "sqlite3 not found. Metrics:"
  Write-Host "Host: $HostName"
  Write-Host "CPU: $cpu%"
  Write-Host "MEM: $mem_committed%"
  Write-Host "DISK: $disk_used%"
}