#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path

import config as cfg_module
from downloader import search_and_download, download_and_organize
from organizer import organize_folder


def detect_usb() -> list:
    """Detecta dispositivos USB montados. Compatible con Linux, macOS, Windows y Termux."""
    drives = []
    IS_TERMUX = "com.termux" in str(Path.home())

    if IS_TERMUX:
        storage = Path.home() / "storage"
        if storage.exists():
            for d in sorted(storage.iterdir()):
                if d.name.startswith("external") and d.is_dir():
                    drives.append(d)

    elif sys.platform == "win32":
        import string, ctypes
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drive = Path(f"{letter}:\\")
                if ctypes.windll.kernel32.GetDriveTypeW(str(drive)) == 2:
                    drives.append(drive)
            bitmask >>= 1

    elif sys.platform == "darwin":
        volumes = Path("/Volumes")
        if volumes.exists():
            for d in volumes.iterdir():
                if d.is_dir() and d.name != "Macintosh HD":
                    drives.append(d)

    else:  # Linux
        user = os.environ.get("USER", "")
        for base in [Path("/media") / user, Path("/media"), Path("/run/media") / user]:
            if base.exists():
                try:
                    for d in base.iterdir():
                        if d.is_dir() and d.is_mount():
                            drives.append(d)
                except PermissionError:
                    pass

    return drives



def clear():
    os.system("cls" if os.name == "nt" else "clear")


def header():
    print("╔══════════════════════════════════════╗")
    print("║       🎵  Music Organizer            ║")
    print("╚══════════════════════════════════════╝")


def print_menu(cfg: dict, usb: list, usb_ignored: bool):
    print(f"\n  Carpeta : {cfg['music_dir']}")
    if usb and not usb_ignored:
        print(f"  💾 USB   : {usb[0].name}  →  descargando aquí  [U] para ignorar")
    elif usb and usb_ignored:
        print(f"  💾 USB   : {usb[0].name}  →  ignorado  [U] para activar")
    print()
    print("  [1] Buscar y descargar canción")
    print("  [2] Organizar carpeta existente")
    print("  [3] Configuración")
    if usb:
        print("  [U] Activar/ignorar USB esta sesión")
    print("  [4] Salir")
    print()


def menu_download(cfg: dict, auto_mode: bool = False, dest_usb=None):
    entrada = input("  Nombre o URL: ").strip()
    if not entrada:
        print("  Entrada vacía, cancelado.")
        return

    print("\n  Formato de audio:")
    print("  [1] mp3 (por defecto)")
    print("  [2] flac")
    print("  [3] m4a")
    fmt = {"1": "mp3", "2": "flac", "3": "m4a"}.get(input("  Opción [1]: ").strip(), "mp3")

    if dest_usb:
        dest = Path(dest_usb)
        print(f"  💾 Descargando en USB: {dest}")
    else:
        dest = Path(cfg["music_dir"])
    dest.mkdir(parents=True, exist_ok=True)

    es_url = entrada.startswith("http://") or entrada.startswith("https://")

    if es_url:
        download_and_organize(
            url=entrada,
            dest_dir=dest,
            email=cfg["email"],
            extensions=cfg["extensions"],
            unknown_folder=cfg["unknown_folder"],
            audio_format=fmt,
            auto_mode=auto_mode,
        )
    else:
        search_and_download(
            query=entrada,
            dest_dir=dest,
            email=cfg["email"],
            extensions=cfg["extensions"],
            unknown_folder=cfg["unknown_folder"],
            audio_format=fmt,
            auto_mode=auto_mode,
        )
    input("\n  Pulsa Enter para continuar...")


def menu_organize(cfg: dict, auto_mode: bool = False):
    src_input = input(f"  Carpeta a organizar [{cfg['music_dir']}]: ").strip()
    src = Path(src_input) if src_input else Path(cfg["music_dir"])

    if not src.exists():
        print(f"  ⚠ La carpeta no existe: {src}")
        input("  Pulsa Enter para continuar...")
        return

    organize_folder(
        src=src,
        dest=src,
        email=cfg["email"],
        extensions=cfg["extensions"],
        unknown_folder=cfg["unknown_folder"],
        auto_mode=auto_mode,
    )
    input("\n  Pulsa Enter para continuar...")


def menu_config(cfg: dict) -> dict:
    updated = cfg_module.setup_wizard()
    input("  Pulsa Enter para continuar...")
    return updated


def main():
    parser = argparse.ArgumentParser(description="Music Organizer")
    parser.add_argument("--auto", action="store_true",
                        help="Modo automático: no pregunta, manda a Unknown/ si no detecta género")
    args = parser.parse_args()
    auto_mode = args.auto

    try:
        if not cfg_module.CONFIG_FILE.exists():
            clear()
            header()
            print("\n  Primera ejecución — vamos a configurar el proyecto.\n")
            cfg = cfg_module.setup_wizard()
        else:
            cfg = cfg_module.load()
    except Exception as e:
        print(f"  ⚠ Error cargando configuración: {e}")
        cfg = dict(cfg_module.DEFAULTS)

    if not cfg_module.check_dependencies():
        input("  Pulsa Enter para continuar de todos modos...")

    usb_ignored = False

    while True:
        clear()
        header()
        if auto_mode:
            print("\n  [Modo automático activado]\n")

        usb = detect_usb()
        dest_usb = usb[0] if usb and not usb_ignored else None
        print_menu(cfg, usb, usb_ignored)

        try:
            choice = input("  Opción: ").strip().upper()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  Hasta luego.\n")
            sys.exit(0)

        if choice == "1":
            menu_download(cfg, auto_mode, dest_usb)
        elif choice == "2":
            menu_organize(cfg, auto_mode)
        elif choice == "3":
            cfg = menu_config(cfg)
        elif choice == "U" and usb:
            usb_ignored = not usb_ignored
        elif choice == "4":
            print("\n  Hasta luego.\n")
            sys.exit(0)
        else:
            print("  Opción no válida.")


if __name__ == "__main__":
    main()
