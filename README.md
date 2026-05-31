# 🎵 AfterTune

> Descarga canciones desde YouTube y las organiza automáticamente por género.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Termux](https://img.shields.io/badge/Termux-000000?style=for-the-badge&logo=android&logoColor=white)
![yt-dlp](https://img.shields.io/badge/yt--dlp-FF0000?style=for-the-badge&logo=youtube&logoColor=white)

---

## ¿Qué hace?

- 🔍 **Búsqueda Inteligente:** Filtra automáticamente reacciones, covers y karaokes para darte la versión real.
- 🌍 **Detección de Género Global:** Utiliza **MusicBrainz** e **iTunes API** para clasificar cada canción en su género exacto.
- 🎸 **Organización Automática:** La música se organiza sola en su carpeta de género (`Rock/`, `Pop/`, `Reggaeton/`...)
- 💾 **Gestión de Bibliotecas:** Organiza carpetas enteras o discos externos (USB) moviendo archivos a una estructura limpia.
- 🚀 **Lanzador One-Click:** Configuración automática de entorno para usuarios que no quieren usar la terminal.
- 🌐 **Multiplataforma:** Compatible con Linux, Windows, macOS y Termux.

---

## Uso (Recomendado)

Para usuarios de Linux/macOS, simplemente ejecuta el lanzador automático:

```bash
./aftertune.sh
```

Este script se encargará de todo: crear el entorno virtual, instalar las dependencias y lanzar la aplicación.

### Uso Manual

Si prefieres hacerlo a mano:

```bash
source .venv/bin/activate
python main.py
```

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
Búsqueda de género (Inteligencia en Red)
    │  1. Tags ID3 del archivo
    │  2. MusicBrainz API (Álbum -> Artista)
    │  3. iTunes Search API (Fallback de alta velocidad)
    │  4. Reglas de palabras clave (Local)
    │  5. Unknown/
    ▼
Mover a Destino/[Género]/canción.mp3
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
