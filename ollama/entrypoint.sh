#!/bin/bash
set -e

# Function to log messages
log() {
    echo "[GPU-DETECTION] $1"
}

# Default configuration - CPU mode
MODEL_ARGS=""
export OLLAMA_NUM_THREADS=4

# Detect available GPU hardware
log "Detecting available GPU hardware..."

# Try to detect NVIDIA GPUs
if [ -e /dev/nvidia0 ] || command -v nvidia-smi &>/dev/null; then
    if nvidia-smi &>/dev/null; then
        log "NVIDIA GPU detected"
        # If CUDA is available, let Ollama use it
        # No need to explicitly configure - Ollama will auto-detect NVIDIA
        export CUDA_VISIBLE_DEVICES=0
        MODEL_ARGS="--gpu"
    else
        log "NVIDIA device found but driver not working properly"
    fi
# Try to detect AMD GPUs
elif [ -d "/dev/dri" ] && (lspci | grep -i 'amd' | grep -i 'radeon\|gpu' &>/dev/null); then
    log "AMD GPU detected"
    # Configure ROCm environment if available
    export HSA_OVERRIDE_GFX_VERSION=10.3.0
    # Some AMD-specific optimizations could go here
    MODEL_ARGS="--gpu"
# Try to detect Intel GPUs
elif [ -d "/dev/dri" ] && (lspci | grep -i 'intel' | grep -i 'graphics' &>/dev/null); then
    log "Intel integrated GPU detected"
    # Intel GPU specific environment
    export INTEL_OPENCL_CONFIG_DIR=/etc/OpenCL/vendors
    MODEL_ARGS="--gpu"
else
    log "No GPU detected, using CPU optimization"
    # Optimize for CPU usage
    export OLLAMA_NUM_THREADS=8
    MODEL_ARGS=""
fi

log "Starting Ollama with configuration: MODEL_ARGS='$MODEL_ARGS'"

# Execute the original Ollama command
exec ollama serve
