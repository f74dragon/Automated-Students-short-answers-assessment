FROM ollama/ollama:latest

# Install tools needed for hardware detection
RUN apt-get update && apt-get install -y \
    pciutils \
    lshw \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy our custom entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
