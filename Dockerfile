FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define the user's home directory and add it to PATH
ENV HOME=/home/appuser
ENV PATH="${HOME}/.local/bin:${PATH}"

# Create a non-root user
RUN adduser \
    --system \
    --group \
    --home ${HOME} \
    --create-home \
    appuser

# Set workdir and copy requirements
WORKDIR ${HOME}/app
COPY --chown=appuser:appuser requirements.txt .

# Install dependencies as the non-root user
USER appuser
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Final Stage ----
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME=/home/appuser
ENV PATH="${HOME}/.local/bin:${PATH}"

# Create the same non-root user
RUN adduser --system --group --home ${HOME} --create-home appuser
# Set the working directory
WORKDIR ${HOME}/app
# Copy installed dependencies from the builder stage
COPY --from=builder --chown=appuser:appuser ${HOME}/.local ${HOME}/.local
# Copy the application code
COPY --chown=appuser:appuser . .
# Switch to the non-root user
USER appuser

EXPOSE 8080

# Use gunicorn to run uvicorn with multiple workers for production
# The number of workers can be adjusted. A common starting point is (2 * CPU_CORES) + 1
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8080"]
