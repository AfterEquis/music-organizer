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

# 1. Comprobar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠ Python no encontrado. Por favor, instálalo primero.${NC}"
    exit 1
fi

# 2. Gestionar Entorno Virtual
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
