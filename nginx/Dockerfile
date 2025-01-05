# Usa l'immagine ufficiale di NGINX
FROM nginx:latest

# Installa apache2-utils per avere il comando htpasswd
RUN apt-get update && \
    apt-get install -y apache2-utils

# Crea la cartella per i file di configurazione e le chiavi
RUN mkdir -p /etc/nginx/keys

# Crea il file .htpasswd con username e password
#RUN echo "user1:$(htpasswd -bnB user1 password123)" > /etc/nginx/keys/.htpasswd

# Copia la configurazione nginx.conf nella configurazione di NGINX
COPY nginx.conf /etc/nginx/nginx.conf

# Esponi la porta 80 per il traffico HTTP
EXPOSE 80

# Comando di avvio di NGINX
CMD ["nginx", "-g", "daemon off;"]
