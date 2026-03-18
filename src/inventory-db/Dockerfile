# 3.23 is the latest version of alpine so 3.22 is penultimate
FROM alpine:3.22

# Install PostgreSQL and create required directories in one layer
RUN apk add --no-cache postgresql postgresql-contrib && \
    mkdir -p /run/postgresql /var/lib/postgresql/data && \
    chown -R postgres:postgres /run/postgresql /var/lib/postgresql/data

USER postgres
WORKDIR /var/lib/postgresql

# Copy init script and ensure permissions
# Note: we copy as postgres user directly if possible, or chmod as root
USER root
COPY init.sh /init.sh
RUN chmod +x /init.sh
USER postgres

EXPOSE 5432

ENTRYPOINT ["/init.sh"]
