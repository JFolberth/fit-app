# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/devcontainers/python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git curl build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Azure CLI and azd are installed via devcontainer features

WORKDIR /workspaces/fit-app
