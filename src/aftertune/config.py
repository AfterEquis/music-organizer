import json
import os
import shutil
import sys
import subprocess
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"

IS_TERMUX = "com.termux" in str(Path.home())


def _default_music_dir() -> str:
    if IS_TERMUX:
        storage = Path.home() / "storage" / "music"
        if storage.exists():
            return str(storage)
        # storage no inicializado, usar home como fallback
        return str(Path.home() / "Music")
    if sys.platform == "win32":
        return str(Path.home() / "Music")
    xdg = os.environ.get("XDG_MUSIC_DIR")
    if xdg:
        return xdg
    return str(Path.home() / "Music")


DEFAULTS = {
    "music_dir":      _default_music_dir(),
    "email":          "",
    "extensions":     [".mp3", ".flac", ".ogg", ".m4a", ".wav"],
    "unknown_folder": "Unknown",
    "rules": {
        "bachata": "Bachata",
        "salsa": "Salsa",
        "techno": "Techno",
        "phonk": "Phonk",
        "lofi": "Lofi",
        "remerix": "Remix"
    },
    "genre_map": {
        "Urbano Latino": "Reggaeton",
        "Latin Trap": "Reggaeton",
        "Trap Latino": "Reggaeton",
        "Urban": "Reggaeton",
        "Dembow": "Reggaeton",
        "Hip-Hop_Rap": "Hip Hop",
        "Chopped And Screwed": "Hip Hop",
        "Rap": "Hip Hop",
        "Emo Rap": "Hip Hop",
        "Pop Rap": "Hip Hop",
        "Alternative Pop": "Pop",
        "Latin Pop": "Pop",
        "Pop Rock": "Pop",
        "Indie Pop": "Pop",
        "2020S": "Pop",
        "Electronic": "Electronica",
        "Electro": "Electronica",
        "House": "Electronica",
        "Deep House": "Electronica",
        "Big Room House": "Electronica",
        "Electro House": "Electronica",
        "Dubstep": "Electronica",
        "Ambient": "Electronica",
        "Breakbeat": "Electronica",
        "Breaks": "Electronica",
        "Slushwave": "Electronica",
        "Techno": "Electronica",
        "Edm": "Electronica",
        "Hard Rock": "Rock",
        "Indie Rock": "Rock",
        "Classic Rock": "Rock",
        "Punk Rock": "Rock",
        "Alternative Rock": "Rock",
        "Punk": "Rock",
        "Metal": "Metal",
        "Melodic Death Metal": "Metal",
        "R&B_Soul": "R&B",
        "Alternative R&B": "R&B",
        "Contemporary R&B": "R&B",
        "Latin Ballad": "Pop",
        "Ballad": "Pop",
        "Bolero": "Latin",
        "Cumbia": "Cumbia",
        "Bachata": "Bachata",
        "Salsa": "Salsa",
        "Reggae": "Reggae"
    }
}


def _spinner_install(name: str, cmd: list) -> bool:
    """Instala un paquete mostrando spinner animado."""
    import threading, time
    CYAN  = "\033[96m"
    GREEN = "\033[92m"
    RED   = "\033[91m"
    RESET = "\033[0m"

    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    result = {"done": False, "ok": False}

    def run():
        r = subprocess.run(cmd, capture_output=True, text=True)
        result["ok"]   = r.returncode == 0
        result["done"] = True

    t = threading.Thread(target=run)
    t.start()
    i = 0
    while not result["done"]:
        print(f"  {CYAN}{frames[i % len(frames)]}{RESET}  {name}...", end="\r")
        time.sleep(0.08)
        i += 1
    t.join()

    if result["ok"]:
        print(f"  {GREEN}✓{RESET}  {name}{' ' * 30}")
    else:
        print(f"  {RED}✗{RESET}  {name} — falló{' ' * 30}")
    return result["ok"]


def check_dependencies() -> bool:
    """
    Verifica dependencias al arrancar.
    Muestra las que faltan e intenta instalarlas automáticamente.
    """
    YELLOW = "\033[93m"
    GREEN  = "\033[92m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"

    PYTHON_DEPS = [
        ("yt-dlp",   "yt_dlp"),
        ("mutagen",  "mutagen"),
        ("requests", "requests"),
    ]

    missing_py  = []
    missing_sys = []

    for pip_name, import_name in PYTHON_DEPS:
        try:
            __import__(import_name)
        except ImportError:
            missing_py.append(pip_name)

    if not shutil.which("ffmpeg"):
        missing_sys.append("ffmpeg")

    # Termux: storage no inicializado
    if IS_TERMUX:
        if not (Path.home() / "storage").exists():
            print(f"  {YELLOW}⚠ Almacenamiento de Termux no inicializado.{RESET}")
            print("    Ejecuta primero: termux-setup-storage\n")
            return False

    all_missing = missing_py + missing_sys
    if not all_missing:
        return True

    print(f"\n  {YELLOW}⚠ Faltan dependencias:{RESET}")
    for dep in all_missing:
        print(f"    · {dep}")
    print()
    print(f"  {BOLD}Instalando...{RESET}\n")

    ok = True

    # Instalar paquetes Python
    for pkg in missing_py:
        if not _spinner_install(pkg, [sys.executable, "-m", "pip", "install", pkg, "-q"]):
            ok = False

    # Instalar ffmpeg según plataforma
    if "ffmpeg" in missing_sys:
        if IS_TERMUX:
            _spinner_install("ffmpeg", ["pkg", "install", "-y", "ffmpeg"])
        elif sys.platform == "win32":
            _spinner_install("ffmpeg", ["winget", "install", "ffmpeg", "-e", "--silent"])
        elif shutil.which("apt"):
            _spinner_install("ffmpeg", ["sudo", "apt", "install", "-y", "ffmpeg"])
        elif shutil.which("pacman"):
            _spinner_install("ffmpeg", ["sudo", "pacman", "-S", "--noconfirm", "ffmpeg"])
        else:
            print(f"  !  ffmpeg — instala manualmente: sudo apt install ffmpeg")
            ok = False

    if ok:
        print(f"\n  {GREEN}✓ Todo listo.{RESET}\n")
    return ok


def load() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {**DEFAULTS, **data}
    return dict(DEFAULTS)


def save(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def setup_wizard() -> dict:
    cfg = load()
    print("\n─── Configuración ───")

    music = input(f"  Carpeta de música [{cfg['music_dir']}]: ").strip()
    if music:
        cfg["music_dir"] = music

    email = input(f"  Email para MusicBrainz [{cfg['email'] or 'vacío'}]: ").strip()
    if email:
        cfg["email"] = email

    save(cfg)
    print("  ✓ Configuración guardada.\n")
    return cfg
