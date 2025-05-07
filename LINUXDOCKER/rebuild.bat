@echo off
REM Stop and remove existing container if it exists
docker stop my-ubuntu-container >nul 2>&1
docker rm my-ubuntu-container >nul 2>&1

REM Build the Docker image
docker build -t my-ubuntu-dev .

REM Run the container with the specified ports
docker run -it ^
  -p 3000:80 ^
  -p 8001:8001 ^
  -p 5432:5432 ^
  -p 11434:11434 ^
  --name my-ubuntu-container ^
  my-ubuntu-dev
