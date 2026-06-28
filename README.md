# Personal Cassette Player

Un piccolo player musicale nato come app desktop Python e affiancato da un
frontend React/Vite in stile Y2K hyperpop.

## Frontend React/Vite

La nuova interfaccia web include:

- caricamento di un file audio locale
- play e pausa
- controllo volume
- barra di avanzamento
- visualizzatore con barrette audio animate
- look da cassette player futuristico Y2K/hyperpop

### Avvio frontend

Installa Node.js, poi dalla cartella del progetto:

```bat
npm install
npm run dev
```

Apri l'indirizzo mostrato dal terminale, di solito:

```text
http://localhost:5173
```

## Versione Python desktop

Un piccolo player musicale desktop creato in Python.

Questa versione e pensata per Windows e non richiede VLC. Usa Windows Media
Player tramite `pywin32`.

### Funzionalita

- selezione file musicali locali
- playlist interna
- play
- pausa
- stop
- brano successivo
- brano precedente
- rimozione brano dalla playlist
- controllo volume

### Formati

Supporta i formati riproducibili dal sistema Windows, tra cui di solito:

- MP3
- WAV
- AAC
- M4A

Altri formati come FLAC/OGG dipendono dai codec presenti sul PC.

### Requisiti desktop

- Windows
- Python 3
- pywin32

### Avvio desktop

Da Anaconda Prompt:

```bat
pip install -r requirements.txt
python main.py
```

Oppure doppio click su:

```text
run.bat
```

### Possibile errore su Windows Media Player

Se compare un errore relativo a `WMPlayer.OCX`, potrebbe essere necessario
abilitare Windows Media Player:

1. Apri Impostazioni Windows
2. Vai su App
3. Apri Funzionalita opzionali
4. Aggiungi una funzionalita
5. Cerca Windows Media Player
6. Installa

## Struttura progetto

```text
personal-cassette-player/
|-- src/
|   |-- main.jsx
|   `-- styles.css
|-- index.html
|-- package.json
|-- vite.config.js
|-- main.py
|-- requirements.txt
|-- README.md
|-- run.bat
`-- .gitignore
```

## Obiettivo

Progetto semplice per imparare Python, React, Vite e GitHub.
