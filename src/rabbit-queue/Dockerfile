#FROM debian:bullseye-slim
FROM debian:oldstable-slim

# Install RabbitMQ and setup environment in one layer to minimize size
RUN apt-get update && \
    apt-get install -y --no-install-recommends rabbitmq-server && \
    mkdir -p /var/lib/rabbitmq /var/log/rabbitmq /etc/rabbitmq && \
    chown -R rabbitmq:rabbitmq /var/lib/rabbitmq /var/log/rabbitmq /etc/rabbitmq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/lib/rabbitmq/mnesia

# Use COPY with chmod for efficiency if supported, or follow with RUN
COPY init.sh /init.sh
RUN chmod +x /init.sh

USER rabbitmq
EXPOSE 5672

ENTRYPOINT ["/init.sh"]
