\# Smart Network Health Dashboard



Small, unique, multi-tech project:

\- Python: metrics collection + AI (anomaly \& forecast)

\- PowerShell: Windows server metrics

\- Database: SQLite (portable, no setup)

\- Networking: ping targets

\- Java: Spring Boot REST + minimal dashboard

\- AI: IsolationForest + Linear Regression



\## Setup



1\. Create DB and seed

```bash

sqlite3 db/health.db < db/schema.sql

sqlite3 db/health.db < db/seed.sql

