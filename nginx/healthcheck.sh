#!/bin/bash

# Per ontrollare se il container è già in salute
if [ -f "/usr/src/app/healthcheck_success" ]; then
  exit 0  # Il container è già sano, esci con successo
fi

curl -f http://game-catalog:3001/ && \
curl -f http://order-service:3002/ && \
curl -f http://notification-service:3003/

if [ $? -eq 0 ]; then
  touch /usr/src/app/healthcheck_success
  exit 0
fi

exit 1
