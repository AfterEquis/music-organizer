#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import config as cfg_module
from downloader import search_and_download, download_and_organize
from organizer import organize_folder


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def header():
    print("╔══════════════════════════════════════╗")
    print("║       🎵  Music Organizer            ║")
    print("╚══════════════════════════════════════╝")


def print_menu(cfg: dict):
    print(f"\n  Carpeta: {cfg['music_dir']}\n")
    print("  [1] Buscar y descargar canción")
    print("  [2] Organizar carpeta existente")
    print("  [3] Configuración")
    print("  [4] Salir")
    print()


def menu_download(cfg: dict):
    entrada = input("  Nombre o URL: ").strip()
    if not entrada:
        print("  Entrada vacía, cancelado.")
        return

    print("\n  Formato de audio:")
    print("  [1] mp3 (por defecto)")
    print("  [2] flac")
    print("  [3] m4a")
    fmt = {"1": "mp3", "2": "flac", "3": "m4a"}.get(input("  Opción [1]: ").strip(), "mp3")

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
        )
    else:
        search_and_download(
            query=entrada,
            dest_dir=dest,
            email=cfg["email"],
            extensions=cfg["extensions"],
            unknown_folder=cfg["unknown_folder"],
            audio_format=fmt,
        )
    input("\n  Pulsa Enter para continuar...")


def menu_organize(cfg: dict):
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
    )
    input("\n  Pulsa Enter para continuar...")


def menu_config(cfg: dict) -> dict:
    updated = cfg_module.setup_wizard()
    input("  Pulsa Enter para continuar...")
    return updated


def main():
    if not cfg_module.CONFIG_FILE.exists():
        clear()
        header()
        print("\n  Primera ejecución — vamos a configurar el proyecto.\n")
        cfg = cfg_module.setup_wizard()
    else:
        cfg = cfg_module.load()

    while True:
        clear()
        header()
        print_menu(cfg)

        choice = input("  Opción: ").strip()

        if choice == "1":
            menu_download(cfg)
        elif choice == "2":
            menu_organize(cfg)
        elif choice == "3":
            cfg = menu_config(cfg)
        elif choice == "4":
            print("\n  Hasta luego.\n")
            sys.exit(0)
        else:
            print("  Opción no válida.")


if __name__ == "__main__":
    main()
