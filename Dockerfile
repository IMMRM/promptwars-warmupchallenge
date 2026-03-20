# ── Stage 1: Build ────────────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /app

# Install dependencies first (leverages Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Runtime ──────────────────────────────────────────────────
FROM python:3.13-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ ./app/
COPY main.py .
COPY .streamlit/ ./.streamlit/

# Create non-root user for security
RUN useradd --create-home appuser
USER appuser

# Cloud Run sets PORT env var (default 8080); Streamlit needs to listen on it
ENV PORT=8080

# Expose the port
EXPOSE ${PORT}

# Health check (works locally; Cloud Run uses its own probes)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/_stcore/health || exit 1

# Run Streamlit on the Cloud Run port
# Using shell form so $PORT is expanded at runtime
CMD streamlit run main.py \
    --server.port=${PORT} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --browser.gatherUsageStats=false
