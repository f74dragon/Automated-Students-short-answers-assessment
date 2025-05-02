@echo off
cd /d "C:\Program Files\PostgreSQL\17\bin"
psql -U postgres -h localhost -d postgres -c "CREATE ROLE \"user\" LOGIN PASSWORD 'mypassword';"
psql -U postgres -h localhost -d postgres -c "CREATE DATABASE mydatabase OWNER \"user\";"