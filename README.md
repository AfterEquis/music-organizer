# 🎵 AfterTune

> Descarga canciones desde YouTube y las organiza automáticamente por género.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Termux](https://img.shields.io/badge/Termux-000000?style=for-the-badge&logo=android&logoColor=white)
![yt-dlp](https://img.shields.io/badge/yt--dlp-FF0000?style=for-the-badge&logo=youtube&logoColor=white)

---

## ¿Qué hace?

- 🔍 Buscas una canción por nombre — filtra automáticamente reacciones, covers y karaokes
- ⭐ El mejor resultado aparece marcado; pulsa Enter para descargarlo o elige un número
- 🎸 La canción se organiza sola en su carpeta de género (`Rock/`, `Pop/`, `Reggaeton/`...)
- 🌐 Compatible con Linux, Windows, macOS y Termux

---

## Demo

```
╔══════════════════════════════════════╗
║       🎵  AfterTune                  ║
╚══════════════════════════════════════╝

  Carpeta: ~/Music

  [1] Buscar y descargar canción
  [2] Organizar carpeta existente
  [3] Configuración
  [4] Salir

  Opción: 1
  Nombre o URL: bad bunny neverita

  Búsqueda: bad bunny neverita
  ───────────────────────────────────────────────────────

★ [1] Bad Bunny - Neverita  · Bad Bunny · 3:12 · 320M views
  [2] Bad Bunny - Neverita (Video Oficial) · BadBunnyVevo · 3:14
  [3] Bad Bunny - Neverita (Letra/Lyrics) · LetrasHD · 3:12

  Opción: ↵

  🎵 Título   Bad Bunny - Neverita
  👤 Artista  Bad Bunny
  🎸 Género   Reggaeton
  📁 Destino  ~/Music/Reggaeton/Bad Bunny - Neverita.mp3
```

---

## Instalación

```bash
git clone https://github.com/AfterEquis/music-organizer.git
cd music-organizer
pip install -r requirements.txt
```

### Activar entorno virtual (opcional pero recomendado)

| Sistema | Comando |
|---|---|
| Linux / macOS / Termux (bash/zsh) | `source .venv/bin/activate` |
| Linux / macOS (fish) | `source .venv/bin/activate.fish` |
| Windows | `.venv\Scripts\activate` |

---

## Uso

```bash
python main.py
```

En la primera ejecución te pedirá tu carpeta de música y un email para MusicBrainz (necesario para la búsqueda de géneros).

---

## Cómo funciona por dentro

```
Nombre/URL
    │
    ▼
Búsqueda YouTube (yt-dlp)
    │  filtra reacciones, covers, karaokes
    ▼
Descarga en temp (webm → mp3/flac/m4a)
    │
    ▼
Búsqueda de género
    │  1. Tags ID3 del archivo
    │  2. MusicBrainz API
    │  3. Last.fm API (opcional)
    │  4. Unknown/
    ▼
Mover a ~/Music/[Género]/canción.mp3
```

---

## Problemas frecuentes

**`ModuleNotFoundError: mutagen`**
```bash
pip install mutagen requests yt-dlp
```

**`pip: Unknown command` en fish**
```bash
python3 -m pip install -r requirements.txt
```

---

## Por [AfterEquis](https://github.com/AfterEquis)
