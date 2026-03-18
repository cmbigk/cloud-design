# Stage 1: Build stage
FROM alpine:3.22 AS builder

# Install build dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev

WORKDIR /app

# Create a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage
FROM alpine:3.22

# Install only runtime dependencies
RUN apk add --no-cache \
    python3 \
    libpq

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the app files
COPY . .

# Usually rabbitmq workers don't expose ports but we can run it like this
EXPOSE 8080

CMD ["python", "run.py"]
