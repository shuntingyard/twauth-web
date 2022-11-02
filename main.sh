#!/bin/bash
trap "deactivate; systemctl start nginx" SIGINT SIGTERM SIGHUP

systemctl stop nginx
. venv/bin/activate

hypercorn                                                           \
    --access-logfile -                                              \
    --certfile  /etc/letsencrypt/live/bitcrack.dev/fullchain.pem    \
    --keyfile   /etc/letsencrypt/live/bitcrack.dev/privkey.pem      \
    --bind bitcrack.dev:443 twauth-web:app
