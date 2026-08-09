#!/bin/sh
set -e

echo "Waiting for PostgreSQL database to be ready..."
python -c "
import socket
import time
import sys

port = 5432
host = 'db'
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(3)
start_time = time.time()
while True:
    try:
        s.connect((host, port))
        s.close()
        print('PostgreSQL is up and running!')
        break
    except socket.error:
        if time.time() - start_time > 60:
            print('Timeout waiting for PostgreSQL!')
            sys.exit(1)
        time.sleep(1)
"

echo "Initializing database, tables, admin user, and Git repository..."
python scripts/init_db.py

echo "Starting FastAPI API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
