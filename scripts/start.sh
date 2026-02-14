#!/bin/bash
set -e

echo "Waiting for database to be ready..."
until PGPASSWORD=camargue_password psql -h db -U camargue_user -d camargue_sailing -c '\q' 2>/dev/null; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is ready!"

echo "Initializing database tables..."
python scripts/init_db.py

echo "Starting Flask application..."
exec flask run --host=0.0.0.0
