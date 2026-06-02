#!/bin/bash
# AfterTune - Script de Publicación Rápida en PyPI (VENV version)

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🚀 Iniciando proceso de publicación de AfterTune v1.1.0...${NC}"

# 1. Activar VENV
if [ ! -d ".venv" ]; then
    echo -e "📦 Creando entorno virtual..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# 2. Instalar herramientas de publicación
echo -e "📦 Instalando herramientas de construcción..."
pip install build twine --quiet

# 3. Limpiar versiones antiguas
echo -e "🧹 Limpiando versiones anteriores..."
rm -rf dist/ build/ *.egg-info

# 4. Construir el paquete
echo -e "🏗️  Construyendo paquete..."
python -m build

# 5. Subir a PyPI
echo -e "\n${GREEN}📤 Listo para subir.${NC}"
echo -e "Se te pedirá el nombre de usuario (usa '__token__') y tu API Token como contraseña.\n"

python -m twine upload dist/*

echo -e "\n${GREEN}✨ Proceso finalizado.${NC}"
