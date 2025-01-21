# Videogame Store

Il progetto **"Videogame Store"** è stato sviluppato per creare una piattaforma di e-commerce dedicata alla vendita di videogiochi. L'obiettivo principale è fornire un'interfaccia utente intuitiva e funzionale che permetta agli utenti di navigare, cercare, acquistare e recensire videogiochi in modo semplice e veloce.

## Caratteristiche Principali

Le principali funzionalità del Videogame Store includono:

- **Catalogo di Videogiochi**: Un catalogo di videogiochi personalizzato in base alle preferenze passate dell’utente. Gli utenti possono sfogliare e filtrare i giochi in base a titolo, prezzo e genere.
- **Sistema di Ricerca**: Una funzionalità di ricerca avanzata che consente agli utenti di trovare videogiochi specifici utilizzando parole chiave, filtri e ordinamenti.
- **Carrello e Acquisti**: Un carrello virtuale dove gli utenti possono aggiungere i giochi 
desiderati e procedere con l'acquisto. 
- **Recensioni e Valutazioni**: Gli utenti possono lasciare recensioni e valutazioni sui giochi acquistati, aiutando altri acquirenti a fare scelte più informate.
- **Sistema di Notifiche**: 
  - Gli utenti ricevono notifiche ogni volta che viene aggiunto o modificato un videogioco nello store.
  - Gli amministratori vengono avvisati ogni volta che un utente effettua un'azione su un videogioco.

## Installazione

È possibile installare l'applicazione utilizzando **Docker Compose** o **Kubernetes**.

### Installazione con Docker Compose

1. Decommentare solo il **1° URL** nel file `frontend/config.ini` ed eliminare un eventuale immagine creata precedentemente.
2. Via terminale spostarsi nella cartella dove si trova il file `docker-compose.yml` ed seguire il comando:
   ```bash
   docker-compose up --build
   ```
3. Attendere circa 1-2 minuti affinché tutti i servizi siano avviati.
4. Accedere all'applicazione dal browser all'indirizzo: [http://localhost:3004/](http://localhost:3004/)

### Installazione con Kubernetes

1. Installare **Ingress NGINX** eseguendo il seguente comando:
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml
    ```
2. Modificare il file `/etc/hosts` con privilegi amministrativi, aggiungendo le seguenti righe:
    ```
    127.0.0.1 store.com
    127.0.0.1 store-grafana.com
   ```
3. Decommentare solo il **2° URL** nel `file frontend/config.ini` ed eliminare un eventuale immagine creata precedentemente.
4. Creare le immagini Docker per ogni servizio:
   - Posizionarsi nelle directory contenenti i file `Dockerfile` dei seguenti servizi:
     - `frontend`
     - `game-catalog`
     - `order-service`
     - `notification-service`
   - Eseguire il comando:
     ```bash
     docker build -t <nome_servizio>:1.0 .
     ```
5. Avviare l'applicazione eseguendo:
    ```bash
    kubectl apply -f k8s.yml
    ```
6. Attendere l'avvio dei servizi. In caso di malfunzionamento delle notifiche, riavviare il pod del servizio `notification-service`.

7. Accedere all'applicazione dal browser all'indirizzo: [http://store.com/login](http://store.com/login)

## Accesso in Modalità Admin
Per accedere alla modalità amministratore, utilizzare le seguenti credenziali:
- Username: `admin`
- Password: `0000`

## Monitoring white-box
### Monitoring con **Grafana**
1. Dalla distribuzione tramite **Docker-compose** andare su [http://localhost:3005/](http://localhost:3005/) o tramite **Kubernetes** su [http://store-grafana.com](http://store-grafana.com)
2. Accedere inserendo le seguenti credenziali:
- Username: `admin`
- Password: `admin`
3. Aggiungere **Prometheus** come data source
   1. Andare su `Home>Connections>Data sources>Add data source` e selezionare `Prometheus`
   2. Nella pagina di configurazione di Prometheus inserire come **URL** `http://prometheus:9090` (se si sta usando **docker-compose**) o `http://prometheus.default.svc.cluster.local:9090` (se si sta usando **Kubernetes**) e cliccare su '`Save & Test`'
4. Creazione di una Dashboard per visualizzare le metriche
   1. Nella barra laterale selezionare `+` e poi `Dashboard`.
   2. Cliccare su `Add new panel`.
   3. Nella sezione di configurazione del pannello:
      - `Metriche`: Scegliere Prometheus come data source.
      - Nella barra di ricerca delle metriche, digitare le metriche come `http_requests_total` e `http_request_duration_seconds`, per visualizzare le statistiche sulle richieste HTTP.
   4. Cliccare su `Apply` per aggiungere il pannello alla dashboard.

### Monitoring con **Prometheus**
1. Andare su [http://localhost:9090](http://localhost:9090).
2. Nella parte superiore, nwlla sezione `Graph` scrivere le query Prometheus come `http_requests_total` e `http_request_duration_seconds` e clicca su "Execute" per visualizzare i dati.

### Metriche **Prometheus**
Le metriche per il monitoring **white-box** inserite sono:
  - `http_requests_total`
  - `http_request_duration_seconds`
  - `db_requests_total`
  - `db_request_duration_seconds`
  - `kafka_messages_processed_total`

## Monitoring black-box
Il monitoring **black-box** è stato realizzato tramite **Cadvisor**, per accedervi utilizzare **Grafana** come illustrato nella sezione precedente.
Tra le metriche inserite da **Cadvisor vi sono:
  - `container_cpu_usage_seconds_total`
  - `container_memory_usage_bytes`
  - `container_fs_reads_bytes_total` 
  - `container_fs_writes_bytes_total`
  - `container_network_receive_bytes_total`
  - `container_network_transmit_bytes_total`
  - `container_blkio_sync_total`
  - `container_blkio_async_total`
  - `container_blkio_sectors_total`
  - `container_start_time_seconds`
  - `container_fs_usage_bytes`
  - `container_cpu_load_average_1m`
  - `container_fs_limit_bytes`
  - `container_last_event_timestamp`