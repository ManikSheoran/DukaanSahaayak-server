# ---- Builder Stage ----
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/appuser \
    PATH="${HOME}/.local/bin:${PATH}"

# Create a non-root user (without --create-home)
RUN adduser --system --group --home ${HOME} appuser

# Set working directory and copy requirements
WORKDIR ${HOME}/app
COPY --chown=appuser:appuser requirements.txt ./

# Install dependencies as non-root user
USER appuser
RUN pip install --no-cache-dir --user -r requirements.txt


# ---- Final Stage ----
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/appuser \
    PATH="${HOME}/.local/bin:${PATH}"

# Create the same non-root user
RUN adduser --system --group --home ${HOME} appuser

# Set working directory
WORKDIR ${HOME}/app

# Copy installed Python packages from builder
COPY --from=builder --chown=appuser:appuser ${HOME}/.local ${HOME}/.local

# Copy application code
COPY --chown=appuser:appuser . .


USER appuser

EXPOSE 8080

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:${PORT}"]
