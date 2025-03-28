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

# Enhanced NVIDIA GPU detection (checking first since user has NVIDIA)
# Debug info
log "Debug: Checking for NVIDIA devices"
ls -la /dev/nvidia* 2>/dev/null || log "Debug: No /dev/nvidia* devices found"

# Method 1: Check NVIDIA devices
HAS_NVIDIA=0
if ls /dev/nvidia* &>/dev/null; then
    log "NVIDIA device files found"
    HAS_NVIDIA=1
fi

# Method 2: Check using nvidia-smi
if command -v nvidia-smi &>/dev/null; then
    log "Debug: nvidia-smi command exists"
    if nvidia-smi -L &>/dev/null; then
        log "NVIDIA GPU detected via nvidia-smi"
        HAS_NVIDIA=1
        # Log GPU info for debugging
        nvidia-smi -L | while read line; do
            log "Debug: $line"
        done
    else
        log "nvidia-smi command exists but failed to list devices"
    fi
fi

# Method 3: Check for NVIDIA libraries
if [ -d "/usr/local/cuda" ] || [ -d "/usr/local/nvidia" ]; then
    log "NVIDIA CUDA libraries detected"
    HAS_NVIDIA=1
fi

# Method 4: Check PCI devices
if lspci | grep -i "NVIDIA" | grep -i -E '(VGA|3D|Display)' &>/dev/null; then
    log "NVIDIA GPU detected via PCI"
    HAS_NVIDIA=1
    # Log GPU info for debugging
    log "Debug: PCI NVIDIA devices:"
    lspci | grep -i "NVIDIA" | while read line; do
        log "Debug: $line"
    done
fi

# Configure NVIDIA if detected
if [ "$HAS_NVIDIA" = "1" ]; then
    log "NVIDIA GPU detected, configuring environment"
    # Set NVIDIA environment variables
    export NVIDIA_VISIBLE_DEVICES=all
    export CUDA_VISIBLE_DEVICES=0
    # Additional variables that might help
    export NVIDIA_DRIVER_CAPABILITIES=compute,utility
    MODEL_ARGS="--gpu"
    
# Try to detect AMD GPUs if NVIDIA not found
elif [ -d "/dev/dri" ] && (lspci | grep -i 'amd' | grep -i 'radeon\|gpu\|vga\|3d\|display' &>/dev/null); then
    log "AMD GPU detected"
    # Configure ROCm environment if available
    export HSA_OVERRIDE_GFX_VERSION=10.3.0
    # Expose AMD device
    export ROCR_VISIBLE_DEVICES=0
    # Enable ROCm 
    export HIP_VISIBLE_DEVICES=0
    # Tell Ollama to use GPU
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
