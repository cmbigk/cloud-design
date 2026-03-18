#!/bin/sh

cat <<EOF > /etc/rabbitmq/rabbitmq.conf
loopback_users.guest = false
default_user = ${RABBITMQ_DEFAULT_USER:-guest}
default_pass = ${RABBITMQ_DEFAULT_PASS:-guest}
EOF

exec rabbitmq-server "$@"
