@echo off
:: AfterTune - Lanzador Automático para Windows
:: Este script configura el entorno y lanza la aplicación sin intervención del usuario.

echo ------------------------------------------
echo         Iniciando AfterTune...
echo ------------------------------------------

:: 1. Comprobar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python no encontrado. Por favor, instale Python desde python.org
    pause
    exit /b
)

:: 2. Gestionar Entorno Virtual
if not exist ".venv" (
    echo [+] Configurando el sistema por primera vez...
    python -m venv .venv
)

:: 3. Sincronizar cambios y dependencias
call .venv\Scripts\activate
echo [+] Verificando componentes y sincronizando...
pip install -e . --quiet --no-warn-script-location

:: 4. Lanzar la aplicación
echo.
echo [OK] Sistema listo. Abriendo AfterTune...
timeout /t 1 >nul
aftertune %*

:: Desactivar entorno al salir
deactivate
