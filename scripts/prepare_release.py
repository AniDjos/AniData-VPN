#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AniData VPN - Release Preparation Script
# © 2023-2024 AniData - All Rights Reserved

import os
import sys
import shutil
import platform
import subprocess
import argparse
import datetime
from pathlib import Path

VERSION = "1.0.0"
RELEASE_DIR = "releases"

def parse_arguments():
    parser = argparse.ArgumentParser(description="Prépare une release d'AniData VPN")
    parser.add_argument('--version', '-v', default=VERSION,
                        help=f'Version de la release (par défaut: {VERSION})')
    parser.add_argument('--platforms', '-p', default='all',
                        choices=['all', 'windows', 'linux', 'appimage', 'deb', 'rpm'],
                        help='Plateformes à préparer (par défaut: all)')
    parser.add_argument('--skip-clean', '-s', action='store_true',
                        help='Ne pas nettoyer les anciens fichiers de build')
    parser.add_argument('--output', '-o', default=RELEASE_DIR,
                        help=f'Dossier de sortie pour les fichiers (par défaut: {RELEASE_DIR})')
    
    return parser.parse_args()

def ensure_directory(directory):
    """Assure qu'un répertoire existe"""
    os.makedirs(directory, exist_ok=True)
    return directory

def clean_build_directories():
    """Nettoie les anciens fichiers de build"""
    print("Nettoyage des anciens fichiers de build...")
    
    build_dirs = ['build', 'dist']
    for dir_name in build_dirs:
        if os.path.exists(dir_name):
            print(f"Suppression de {dir_name}/")
            shutil.rmtree(dir_name)
    
    # Nettoyer les fichiers spec de PyInstaller
    for spec_file in Path('.').glob('*.spec'):
        print(f"Suppression de {spec_file}")
        spec_file.unlink()

def update_version_info(version):
    """Met à jour les informations de version dans les fichiers du projet"""
    print(f"Mise à jour des informations de version vers {version}...")
    
    # Chercher les fichiers Python principaux
    script_files = [
        'scripts/simple_vpn.py',
        'scripts/package_windows.py',
        'scripts/packaging/package_linux.py'
    ]
    
    # Date actuelle pour les droits d'auteur
    current_year = datetime.datetime.now().year
    copyright_str = f"© 2023-{current_year}" if current_year > 2023 else "© 2023"
    
    for script_file in script_files:
        if os.path.exists(script_file):
            try:
                with open(script_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Mettre à jour la version
                if "version" in content.lower():
                    # Trouver et remplacer les lignes de version
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if '"version"' in line.lower() or "'version'" in line.lower():
                            if ':' in line:  # Format JSON ou dict
                                prefix = line.split(':')[0]
                                lines[i] = f'{prefix}: "{version}",'
                            elif '=' in line:  # Affectation de variable
                                prefix = line.split('=')[0]
                                lines[i] = f'{prefix}= "{version}"'
                    
                    content = '\n'.join(lines)
                
                # Mettre à jour l'année de copyright
                content = content.replace("© 2023", copyright_str)
                
                with open(script_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"Mis à jour: {script_file}")
                
            except Exception as e:
                print(f"Erreur lors de la mise à jour de {script_file}: {e}")
    
    # Mettre à jour le README
    readme_file = 'README.md'
    if os.path.exists(readme_file):
        try:
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Mettre à jour l'année de copyright
            if "© 2023" in content:
                content = content.replace("© 2023", copyright_str)
            
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"Mis à jour: {readme_file}")
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour de {readme_file}: {e}")

def build_windows_release(output_dir, version):
    """Génère un installateur Windows"""
    if platform.system() != "Windows":
        print("La génération d'installateur Windows n'est possible que sur Windows")
        print("Création d'une note dans le dossier de sortie...")
        
        note_file = os.path.join(output_dir, "WINDOWS_BUILD_NOTE.txt")
        with open(note_file, 'w', encoding='utf-8') as f:
            f.write(f"Pour générer un installateur Windows pour AniData VPN v{version}:\n\n")
            f.write("1. Clonez ce dépôt sur une machine Windows\n")
            f.write("2. Exécutez: python scripts/package_windows.py\n")
            f.write("3. L'installateur sera généré dans le dossier dist/\n")
        
        return False
    
    try:
        print("Génération de l'installateur Windows...")
        package_script = "scripts/package_windows.py"
        subprocess.run([sys.executable, package_script], check=True)
        
        # Copier l'installateur généré
        installer_file = None
        for file in Path('dist').glob('*Setup.exe'):
            installer_file = file
            break
        
        if installer_file:
            target_file = os.path.join(output_dir, f"AniDataVPN_{version}_Setup.exe")
            shutil.copy2(installer_file, target_file)
            print(f"Installateur Windows créé: {target_file}")
            return True
        else:
            print("Aucun installateur Windows trouvé après la génération")
            return False
            
    except Exception as e:
        print(f"Erreur lors de la génération de l'installateur Windows: {e}")
        return False

def build_linux_release(output_dir, version, pkg_type='all'):
    """Génère des packages Linux"""
    if platform.system() != "Linux":
        print("La génération de packages Linux n'est possible que sur Linux")
        print("Création d'une note dans le dossier de sortie...")
        
        note_file = os.path.join(output_dir, "LINUX_BUILD_NOTE.txt")
        with open(note_file, 'w', encoding='utf-8') as f:
            f.write(f"Pour générer des packages Linux pour AniData VPN v{version}:\n\n")
            f.write("1. Clonez ce dépôt sur une machine Linux\n")
            f.write(f"2. Exécutez: python scripts/packaging/package_linux.py --type {pkg_type}\n")
            f.write("3. Les packages seront générés dans le répertoire courant\n")
        
        return False
    
    try:
        print(f"Génération des packages Linux ({pkg_type})...")
        package_script = "scripts/packaging/package_linux.py"
        subprocess.run([sys.executable, package_script, '--type', pkg_type], check=True)
        
        # Identifier et copier les packages générés
        package_patterns = {
            'deb': '*.deb',
            'rpm': '*.rpm',
            'appimage': '*.AppImage'
        }
        
        types_to_check = [pkg_type]
        if pkg_type == 'all':
            types_to_check = package_patterns.keys()
        
        packages_found = False
        
        for pkg in types_to_check:
            if pkg in package_patterns:
                pattern = package_patterns[pkg]
                for file in Path('.').glob(pattern):
                    target_file = os.path.join(output_dir, f"AniDataVPN_{version}{file.suffix}")
                    shutil.copy2(file, target_file)
                    print(f"Package Linux créé: {target_file}")
                    packages_found = True
        
        return packages_found
    
    except Exception as e:
        print(f"Erreur lors de la génération des packages Linux: {e}")
        return False

def generate_checksums(output_dir):
    """Génère des checksums pour tous les fichiers de release"""
    print("Génération des checksums...")
    
    checksums_file = os.path.join(output_dir, "checksums.txt")
    
    try:
        with open(checksums_file, 'w', encoding='utf-8') as f:
            f.write(f"# AniData VPN Checksums\n")
            f.write(f"# Generated: {datetime.datetime.now().isoformat()}\n\n")
            
            for file in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file)
                if os.path.isfile(file_path) and file != "checksums.txt":
                    if platform.system() == "Windows":
                        # Utiliser certutil sur Windows
                        result = subprocess.run(
                            ['certutil', '-hashfile', file_path, 'SHA256'],
                            capture_output=True, text=True, check=True
                        )
                        # Extraire la ligne du hash (la deuxième ligne)
                        hash_line = result.stdout.splitlines()[1].strip()
                        f.write(f"SHA256 ({file}) = {hash_line}\n")
                    else:
                        # Utiliser sha256sum sur Linux/Mac
                        result = subprocess.run(
                            ['sha256sum', file_path],
                            capture_output=True, text=True, check=True
                        )
                        # Format: <hash> <filename>
                        hash_value = result.stdout.split()[0]
                        f.write(f"SHA256 ({file}) = {hash_value}\n")
        
        print(f"Checksums générés: {checksums_file}")
        return True
    
    except Exception as e:
        print(f"Erreur lors de la génération des checksums: {e}")
        return False

def create_release_notes(output_dir, version):
    """Crée un fichier de notes de version"""
    release_notes_file = os.path.join(output_dir, f"RELEASE_NOTES_{version}.md")
    
    try:
        with open(release_notes_file, 'w', encoding='utf-8') as f:
            f.write(f"# AniData VPN {version} - Notes de version\n\n")
            f.write(f"Date de publication: {datetime.datetime.now().strftime('%d %B %Y')}\n\n")
            
            f.write("## Nouveautés\n\n")
            f.write("- Interface utilisateur améliorée avec thème Bleu Azur\n")
            f.write("- Support pour plus de 150 pays\n")
            f.write("- Intégration améliorée avec les systèmes d'exploitation\n")
            f.write("- Packages d'installation pour Windows et Linux\n\n")
            
            f.write("## Instructions d'installation\n\n")
            f.write("### Windows\n\n")
            f.write("1. Téléchargez le fichier AniDataVPN_Setup.exe\n")
            f.write("2. Exécutez l'installateur et suivez les instructions\n\n")
            
            f.write("### Linux\n\n")
            f.write("#### Debian/Ubuntu\n\n")
            f.write("```bash\n")
            f.write(f"sudo dpkg -i AniDataVPN_{version}.deb\n")
            f.write("```\n\n")
            
            f.write("#### Fedora/CentOS\n\n")
            f.write("```bash\n")
            f.write(f"sudo rpm -i AniDataVPN_{version}.rpm\n")
            f.write("```\n\n")
            
            f.write("#### Autres distributions\n\n")
            f.write(f"Utilisez le fichier AppImage: `chmod +x AniDataVPN_{version}.AppImage && ./AniDataVPN_{version}.AppImage`\n\n")
            
            f.write("## Vérification des fichiers\n\n")
            f.write("Pour vérifier l'intégrité des fichiers téléchargés, utilisez les checksums fournis dans le fichier `checksums.txt`.\n\n")
            
            f.write("## Support\n\n")
            f.write("Pour toute question ou problème, veuillez ouvrir un ticket sur GitHub.\n")
        
        print(f"Notes de version créées: {release_notes_file}")
        return True
    
    except Exception as e:
        print(f"Erreur lors de la création des notes de version: {e}")
        return False

def main():
    args = parse_arguments()
    
    # Vérifier que nous sommes dans le répertoire racine du projet
    if not os.path.exists("scripts") or not os.path.exists("ui"):
        print("Erreur: Ce script doit être exécuté depuis le répertoire racine du projet AniData VPN")
        sys.exit(1)
    
    # Créer le répertoire de sortie
    output_dir = ensure_directory(args.output)
    print(f"Préparation de la release {args.version} dans {output_dir}")
    
    # Nettoyer les anciens fichiers de build si nécessaire
    if not args.skip_clean:
        clean_build_directories()
    
    # Mettre à jour les informations de version
    update_version_info(args.version)
    
    # Construire les releases selon les plateformes demandées
    if args.platforms in ['all', 'windows']:
        build_windows_release(output_dir, args.version)
    
    if args.platforms in ['all', 'linux', 'deb', 'rpm', 'appimage']:
        pkg_type = args.platforms if args.platforms not in ['all', 'linux'] else 'all'
        build_linux_release(output_dir, args.version, pkg_type)
    
    # Générer des notes de version
    create_release_notes(output_dir, args.version)
    
    # Générer des checksums pour les fichiers
    generate_checksums(output_dir)
    
    print(f"\nPréparation de la release {args.version} terminée!")
    print(f"Fichiers disponibles dans: {output_dir}")
    print("\nPour publier cette release sur GitHub:")
    print("1. Committez les modifications")
    print("2. Créez un tag Git: git tag -a v{args.version} -m 'Version {args.version}'")
    print("3. Poussez le tag: git push origin v{args.version}")
    print("4. Créez une nouvelle release sur GitHub et téléversez les fichiers du dossier {output_dir}")

if __name__ == "__main__":
    main()