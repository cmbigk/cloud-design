#!/bin/sh

if [ ! -s "/var/lib/postgresql/data/PG_VERSION" ]; then
    echo "Initializing database cluster..."
    initdb -D /var/lib/postgresql/data
    echo "listen_addresses='*'" >> /var/lib/postgresql/data/postgresql.conf
    echo "host all all 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf
    
    pg_ctl start -D /var/lib/postgresql/data -w
    psql -c "CREATE USER ${POSTGRES_USER} WITH SUPERUSER PASSWORD '${POSTGRES_PASSWORD}';" || true
    psql -c "ALTER USER ${POSTGRES_USER} WITH SUPERUSER PASSWORD '${POSTGRES_PASSWORD}';"
    psql -c "CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER};" || true
    pg_ctl stop -D /var/lib/postgresql/data -m fast
fi

# Finally drop privileges to postgres if needed (we are already postgres user)
exec postgres -D /var/lib/postgresql/data
