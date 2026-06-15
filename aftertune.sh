#!/bin/bash
# AfterTune - Lanzador Automático
# Este script configura el entorno y lanza la aplicación sin intervención del usuario.

# Colores para una interfaz amigable
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear
echo -e "${CYAN}╔══════════════════════════════════════╗${NC}"
echo -e "${CYAN}║       🎵  Iniciando AfterTune        ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════╝${NC}"

# 1. Comprobar e instalar dependencias del sistema
install_pkg() {
    if command -v pkg &> /dev/null; then # Termux
        pkg install -y "$1"
    elif command -v apt &> /dev/null; then # Debian/Ubuntu
        sudo apt update && sudo apt install -y "$1"
    elif command -v pacman &> /dev/null; then # Arch Linux
        sudo pacman -Sy --noconfirm "$1"
    fi
}

if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠ Python no encontrado. Instalando...${NC}"
    install_pkg python
fi

# Instalar dependencias necesarias para el entorno virtual en Debian/Ubuntu
if command -v apt &> /dev/null; then
    if ! dpkg -l | grep -q "python3-venv"; then
        echo -e "${YELLOW}⚠ python3-venv no encontrado (necesario para el entorno virtual). Instalando...${NC}"
        install_pkg python3-venv
    fi
    if ! dpkg -l | grep -q "python3-pip"; then
        echo -e "${YELLOW}⚠ python3-pip no encontrado. Instalando...${NC}"
        install_pkg python3-pip
    fi
fi

if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠ FFmpeg no encontrado (necesario para 320kbps). Instalando...${NC}"
    # En algunos sistemas el paquete se llama ffmpeg, en otros python-ffmpeg no es lo que queremos
    install_pkg ffmpeg
fi

# 2. Gestionar Entorno Virtual
if [ -d ".venv" ] && [ ! -f ".venv/bin/activate" ]; then
    echo -e "${YELLOW}⚠ El entorno virtual (.venv) está corrupto o incompleto. Recreándolo...${NC}"
    rm -rf .venv
fi

if [ ! -d ".venv" ]; then
    echo -e "  Configurando el sistema por primera vez..."
    python3 -m venv .venv
fi

# 3. Sincronizar cambios del código fuente
source .venv/bin/activate
echo -e "  Sincronizando cambios de AfterTune..."
# Usamos pip install -e para que cualquier cambio en los .py se vea reflejado sin reinstalar,
# pero lo ejecutamos para asegurar que las dependencias estén al día.
pip install -e . --quiet --no-warn-script-location

# 4. Lanzar la aplicación
echo -e "  ${GREEN}✔ Sistema listo.${NC}\n"
sleep 0.5
aftertune "$@"
