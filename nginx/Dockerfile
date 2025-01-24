FROM nginx:latest

RUN apt-get update && \
    apt-get install -y apache2-utils

# Crea la cartella per i file di configurazione e le chiavi
RUN mkdir -p /etc/nginx/keys

# Crea il file .htpasswd con username e password
#RUN echo "user1:$(htpasswd -bnB user1 password123)" > /etc/nginx/keys/.htpasswd

COPY nginx.conf /etc/nginx/nginx.conf
#COPY healthcheck.sh /usr/src/app/healthcheck.sh

#RUN chmod +x /usr/src/app/healthcheck.sh

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
