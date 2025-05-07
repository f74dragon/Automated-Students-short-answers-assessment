#!/bin/bash
docker stop my-ubuntu-container 2>/dev/null && docker rm my-ubuntu-container 2>/dev/null

docker build -t my-ubuntu-dev .

docker run -it \
  -p 3000:80 \
  -p 8001:8001 \
  -p 5432:5432 \
  -p 11434:11434 \
  --name my-ubuntu-container \
  my-ubuntu-dev
