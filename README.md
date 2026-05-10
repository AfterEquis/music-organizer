# 🎵 Music Organizer

Descargador y organizador de música por género. Descarga canciones o playlists de YouTube con yt-dlp y las categoriza automáticamente usando MusicBrainz.

## Características

- Descarga canciones o playlists completas desde YouTube
- Organiza por género en el momento de la descarga (sin pasos extra)
- Busca el género primero en los tags del archivo, luego en MusicBrainz
- Parsea el nombre del archivo si no hay tags disponibles
- Maneja duplicados automáticamente
- Funciona en Linux, Windows y Termux (Android)

## Requisitos

- Python 3.10+
- ffmpeg instalado en el sistema

### Instalar ffmpeg

**Linux / Termux:**
```bash
# Arch / CachyOS
sudo pacman -S ffmpeg

# Debian / Ubuntu
sudo apt install ffmpeg

# Termux
pkg install ffmpeg
```

**Windows:**
Descarga desde https://ffmpeg.org y añade al PATH, o usa `winget`:
```powershell
winget install ffmpeg
```

## Instalación

```bash
git clone https://github.com/tuusuario/music-organizer
cd music-organizer
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

En la primera ejecución te pedirá la carpeta de música y tu email (necesario para la API de MusicBrainz).

### Menú principal

```
[1] Descargar canción / playlist y organizar   ← descarga + categoriza al instante
[2] Organizar carpeta existente                ← para música que ya tienes
[3] Configuración
[4] Salir
```

### Estructura de carpetas resultante

```
~/Music/
├── Reggaeton/
│   ├── Bad_Bunny_-_Neverita.mp3
│   └── BAD_BUNNY_x_JHAY_CORTEZ_-_DÁKITI.mp3
├── Pop/
│   └── Aitana_-_SENTIMIENTO_NATURAL.mp3
├── Hip-Hop/
│   └── ...
└── Unknown/
    └── canciones_sin_género.mp3
```

## Configuración

Se guarda en `config.json` (se crea automáticamente):

```json
{
  "music_dir": "/home/user/Music",
  "email": "tu@email.com",
  "extensions": [".mp3", ".flac", ".ogg", ".m4a", ".wav"],
  "unknown_folder": "Unknown"
}
```

## Notas

- MusicBrainz permite 1 request/segundo. Para carpetas grandes el proceso puede tardar varios minutos.
- Las canciones sin género conocido van a la carpeta `Unknown/`.
- Si el nombre del archivo sigue el formato `Artista - Título`, la búsqueda en MusicBrainz es más precisa.
