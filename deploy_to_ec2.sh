#!/bin/bash

# Configurable variables
EC2_USER="ec2-user"            # Change to 'ec2-user' if required
EC2_HOST="ec2-13-55-250-224.ap-southeast-2.compute.amazonaws.com"  # Replace with your EC2 instance public DNS/IP
EC2_KEY="S:\project\ayurveda\ACCESSKEY.pem"  # Path to the private key
IMAGE_NAME="anindya2369/ayurvedic-bot"   # Docker image repository/name
IMAGE_TAG="latest"               # Docker image tag, default to 'latest'
REMOTE_PORT=8080                   # Remote port mapping for the container

# Function to log messages
log() {
    echo "[INFO] $1"
}

# SSH into the EC2 instance and deploy the Docker container
log "Connecting to EC2 instance $EC2_HOST as $EC2_USER..."
# Pass necessary variables to the remote script
ssh -tt -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" << EOF
# Export variables passed from parent script
export IMAGE_NAME="$IMAGE_NAME"
export IMAGE_TAG="$IMAGE_TAG"
export REMOTE_PORT="$REMOTE_PORT"

set -e

# Function to log remote messages
log_remote() {
    echo "[REMOTE] $1"
}

# Ensure we're in the home directory
cd ~

# Set error handling
set -e
trap 'log_remote "An error occurred. Exiting..."; exit 1' ERR

log_remote "Checking if Docker is installed..."
if ! command -v docker &> /dev/null; then
    log_remote "Docker not found. Starting installation..."
    
    if command -v apt-get &>/dev/null; then
        log_remote "Detected apt-get: Ubuntu/Debian environment assumed. Installing Docker..."
        sudo apt-get update
        sudo apt-get install -y docker.io
    elif command -v dnf &>/dev/null; then
        log_remote "Detected dnf: Amazon Linux 2023 environment assumed. Running Docker installation commands..."
        sudo dnf update -y
        sudo dnf install -y docker
    elif command -v yum &>/dev/null; then
        log_remote "Detected yum: Amazon Linux 2/CentOS environment assumed. Installing Docker..."
        sudo yum update -y
        sudo yum install -y docker
    else
        log_remote "No supported package manager found to install Docker. Exiting..."
        exit 1
    fi
    
    sudo systemctl start docker
    sudo systemctl enable docker
    log_remote "Docker installation completed."
else
    log_remote "Docker is already installed."
fi

# Add user to docker group to avoid permission issues
log_remote "Adding current user to the docker group..."
if ! sudo usermod -aG docker $(whoami); then
    log_remote "Failed to add user to docker group. Continuing anyway..."
fi
# Restart Docker service
log_remote "Restarting Docker service..."
sudo systemctl restart docker

# Fix Docker permissions directly without using newgrp
log_remote "Setting Docker socket permissions..."
sudo chmod 666 /var/run/docker.sock
log_remote "Docker socket permissions updated."

# Verify Docker permissions and service status
log_remote "Checking Docker service status..."
sudo systemctl start docker || true
sudo systemctl status docker || true

# Wait for Docker to be fully operational
log_remote "Waiting for Docker to be fully operational..."
for i in {1..30}; do
    if docker info &>/dev/null; then
        log_remote "Docker is now operational"
        break
    fi
    log_remote "Waiting for Docker to be ready... ($i/30)"
    sleep 2
done

# Verify Docker is operational
if ! docker info &>/dev/null; then
    log_remote "Docker is not operational after waiting period. Trying with sudo..."
    if ! sudo docker info &>/dev/null; then
        log_remote "Docker is not operational even with sudo. Exiting..."
        exit 1
    else
        log_remote "Docker works with sudo. Will use sudo for all docker commands."
        DOCKER_CMD="sudo docker"
    fi
fi

log_remote "Docker permissions verified successfully."
# Set default docker command if not already set
if [ -z "$DOCKER_CMD" ]; then
    DOCKER_CMD="docker"
fi

# Verify Docker command works before proceeding
log_remote "Verifying Docker command functionality..."
if ! $DOCKER_CMD --version &>/dev/null; then
    log_remote "Docker command not functioning properly. Trying alternative approach..."
    DOCKER_CMD="sudo $(which docker)"
    if ! $DOCKER_CMD --version &>/dev/null; then
        log_remote "Docker command still not working. Exiting..."
        exit 1
    fi
fi

log_remote "Pulling Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
if ! $DOCKER_CMD pull ${IMAGE_NAME}:${IMAGE_TAG}; then
    log_remote "Failed to pull Docker image. Exiting..."
    exit 1
fi

log_remote "Stopping and removing any existing container named 'ayurveda_app'..."
if $DOCKER_CMD ps -a --format '{{.Names}}' | grep -q '^ayurveda_app$'; then
    $DOCKER_CMD stop ayurveda_app || true
    $DOCKER_CMD rm ayurveda_app || true
    log_remote "Existing container stopped and removed."
else
    log_remote "No existing container found."
fi

log_remote "Starting new Docker container..."
$DOCKER_CMD run -d --name ayurveda_app -p ${REMOTE_PORT}:8080 ${IMAGE_NAME}:${IMAGE_TAG}
log_remote "Docker container started successfully."

EOF

if [ $? -eq 0 ]; then
    log "Deployment script completed successfully."
    log "Verifying container is running..."
    ssh -tt -i "$EC2_KEY" "$EC2_USER@$EC2_HOST" "docker ps | grep ayurveda_app" && \
        log "Container is running properly." || \
        log "WARNING: Container may not be running correctly. Please check manually."
else
    log "Deployment script encountered an error."
    exit 1
fi

# Reminder: make sure to make this script executable using 'chmod +x deploy_to_ec2.sh'
