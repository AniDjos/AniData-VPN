#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AniData VPN - Windows Preparation Script (163 Countries Edition)
# © 2023-2024 AniData - All Rights Reserved

import os
import sys
import json
import shutil
from pathlib import Path
import subprocess

def main():
    """Prepare AniData VPN for Windows packaging with 163 countries"""
    print("AniData VPN - Windows Preparation Script (163 Countries Edition)")
    
    # Get project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Paths
    config_dir = os.path.join(project_root, "infrastructure", "servers")
    config_file = os.path.join(config_dir, "config.json")
    expanded_config_file = os.path.join(config_dir, "new_expanded_config.json")
    vpn_script = os.path.join(project_root, "scripts", "simple_vpn.py")
    
    # Generate extended configuration
    print("\n1. Generating extended server configuration with 163 countries...")
    
    try:
        # Run the update_servers.py script
        update_script = os.path.join(script_dir, "update_servers.py")
        if os.path.exists(update_script) and os.path.exists(config_file):
            cmd = [
                sys.executable,
                update_script,
                "-i", config_file,
                "-o", expanded_config_file
            ]
            subprocess.run(cmd, check=True)
            print("   ✓ Extended configuration generated successfully.")
        else:
            print("   ✗ Update script or config file not found.")
            print(f"     - Update script: {os.path.exists(update_script)}")
            print(f"     - Config file: {os.path.exists(config_file)}")
    except Exception as e:
        print(f"   ✗ Error generating extended configuration: {e}")
    
    # Verify the extended configuration
    print("\n2. Verifying extended server configuration...")
    if os.path.exists(expanded_config_file):
        try:
            with open(expanded_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                server_count = len(config.get("servers", []))
                print(f"   ✓ Extended configuration verified with {server_count} servers.")
                
                # Copy it to a standard name
                std_expanded_config = os.path.join(config_dir, "expanded_config.json")
                shutil.copy2(expanded_config_file, std_expanded_config)
                print(f"   ✓ Copied to standard filename: {os.path.basename(std_expanded_config)}")
                
        except Exception as e:
            print(f"   ✗ Error verifying extended configuration: {e}")
    else:
        print(f"   ✗ Extended configuration file not found at {expanded_config_file}")
    
    # Update the VPN script to use the extended configuration
    print("\n3. Updating VPN script to use extended configuration...")
    try:
        if os.path.exists(vpn_script):
            with open(vpn_script, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if we need to modify the script
            if 'SERVERS_FILE = os.path.join(HOME_DIR, "servers/config.json")' in content:
                # Make a backup
                backup_file = vpn_script + '.bak'
                shutil.copy2(vpn_script, backup_file)
                print(f"   ✓ Created backup of VPN script at {os.path.basename(backup_file)}")
                
                # Update the script
                content = content.replace(
                    'SERVERS_FILE = os.path.join(HOME_DIR, "servers/config.json")',
                    'SERVERS_FILE = os.path.join(HOME_DIR, "servers/expanded_config.json")'
                )
                
                if 'self.root.title("AniData VPN")' in content:
                    content = content.replace(
                        'self.root.title("AniData VPN")',
                        'self.root.title("AniData VPN - Édition 163 Pays")'
                    )
                
                with open(vpn_script, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("   ✓ Updated VPN script to use extended configuration.")
            else:
                print("   ✓ VPN script already uses extended configuration.")
        else:
            print(f"   ✗ VPN script not found at {vpn_script}")
    except Exception as e:
        print(f"   ✗ Error updating VPN script: {e}")
    
    # Create a batch file for Windows
    print("\n4. Creating Windows batch file...")
    batch_file = os.path.join(project_root, "AniDataVPN_163Countries.bat")
    batch_content = r"""@echo off
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
"""
    
    try:
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        print(f"   ✓ Created Windows batch file at {os.path.basename(batch_file)}")
    except Exception as e:
        print(f"   ✗ Error creating Windows batch file: {e}")
    
    print("\n5. Creating README for Windows users...")
    readme_file = os.path.join(project_root, "README_WINDOWS.txt")
    readme_content = r"""AniData VPN - Édition 163 Pays
==============================

Guide d'installation et d'utilisation pour Windows
-------------------------------------------------

1. Prérequis:
   - Python 3.8 ou supérieur installé
   - Les bibliothèques Python: tkinter, pillow (PIL)
   - Optionnel: WireGuard pour des connexions VPN complètes

2. Installation sur Windows:
   a) Installez Python depuis python.org
   b) Ouvrez l'invite de commande en tant qu'administrateur
   c) Installez les dépendances requises:
      pip install pillow

3. Lancement de l'application:
   - Double-cliquez sur le fichier "AniDataVPN_163Countries.bat"
   - OU ouvrez une invite de commande et exécutez:
     python scripts/simple_vpn.py

4. Création d'un installateur Windows (avancé):
   - Si vous souhaitez créer un installateur Windows (.exe):
   - Installez PyInstaller: pip install pyinstaller
   - Installez Inno Setup (https://jrsoftware.org/isinfo.php)
   - Exécutez: python scripts/windows_package.py

En cas de problème:
------------------
- Vérifiez que Python et toutes les dépendances sont installés
- Consultez la documentation dans le dossier "docs/"
- Si les 163 pays ne s'affichent pas, assurez-vous que le fichier 
  "infrastructure/servers/expanded_config.json" existe

Profitez de votre accès VPN mondial!
"""
    
    try:
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"   ✓ Created README for Windows users at {os.path.basename(readme_file)}")
    except Exception as e:
        print(f"   ✗ Error creating README for Windows: {e}")
    
    print("\nPréparation terminée!")
    print("Pour utiliser AniData VPN avec 163 pays sur Windows:")
    print("1. Transférez ce dossier complet sur une machine Windows")
    print("2. Installez Python et les dépendances nécessaires")
    print("3. Double-cliquez sur AniDataVPN_163Countries.bat")
    print("   OU exécutez python scripts/simple_vpn.py")
    print("\nPour créer un installateur Windows:")
    print("1. Transférez ce dossier sur une machine Windows")
    print("2. Exécutez python scripts/windows_package.py (si disponible)")
    print("   OU suivez les instructions dans README_WINDOWS.txt")

if __name__ == "__main__":
    main()