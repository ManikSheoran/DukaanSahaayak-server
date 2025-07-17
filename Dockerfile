FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define the user's home directory
ENV HOME=/home/appuser
ENV PATH="${HOME}/.local/bin:${PATH}"

# Create the appuser
RUN adduser \
    --system \
    --group \
    --home ${HOME} \
    --create-home \
    appuser
# Set the working directory
WORKDIR ${HOME}/app
# Copy and install requirements
COPY --chown=appuser:appuser requirements.txt .
USER appuser
RUN pip install --no-cache-dir --user -r requirements.txt
# Copy the application
COPY --chown=appuser:appuser . .

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
