import shutil
import time
from pathlib import Path

import requests
from mutagen import File

from utils import safe_name, parse_filename


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
    """Busca el género en MusicBrainz usando tags o nombre del archivo."""
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

    query = f'recording:"{title}"'
    if artist:
        query += f' AND artist:"{artist}"'

    try:
        r = requests.get(
            "https://musicbrainz.org/ws/2/recording",
            params={"query": query, "fmt": "json", "limit": 1},
            headers=headers, timeout=10,
        )
        r.raise_for_status()
        recordings = r.json().get("recordings", [])
        if not recordings:
            return None

        releases = recordings[0].get("releases", [])
        if not releases:
            return None

        rg_id = releases[0].get("release-group", {}).get("id")
        if not rg_id:
            return None

        time.sleep(1)
        rg = requests.get(
            f"https://musicbrainz.org/ws/2/release-group/{rg_id}",
            params={"inc": "tags", "fmt": "json"},
            headers=headers, timeout=10,
        )
        rg.raise_for_status()
        tags = rg.json().get("tags", [])
        if tags:
            best = max(tags, key=lambda t: t.get("count", 0))
            return safe_name(best["name"].title())

    except Exception as e:
        print(f"  ⚠ MusicBrainz: {e}")

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


def organize_file(path: Path, dest_dir: Path, email: str, unknown_folder: str = "Unknown") -> str:
    """Obtiene el género y mueve el archivo. Devuelve el género asignado."""
    genre = genre_from_tags(path)
    if genre:
        print(f"  → (tag) {genre}")
    else:
        genre = genre_from_musicbrainz(path, email)
        if genre:
            print(f"  → (MusicBrainz) {genre}")
            time.sleep(1)
        else:
            genre = unknown_folder
            print(f"  → {unknown_folder}")

    move_file(path, genre, dest_dir)
    return genre


def organize_folder(src: Path, dest: Path, email: str, extensions: list, unknown_folder: str):
    """Organiza todos los archivos de una carpeta."""
    files = [f for f in src.rglob("*") if f.suffix.lower() in extensions and f.is_file()]
    total = len(files)

    if total == 0:
        print("No se encontraron archivos de audio.")
        return

    print(f"\n{total} archivos encontrados.\n")
    for i, file in enumerate(files, 1):
        print(f"[{i}/{total}] {file.name}")
        organize_file(file, dest, email, unknown_folder)

    print("\n─── Resultado ───")
    for d in sorted(dest.iterdir()):
        if d.is_dir():
            n = len(list(d.iterdir()))
            print(f"  {d.name}/  ({n} archivo{'s' if n > 1 else ''})")
