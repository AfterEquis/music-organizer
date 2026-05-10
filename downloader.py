import re
import math
import tempfile
from pathlib import Path

import yt_dlp

from organizer import organize_file

# ── Colores ───────────────────────────────────────────────────────────────────
YELLOW = "\033[93m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

PENALTY_WORDS = [
    "reaccion", "reaccionando", "reaction", "reacting",
    "cover", "karaoke", "tutorial", "parodia", "parody",
    "gameplay", "compilation", "compilacion", "mix",
    "extended", "slowed", "reverb", "nightcore",
    "hora", "hours", "completo",
]

BONUS_WORDS = ["official", "oficial", "audio", "vevo"]


def _score(entry: dict) -> float:
    title   = (entry.get("title")   or "").lower()
    channel = (entry.get("channel") or "").lower()
    dur     = entry.get("duration")   or 0
    views   = entry.get("view_count") or 0
    score   = 0.0

    for word in PENALTY_WORDS:
        if word in title:
            score -= 30

    for word in BONUS_WORDS:
        if word in title or word in channel:
            score += 20

    if 90 <= dur <= 360:
        score += 30
    elif dur > 600:
        score -= 50
    elif dur > 360:
        score -= 10

    if views > 0:
        score += math.log10(views) * 3

    return score


def search_youtube(query: str, max_results: int = 5) -> list:
    opts = {"quiet": True, "no_warnings": True, "extract_flat": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch{max_results * 3}:{query}", download=False)
        entries = info.get("entries") or []

    entries = [e for e in entries if e.get("title") and e.get("url")]
    scored  = sorted(entries, key=_score, reverse=True)
    return scored[:max_results]


def _fmt_views(n) -> str:
    if not n:   return "?"
    if n >= 1_000_000_000: return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:     return f"{n/1_000_000:.1f}M"
    if n >= 1_000:         return f"{n/1_000:.0f}K"
    return str(n)


def _fmt_duration(secs) -> str:
    if not secs: return "?"
    m, s = divmod(int(secs), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"


def show_results(query: str, results: list):
    print()
    print(f"  Búsqueda: {BOLD}{query}{RESET}")
    print(f"  {DIM}{'─' * 55}{RESET}")
    print()
    for i, r in enumerate(results):
        title   = r.get("title", "Sin título")
        channel = r.get("channel") or r.get("uploader") or "?"
        dur     = _fmt_duration(r.get("duration"))
        views   = _fmt_views(r.get("view_count"))
        marker  = "★" if i == 0 else " "
        meta    = f"{DIM}· {channel} · {dur} · {views} views{RESET}"
        if i == 0:
            print(f"{YELLOW}{BOLD}  {marker} [{i+1}] {title}  {meta}{RESET}")
        else:
            print(f"    [{i+1}] {title}  {meta}")
    print()
    print(f"  {DIM}Selecciona un número o pulsa Enter para descargar el marcado [★]{RESET}")
    print()


def pick_result(results: list):
    raw = input("  Opción: ").strip()
    if raw == "":
        return results[0]
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(results):
            return results[idx]
        print(f"  ⚠ Número fuera de rango (1-{len(results)})")
        return None
    print("  ⚠ Entrada no válida.")
    return None


def _make_ydl_opts(tmp_dir: str, audio_format: str = "mp3") -> dict:
    return {
        "format": "bestaudio/best",
        "outtmpl": str(Path(tmp_dir) / "%(title)s.%(ext)s"),
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": audio_format, "preferredquality": "192"}],
        "quiet": True,
        "no_warnings": True,
    }


def download_and_organize(url: str, dest_dir: Path, email: str,
                          extensions: list, unknown_folder: str, audio_format: str = "mp3"):
    with tempfile.TemporaryDirectory() as tmp_dir:
        opts = _make_ydl_opts(tmp_dir, audio_format)

        def on_finished(info: dict):
            filepath = info.get("filepath") or info.get("filename")
            if not filepath:
                return
            path = Path(filepath)
            if path.suffix.lower() not in extensions or not path.exists():
                return
            print(f"\n↓ Descargado: {path.name}")
            organize_file(path, dest_dir, email, unknown_folder)

        opts["postprocessor_hooks"] = [
            lambda info: on_finished(info) if info.get("status") == "finished" else None
        ]
        print(f"\n  Descargando...\n")
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
        except yt_dlp.utils.DownloadError as e:
            print(f"  ⚠ Error de descarga: {e}")


def search_and_download(query: str, dest_dir: Path, email: str,
                        extensions: list, unknown_folder: str, audio_format: str = "mp3"):
    print(f"\n  Buscando...")
    results = search_youtube(query)

    if not results:
        print("  ⚠ No se encontraron resultados.")
        return

    show_results(query, results)
    chosen = pick_result(results)
    if not chosen:
        return

    url = chosen.get("url") or chosen.get("webpage_url") or ""
    if not url.startswith("http"):
        url = f"https://www.youtube.com/watch?v={url}"

    download_and_organize(url, dest_dir, email, extensions, unknown_folder, audio_format)
