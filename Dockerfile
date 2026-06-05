FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY preemptcore/ ./preemptcore/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

ENTRYPOINT ["preemptcore"]
CMD ["--help"]
