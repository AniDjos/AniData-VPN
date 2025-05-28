@echo off
echo AniData VPN - Edition 163 Pays
echo ===============================
echo.

set SCRIPT_DIR=%~dp0
cd %SCRIPT_DIR%

echo Verification des configurations...
if not exist "infrastructure\servers\expanded_config.json" (
    echo Configuration etendue non trouvee. Generation en cours...
    python scripts\update_servers.py -i infrastructure\servers\config.json -o infrastructure\servers\expanded_config.json
    if errorlevel 1 (
        echo Erreur lors de la generation de la configuration.
        pause
        exit /b 1
    )
)

echo Lancement de AniData VPN - Edition 163 Pays...
python scripts\simple_vpn.py
if errorlevel 1 (
    echo Erreur lors du lancement de l'application.
    pause
)
