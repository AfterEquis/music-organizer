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

# 3. Activar e instalar dependencias silenciosamente
source .venv/bin/activate
echo -e "  Verificando componentes..."
pip install -r requirements.txt --quiet

# 4. Lanzar la aplicación
echo -e "  ${GREEN}¡Todo listo! Abriendo AfterTune...${NC}\n"
sleep 1
python3 main.py "$@"
