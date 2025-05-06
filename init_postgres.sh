#!/bin/bash
# init_postgres.sh

set -e

# Wait for PostgreSQL to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL started, initializing database..."

# Run database initialization or migrations if needed
cd /app/backend
python -c "
from app.database.connection import Base, engine
from app.models.base import *
from app.models.user import User
from app.models.student import Student
from app.models.question import Question
from app.models.student_answer import StudentAnswer
from app.models.test import Test
from app.models.collection import Collection
from app.models.combination import Combination
from app.models.prompt import Prompt
from app.models.llm_response import LLMResponse

# Create all tables
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"

echo "Database initialization completed."
