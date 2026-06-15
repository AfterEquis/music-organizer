import re
import math
import time
import shutil
import tempfile
import requests
from pathlib import Path

import yt_dlp
from mutagen import File

from .utils import safe_name, parse_filename

YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

PENALTY_WORDS = [
    "reaccion", "reaccionando", "reaction", "reacting",
    "cover", "karaoke", "tutorial", "parodia", "parody",
    "gameplay", "compilation", "compilacion", "mix",
    "extended", "slowed", "reverb", "nightcore",
    "hora", "hours", "completo",
    "videoclip", "video oficial", "official video", "music video", "clip"
]
BONUS_WORDS = ["official", "oficial", "audio", "vevo", "lyrics", "letra", "topic", "visualizer"]
GENRE_RULES = [
    ("bachata", "Bachata"),
    ("salsa", "Salsa"),
    ("cumbia", "Cumbia"),
    ("merengue", "Merengue"),
    ("trap", "Trap Latino"),
    ("reggaeton", "Reggaeton"),
    ("reggaetón", "Reggaeton"),
    ("perreo", "Reggaeton"),
    ("dembow", "Reggaeton"),
    ("afrobeat", "Afrobeat"),
    ("afrobeats", "Afrobeat"),
    ("acoustic", "Acoustic"),
    ("acustic", "Acoustic"),
    ("piano", "Acoustic"),
    ("live", "Live"),
    ("concert", "Live"),
    ("tour", "Live"),
]
CHANNEL_RULES = [
    ("vevo", "Pop"),
    ("badbunny", "Urbano Latino"),
    ("anuel", "Urbano Latino"),
    ("feid", "Urbano Latino"),
    ("jhay", "Urbano Latino"),
    ("quevedo", "Urbano Latino"),
    ("aitana", "Pop"),
    ("mora", "Urbano Latino"),
    ("manuelturizo", "Urbano Latino"),
]


def _fmt_bytes(n) -> str:
    if not n:
        return "?"
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f} MB"
    if n >= 1_000:
        return f"{n/1_000:.1f} KB"
    return f"{n} B"


def _fmt_views(n) -> str:
    if not n:
        return "?"
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(n)


def _fmt_duration(secs) -> str:
    if not secs:
        return "?"
    m, s = divmod(int(secs), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"


def _progress_bar(percent: float, width: int = 35) -> str:
    filled = int(width * percent / 100)
    return f"[{'█' * filled}{'░' * (width - filled)}] {int(percent)}%"


BOX_W = 51


def make_progress_hook(title: str, audio_format: str):
    state = {"header_printed": False}

    def hook(d):
        if d["status"] == "downloading":
            filesize = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            if not state["header_printed"]:
                t = title if len(title) <= 44 else title[:41] + "..."
                size_str = _fmt_bytes(filesize)
                info = f"{size_str} · webm → {audio_format} · 320kbps"
                print()
                print(f" {CYAN}┌{'─'*BOX_W}┐{RESET}")
                print(f" {CYAN}│{RESET} {BOLD}↓ {t}{RESET}{' '*(BOX_W-4-len(t))}{CYAN}│{RESET}")
                print(f" {CYAN}│{RESET} {DIM}{info}{RESET}{' '*(BOX_W-2-len(info))}{CYAN}│{RESET}")
                state["header_printed"] = True
            percent = (downloaded / filesize * 100) if filesize else 0
            bar = _progress_bar(percent)
            print(f" {CYAN}│{RESET} {YELLOW}{bar}{RESET}{' '*(BOX_W-2-len(bar))}{CYAN}│{RESET}", end="\r")
        elif d["status"] == "finished":
            bar = _progress_bar(100)
            print(f" {CYAN}│{RESET} {GREEN}{bar}{RESET}{' '*(BOX_W-2-len(bar))}{CYAN}│{RESET}")
            print(f" {CYAN}└{'─'*BOX_W}┘{RESET}")

    return hook


def print_result(artist: str, extra: list, genre: str, dest: Path):
    artista_str = artist or "?"
    if extra:
        artista_str += " · " + " · ".join(extra)
    home = str(Path.home())
    d = str(dest).replace(home, "~")
    parts = d.rsplit("/", 1)
    d_disp = f"{parts[0]}/{GREEN}{parts[1]}{RESET}" if len(parts) == 2 else d
    print()
    print(f" 🎵 {DIM}Título {RESET} {dest.stem}")
    print(f" 👤 {DIM}Artista {RESET} {artista_str}")
    print(f" 🎸 {DIM}Género {RESET} {YELLOW}{genre}{RESET}")
    print(f" 📁 {DIM}Destino {RESET} {d_disp}")
    print()


def _query_words(query: str) -> set:
    stopwords = {"de", "la", "el", "en", "y", "a", "the", "an", "of", "in"}
    return {w for w in re.findall(r'\w+', query.lower()) if len(w) > 1 and w not in stopwords}


def _score_v1(entry: dict, query: str = "") -> float:
    title = (entry.get("title") or "").lower()
    channel = (entry.get("channel") or "").lower()
    dur = entry.get("duration") or 0
    views = entry.get("view_count") or 0
    score = 0.0
    
    if query:
        q_words = _query_words(query)
        title_words = set(re.findall(r'\w+', title))
        if q_words:
            overlap = len(q_words & title_words) / len(q_words)
            score += overlap * 100 # Aumentamos peso de coincidencia
            score -= len(q_words - title_words) * 20
        
        # Bonus si el canal coincide con el artista buscado
        channel_words = set(re.findall(r'\w+', channel))
        if q_words & channel_words:
            score += 50

    # Penalizaciones fuertes
    for w in PENALTY_WORDS:
        if w in title:
            score -= 60
            
    # Penalizar específicamente Lyrics/Letra si buscamos calidad oficial
    if "lyrics" in title or "letra" in title:
        score -= 40
            
    # Bonificaciones estratégicas
    if "visualizer" in title:
        score += 80
    
    if "official audio" in title or "audio oficial" in title:
        score += 70
    elif "audio" in title:
        score += 30
        
    if "vevo" in channel or "oficial" in channel or "official" in channel:
        score += 40
            
    # Prioridad máxima: Canales Topic (Distribución oficial de YouTube Music)
    if channel.endswith(" - topic"):
        score += 100
        
    # Duración ideal de una canción
    if 90 <= dur <= 360:
        score += 30
    elif dur > 600:
        score -= 100
    elif dur > 420:
        score -= 40
        
    if views > 0:
        # El peso de las visitas es dominante (x10.0) para que la versión oficial popular 
        # (millones de views) siempre aplaste a resubidos o versiones secundarias (miles de views).
        score += math.log10(views) * 10.0
        
    return score


def _score(entry: dict, query: str = "") -> float:
    title = (entry.get("title") or "").lower()
    channel = (entry.get("channel") or "").lower()
    dur = entry.get("duration") or 0
    views = entry.get("view_count") or 0
    score = 0.0
    
    if query:
        q_words = _query_words(query)
        title_words = set(re.findall(r'\w+', title))
        channel_words = set(re.findall(r'\w+', channel))
        combined_words = title_words | channel_words
        
        if q_words:
            # Coincidencia en el título (mantiene prioridad para títulos exactos)
            overlap_title = len(q_words & title_words) / len(q_words)
            score += overlap_title * 100
            
            # Penalización suave por palabras faltantes en el título
            score -= len(q_words - title_words) * 20
            
            # Penalización severa por palabras clave de la búsqueda que NO aparecen
            # ni en el título ni en el canal (ausencia total de la palabra clave)
            missing_completely = q_words - combined_words
            score -= len(missing_completely) * 120

        # Bonus si el canal coincide con el artista buscado
        if q_words & channel_words:
            score += 50

    # Penalizaciones fuertes
    for w in PENALTY_WORDS:
        if w in title:
            score -= 60
            
    # Penalizar específicamente Lyrics/Letra si buscamos calidad oficial
    if "lyrics" in title or "letra" in title:
        score -= 40
            
    # Bonificaciones estratégicas
    if "visualizer" in title:
        score += 80
    
    if "official audio" in title or "audio oficial" in title:
        score += 70
    elif "audio" in title:
        score += 30
        
    if "vevo" in channel or "oficial" in channel or "official" in channel:
        score += 40
            
    # Prioridad máxima: Canales Topic (Distribución oficial de YouTube Music)
    if channel.endswith(" - topic"):
        score += 100
        
    # Duración ideal de una canción
    if 90 <= dur <= 360:
        score += 30
    elif dur > 600:
        score -= 100
    elif dur > 420:
        score -= 40
        
    if views > 0:
        score += math.log10(views) * 10.0
        
    return score


def search_youtube(query: str, max_results: int = 5) -> list:
    opts = {"quiet": True, "no_warnings": True, "extract_flat": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch{max_results * 3}:{query}", download=False)
    entries = [e for e in (info.get("entries") or []) if e.get("title") and e.get("url")]
    return sorted(entries, key=lambda e: _score(e, query), reverse=True)[:max_results]


def show_results(query: str, results: list):
    print()
    print(f" Búsqueda: {BOLD}{query}{RESET}")
    print(f" {DIM}{'─' * 55}{RESET}")
    print()
    for i, r in enumerate(results):
        title = r.get("title", "Sin título")
        channel = r.get("channel") or r.get("uploader") or "?"
        dur = _fmt_duration(r.get("duration"))
        views = _fmt_views(r.get("view_count"))
        marker = "★" if i == 0 else " "
        meta = f"{DIM}· {channel} · {dur} · {views} views{RESET}"
        if i == 0:
            print(f"{YELLOW}{BOLD} {marker} [{i+1}] {title} {meta}{RESET}")
        else:
            print(f" [{i+1}] {title} {meta}")
    print()
    print(f" {DIM}Selecciona un número o pulsa Enter para descargar el marcado [★]{RESET}")
    print()


def pick_result(results: list):
    raw = input(" Opción: ").strip()
    if raw == "":
        return results[0]
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(results):
            return results[idx]
        print(f" ⚠ Número fuera de rango (1-{len(results)})")
    else:
        print(" ⚠ Entrada no válida.")
    return None


def _parse_yt_title(yt_title: str):
    parts = re.split(r'\s*-\s+', yt_title, maxsplit=1)
    artist = parts[0].strip() if len(parts) == 2 else None
    title = parts[1].strip() if len(parts) == 2 else yt_title.strip()
    feat = r'\s+(?:with|ft\.?|feat\.?)\s+(.+?)(?:\s*[\(\[]|$)'
    m = re.search(feat, title, flags=re.IGNORECASE)
    extra = []
    if m:
        extra = [a.strip() for a in re.split(r'\s*[,&]\s*', m.group(1))]
        title = re.sub(feat, '', title, flags=re.IGNORECASE).strip()
    title = re.sub(r'\s*[\(\[](?:audio|official|video|lyrics?|visualizer)[^\)\]]*[\)\]]', '', title, flags=re.IGNORECASE).strip()
    return artist, title, extra


def _fetch_genre(query: str, headers: dict) -> str | None:
    try:
        r = requests.get(
            "https://musicbrainz.org/ws/2/recording",
            params={"query": query, "fmt": "json", "limit": 1},
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        recs = r.json().get("recordings", [])
        if not recs:
            return None
        rels = recs[0].get("releases", [])
        if not rels:
            return None
        rg_id = rels[0].get("release-group", {}).get("id")
        if not rg_id:
            return None
        time.sleep(1)
        rg = requests.get(
            f"https://musicbrainz.org/ws/2/release-group/{rg_id}",
            params={"inc": "tags", "fmt": "json"},
            headers=headers,
            timeout=10,
        )
        rg.raise_for_status()
        tags = rg.json().get("tags", [])
        if tags:
            return safe_name(max(tags, key=lambda t: t.get("count", 0))["name"].title())
    except Exception:
        pass
    return None


def get_genre(yt_title: str, yt_channel: str, email: str) -> str | None:
    headers = {"User-Agent": f"MusicOrganizer/1.0 ({email or 'user@example.com'})"}
    artist, title, extra = _parse_yt_title(yt_title)
    if not title:
        return None
    queries = []
    if artist:
        queries.append(f'recording:"{title}" AND artist:"{artist}"')
    if extra:
        queries.append(f'recording:"{title}" AND artist:"{extra[0]}"')
    queries.append(f'recording:"{title}"')
    if yt_channel and yt_channel != artist:
        queries.append(f'recording:"{title}" AND artist:"{yt_channel}"')
    for q in queries:
        g = _fetch_genre(q, headers)
        if g:
            return g
        time.sleep(1)
    return None


def _suggest_genre(yt_title: str, yt_channel: str) -> str:
    t = (yt_title or "").lower()
    c = (yt_channel or "").lower()
    for k, v in GENRE_RULES:
        if k in t:
            return v
    for k, v in CHANNEL_RULES:
        if k in c:
            return v
    if any(x in t for x in ["audio oficial", "official audio", "vevo"]):
        return "Pop"
    if any(x in t for x in ["urban", "urbano", "latino"]):
        return "Urbano Latino"
    return "Unknown"


def _ask_unknown_genre(track_title: str, yt_channel: str, unknown_folder: str) -> str:
    suggestion = _suggest_genre(track_title, yt_channel)
    raw = input(f" Género no detectado para '{track_title}'. Género sugerido [{suggestion}]: ").strip()
    if not raw:
        return suggestion if suggestion != "Unknown" else unknown_folder
    return safe_name(raw)


from .organizer import genre_from_rules, genre_from_tags, move_file, genre_from_musicbrainz, genre_from_itunes

def download_and_organize(url: str, dest_dir: Path, cfg: dict, audio_format: str = "mp3", yt_title: str = "", yt_channel: str = "", auto_mode: bool = False):
    if not yt_title:
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as ydl:
                info = ydl.extract_info(url, download=False)
                yt_title = info.get("title", "")
                yt_channel = info.get("channel") or info.get("uploader", "")
        except Exception:
            pass

    artist, title, extra = _parse_yt_title(yt_title)
    unknown_folder = cfg.get("unknown_folder", "Unknown")

    with tempfile.TemporaryDirectory() as tmp_dir:
        opts = {
            "format": "bestaudio/best",
            "outtmpl": str(Path(tmp_dir) / "%(title)s.%(ext)s"),
            "postprocessors": [
                {"key": "FFmpegMetadata"},
                {"key": "FFmpegExtractAudio", "preferredcodec": audio_format, "preferredquality": "320"},
            ],
            "quiet": True, "no_warnings": True, "noprogress": True,
            "progress_hooks": [make_progress_hook(yt_title, audio_format)],
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
        except yt_dlp.utils.DownloadError as e:
            print(f"\n ⚠ Error de descarga: {e}")
            return

        archivos = [f for f in Path(tmp_dir).iterdir() if f.suffix.lower() in cfg.get("extensions", [])]
        if not archivos:
            print("\n ⚠ No se encontró ningún archivo de audio.")
            return

        for archivo in archivos:
            # 1. Reglas Locales
            genre = genre_from_rules(archivo, cfg)
            if genre:
                print(f"  → (regla local) {genre}")
            else:
                # 2. MusicBrainz (Internet A)
                genre = genre_from_musicbrainz(archivo, cfg.get("email", ""))
                if genre:
                    print(f"  → (MusicBrainz) {genre}")
                else:
                    # 3. iTunes (Internet B - Fallback)
                    genre = genre_from_itunes(archivo)
                    if genre:
                        print(f"  → (iTunes) {genre}")
                    else:
                        # 4. Sugerencia o Unknown
                        if auto_mode:
                            genre = _suggest_genre(yt_title, yt_channel)
                        else:
                            genre = _ask_unknown_genre(yt_title or archivo.stem, yt_channel, unknown_folder)

            # --- NUEVA OPCIÓN: CORRECCIÓN MANUAL ---
            if not auto_mode:
                prompt = f"  🎸 Género detectado: {YELLOW}{genre}{RESET}. ¿Cambiar? (Enter para mantener): "
                new_genre = input(prompt).strip()
                if new_genre:
                    genre = safe_name(new_genre.title())

            target = move_file(archivo, genre, dest_dir)
            print_result(artist, extra, genre, target)


def search_and_download(query: str, dest_dir: Path, cfg: dict, audio_format: str = "mp3", auto_mode: bool = False):
    print("\n Buscando...")
    results = search_youtube(query)
    if not results:
        print(" ⚠ No se encontraron resultados.")
        return
    show_results(query, results)
    chosen = pick_result(results)
    if not chosen:
        return
    url = chosen.get("url") or chosen.get("webpage_url") or ""
    if not url.startswith("http"):
        url = f"https://www.youtube.com/watch?v={url}"
    download_and_organize(
        url, dest_dir, cfg, audio_format,
        yt_title=chosen.get("title", ""),
        yt_channel=chosen.get("channel") or chosen.get("uploader", ""),
        auto_mode=auto_mode
    )
