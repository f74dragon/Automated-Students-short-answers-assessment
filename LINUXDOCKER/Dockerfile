FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt update && apt install -y \
    git python3 python3-venv python3-pip \
    nodejs npm \
    postgresql postgresql-contrib curl

# Copy setup script
COPY setup.sh /setup.sh
RUN chmod +x /setup.sh

# Expose port 3000 for the React frontend or any app
EXPOSE 3000
EXPOSE 8001
EXPOSE 80
EXPOSE 5432
EXPOSE 11434

# Set working directory
WORKDIR /project

# Run the setup script on container startup
CMD /setup.sh && bash

