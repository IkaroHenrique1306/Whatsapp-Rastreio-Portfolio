@echo off
echo ============================================
echo  Compilando launchers para .exe
echo ============================================

where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

echo.
echo [1/2] Compilando launcher_flask.exe...
pyinstaller --onefile --noconsole --name "Servidor Flask" launcher_flask.py

echo.
echo [2/2] Compilando launcher_node.exe...
pyinstaller --onefile --noconsole --name "Bot WhatsApp" launcher_node.py

echo.
echo ============================================
echo  Pronto! Os .exe estao em: dist\
echo  Copie-os para a pasta do projeto.
echo ============================================
pause