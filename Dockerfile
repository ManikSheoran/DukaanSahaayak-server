FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV HOME=/home/appuser
ENV PATH="${HOME}/.local/bin:${PATH}"

RUN addgroup --system appuser && \
    adduser --system --ingroup appuser --create-home ${HOME} appuser

WORKDIR ${HOME}/app

COPY --chown=appuser:appuser requirements.txt .

USER appuser

RUN pip install --no-cache-dir --user -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
