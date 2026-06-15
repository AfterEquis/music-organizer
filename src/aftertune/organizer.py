import shutil
import time
from pathlib import Path

import requests
from mutagen import File

from .utils import safe_name, parse_filename, clean_stem


def genre_from_tags(path: Path) -> str | None:
    """Lee el tag genre del archivo si existe."""
    try:
        audio = File(path, easy=True)
        if audio and audio.get("genre"):
            return safe_name(audio["genre"][0])
    except Exception:
        pass
    return None


def genre_from_musicbrainz(path: Path, email: str) -> str | None:
    """Busca el género en MusicBrainz de forma inteligente."""
    headers = {"User-Agent": f"MusicOrganizer/1.0 ({email or 'user@example.com'})"}
    title, artist = None, None

    try:
        audio = File(path, easy=True)
        if audio:
            title  = (audio.get("title")  or [None])[0]
            artist = (audio.get("artist") or [None])[0]
    except Exception:
        pass

    if not title:
        artist, title = parse_filename(path.stem)

    # Lista de consultas de mayor a menor precisión
    queries = []
    if artist and title:
        queries.append(f'recording:"{title}" AND artist:"{artist}"')
    if title:
        queries.append(f'recording:"{title}"')
    # Fallback: búsqueda difusa con el nombre del archivo limpio
    queries.append(clean_stem(path.stem))

    for query in queries:
        try:
            r = requests.get(
                "https://musicbrainz.org/ws/2/recording",
                params={"query": query, "fmt": "json", "limit": 1},
                headers=headers, timeout=10,
            )
            r.raise_for_status()
            recordings = r.json().get("recordings", [])
            if not recordings:
                continue

            # Intentar obtener tags del release-group
            releases = recordings[0].get("releases", [])
            rg_id = None
            if releases:
                rg_id = releases[0].get("release-group", {}).get("id")
            
            # Si no hay release-group, mirar tags del artista
            artist_id = recordings[0].get("artist-credit", [{}])[0].get("artist", {}).get("id")

            genre = None
            # 1. Intentar por Release Group (más preciso para el álbum/canción)
            if rg_id:
                time.sleep(1)
                res = requests.get(f"https://musicbrainz.org/ws/2/release-group/{rg_id}",
                                 params={"inc": "tags", "fmt": "json"}, headers=headers, timeout=10)
                tags = res.json().get("tags", [])
                if tags:
                    genre = max(tags, key=lambda t: t.get("count", 0))["name"].title()

            # 2. Fallback al Artista (si el álbum no tiene tags)
            if not genre and artist_id:
                time.sleep(1)
                res = requests.get(f"https://musicbrainz.org/ws/2/artist/{artist_id}",
                                 params={"inc": "tags", "fmt": "json"}, headers=headers, timeout=10)
                tags = res.json().get("tags", [])
                if tags:
                    genre = max(tags, key=lambda t: t.get("count", 0))["name"].title()

            if genre:
                return safe_name(genre)

        except Exception as e:
            print(f"  ⚠ MusicBrainz ({query[:20]}...): {e}")
        
        time.sleep(1) # Respetar límites de la API

    return None


def move_file(file: Path, genre: str, dest_dir: Path):
    target_dir = dest_dir / genre
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / file.name

    if target.exists():
        i = 1
        while True:
            candidate = target_dir / f"{file.stem} ({i}){file.suffix}"
            if not candidate.exists():
                target = candidate
                break
            i += 1

    shutil.move(str(file), str(target))
    return target


def genre_from_rules(path: Path, cfg: dict) -> str | None:
    """Intenta determinar el género basándose en palabras clave en el título/nombre."""
    t = path.stem.lower()

    # Reglas por palabras clave en el título/nombre
    if cfg.get("rules"):
        for kw, genre in cfg["rules"].items():
            if kw.lower() in t:
                return genre

    return None


def genre_from_itunes(path: Path) -> str | None:
    """Busca el género en la API de iTunes como fallback."""
    artist, title = parse_filename(path.stem)
    term = f"{artist} {title}" if artist else title
    try:
        r = requests.get("https://itunes.apple.com/search", 
                         params={"term": term, "media": "music", "limit": 1},
                         timeout=10)
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results:
                return safe_name(results[0].get("primaryGenreName", "").title())
    except Exception:
        pass
    return None

def simplify_genre(genre: str, genre_map: dict) -> str:
    """Simplifica un género específico a una categoría genérica usando el mapeo."""
    if not genre or not genre_map:
        return genre

    # Normalizar para búsqueda
    g_search = genre.strip()

    # 1. Búsqueda exacta
    if g_search in genre_map:
        return genre_map[g_search]

    # 2. Búsqueda por subcadena (ej: "Melodic Death Metal" -> "Metal")
    for specific, generic in genre_map.items():
        if specific.lower() in g_search.lower():
            return generic

    return genre


def organize_file(path: Path, dest_dir: Path, cfg: dict) -> str:
    """Obtiene el género y mueve el archivo. Devuelve el género asignado."""
    unknown_folder = cfg.get("unknown_folder", "Unknown")
    genre_map = cfg.get("genre_map", {})

    # Prioridad 1: Tags existentes
    genre = genre_from_tags(path)
    if genre:
        print(f"  → (tag) {genre}")
    else:
        # Prioridad 2: Reglas locales (Rules)
        genre = genre_from_rules(path, cfg)
        if genre:
            print(f"  → (regla local) {genre}")
        else:
            # Prioridad 3: MusicBrainz
            genre = genre_from_musicbrainz(path, cfg.get("email", ""))
            if genre:
                print(f"  → (MusicBrainz) {genre}")
            else:
                # Prioridad 4: iTunes
                genre = genre_from_itunes(path)
                if genre:
                    print(f"  → (iTunes) {genre}")
                else:
                    genre = unknown_folder
                    print(f"  → {unknown_folder}")

    # Aplicar simplificación de género si no es Unknown
    if genre != unknown_folder:
        old_genre = genre
        genre = simplify_genre(genre, genre_map)
        if genre != old_genre:
            print(f"  ⚡ Simplificado: {old_genre} → {genre}")

    move_file(path, genre, dest_dir)
    return genre



def organize_folder(src: Path, dest: Path, cfg: dict):
    """Organiza todos los archivos de una carpeta con reporte final."""
    extensions = cfg.get("extensions", [".mp3", ".flac"])
    unknown_folder = cfg.get("unknown_folder", "Unknown")
    
    files = [f for f in src.rglob("*") if f.suffix.lower() in extensions and f.is_file()]
    total = len(files)

    if total == 0:
        print("No se encontraron archivos de audio.")
        return

    stats = {}
    print(f"\n🚀 Procesando {total} archivos de: {src}\n")
    
    for i, file in enumerate(files, 1):
        print(f"[{i}/{total}] {file.name}")
        genre = organize_file(file, dest, cfg)
        stats[genre] = stats.get(genre, 0) + 1

    print("\n" + "═"*30)
    print("      REPORTE DE ORGANIZACIÓN")
    print("═"*30)
    for genre in sorted(stats.keys()):
        count = stats[genre]
        color = "\033[93m" if genre == unknown_folder else "\033[92m"
        print(f"  {color}{genre:15}{count:>3} archivo{'s' if count > 1 else ''}\033[0m")
    print("═"*30)
    print(f"  Total: {total} archivos procesados.\n")

    # Si es Termux, notificar al escáner de medios sobre la carpeta destino en segundo plano
    from .config import IS_TERMUX
    if IS_TERMUX:
        try:
            import subprocess
            subprocess.Popen(["termux-media-scan", str(dest)],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        except Exception:
            pass
