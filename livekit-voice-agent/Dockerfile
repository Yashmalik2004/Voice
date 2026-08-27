# Production Dockerfile for LiveKit Voice Agent + Web UI
# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13
ARG NODE_VERSION=20

# --- Frontend Build Stage ---
FROM node:${NODE_VERSION}-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Base Python Stage ---
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim AS base
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1

# --- Python Build Stage ---
FROM base AS build
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked
RUN uv run --module livekit.agents download-files
COPY . .
# Copy compiled frontend from frontend-build stage
COPY --from=frontend-build /frontend/dist ./frontend/dist

# --- Production Image ---
FROM base
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

WORKDIR /app
COPY --from=build --chown=appuser:appuser /app /app
USER appuser

EXPOSE 7880

# Starts both the token & web server on port 7880 AND registers the LiveKit RTC worker
CMD ["uv", "run", "agent.py", "start"]
