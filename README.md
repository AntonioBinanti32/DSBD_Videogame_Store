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

1. Decommentare solo il **1° URL** nel file `frontend/config.ini`.
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
2. Modificare il file `/etc/hosts` con privilegi amministrativi, aggiungendo la seguente riga:
    ```
    127.0.0.1 store.com
   ```
3. Decommentare solo il **2° URL** nel `file frontend/config.ini`.
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
