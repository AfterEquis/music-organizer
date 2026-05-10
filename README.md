# 🎵 AfterTune

Descarga canciones desde YouTube y las organiza automáticamente por género en tu ordenador.

Funciona en Linux, Windows, Mac y Termux.

---

## ¿Qué hace?

- Buscas una canción por nombre (o pegas la URL directamente).
- Te muestra los mejores resultados filtrados, sin reacciones ni covers.
- Descargas con Enter o eligiendo un número.
- La canción se mueve sola a su carpeta de género.

---

## Requisitos

- Python 3.8 o superior
- Conexión a internet

---

## Instalación

```bash
git clone https://github.com/AfterEquis/music-organizer.git
cd music-organizer
python3 -m pip install -r requirements.txt
```

### En fish (Linux)
```bash
source .venv/bin/activate.fish
```

### En bash/zsh (Linux, Mac)
```bash
source .venv/bin/activate
```

### En Windows
```cmd
.venv\Scripts\activate
```

---

## Uso

```bash
python main.py
```

---

## Problemas frecuentes

**`ModuleNotFoundError: mutagen`**
```bash
python3 -m pip install mutagen requests yt-dlp
```

**`pip: Unknown command` en fish**
```bash
python3 -m pip install -r requirements.txt
```

**`source .venv/bin/activate` falla en fish**
```bash
source .venv/bin/activate.fish
```

---

## Por AfterEquis
