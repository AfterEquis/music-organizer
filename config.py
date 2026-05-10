import json
import os
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"

DEFAULTS = {
    "music_dir": str(Path.home() / "Music"),
    "email": "",
    "extensions": [".mp3", ".flac", ".ogg", ".m4a", ".wav"],
    "unknown_folder": "Unknown",
}

def load() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge con defaults por si faltan claves nuevas
        return {**DEFAULTS, **data}
    return dict(DEFAULTS)

def save(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def setup_wizard():
    """Asistente de primera configuración."""
    cfg = load()
    print("\n─── Configuración ───")

    music = input(f"Carpeta de música [{cfg['music_dir']}]: ").strip()
    if music:
        cfg["music_dir"] = music

    email = input(f"Tu email (para MusicBrainz) [{cfg['email'] or 'vacío'}]: ").strip()
    if email:
        cfg["email"] = email

    save(cfg)
    print("✓ Configuración guardada.\n")
    return cfg
