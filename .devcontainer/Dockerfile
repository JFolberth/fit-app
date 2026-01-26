# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git curl build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Azure CLI (for IaC deployments)
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Install Azure Developer CLI (azd)
RUN curl -fsSL https://aka.ms/install-azd.sh | bash

# Node is provided via devcontainer feature; ensure playwright dependencies (optional)
RUN npm -v >/dev/null 2>&1 || true

WORKDIR /workspaces/fit-app
