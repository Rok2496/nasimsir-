#!/bin/bash

# Exit on any error
set -e

# Run database migrations if needed (optional)
# alembic upgrade head

# Start the FastAPI application
python -m uvicorn main:app --host 0.0.0.0 --port $PORT