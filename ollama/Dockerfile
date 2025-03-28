FROM ollama/ollama:latest

# Install tools needed for hardware detection
RUN apt-get update && apt-get install -y \
    pciutils \
    lshw \
    hwinfo \
    lsof \
    procps \
    && (apt-get install -y nvidia-utils-525 || true) \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create NVIDIA compatibility links in case they're needed
RUN mkdir -p /usr/local/nvidia/lib64 || true

# Copy our custom entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
