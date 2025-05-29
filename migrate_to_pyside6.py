#!/usr/bin/env python3
"""
Script de migration de PyQt5 à PySide6 pour AniData VPN
Ce script modifie les fichiers Python du projet pour utiliser PySide6 au lieu de PyQt5.
"""

import os
import re
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Installe PySide6 et les autres dépendances nécessaires."""
    print("Installation des dépendances...")
    
    # Vérifier si pip est disponible
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
    except subprocess.CalledProcessError:
        print("Erreur: pip n'est pas disponible. Veuillez installer pip.")
        sys.exit(1)
    
    # Installer PySide6 et autres dépendances
    dependencies = ["PySide6", "pyqtgraph", "numpy"]
    
    for dep in dependencies:
        print(f"Installation de {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'installation de {dep}: {e}")
            sys.exit(1)
    
    print("Toutes les dépendances ont été installées avec succès.")

def find_python_files(base_dir):
    """Trouve tous les fichiers Python dans le répertoire spécifié."""
    python_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def modify_file(file_path):
    """Modifie un fichier Python pour utiliser PySide6 au lieu de PyQt5."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remplacer les imports PyQt5 par PySide6
    content = re.sub(r'from PyQt5\.QtWidgets', r'from PySide6.QtWidgets', content)
    content = re.sub(r'from PyQt5\.QtCore', r'from PySide6.QtCore', content)
    content = re.sub(r'from PyQt5\.QtGui', r'from PySide6.QtGui', content)
    content = re.sub(r'from PyQt5\.QtWebEngineWidgets', r'from PySide6.QtWebEngineWidgets', content)
    content = re.sub(r'from PyQt5 import', r'from PySide6 import', content)
    content = re.sub(r'import PyQt5\.', r'import PySide6.', content)
    
    # Remplacer pyqtSignal par Signal
    content = re.sub(r'pyqtSignal', r'Signal', content)
    
    # Ajustements spécifiques pour QWebEngineView (si nécessaire)
    # Ajuster la façon dont les signaux sont connectés
    content = re.sub(r'\.connect\(([^,]+)\)', r'.connect(\1)', content)
    
    # Écrire le contenu modifié dans le fichier
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Fichier modifié: {file_path}")

def create_compatibility_layer():
    """Crée un module de compatibilité pour faciliter la transition."""
    compat_dir = Path("VPN_anicet/ui/compat")
    compat_dir.mkdir(exist_ok=True)
    
    compat_init = compat_dir / "__init__.py"
    with open(compat_init, 'w', encoding='utf-8') as file:
        file.write("""
# Module de compatibilité pour faciliter la transition PyQt5 -> PySide6
from PySide6 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

# Alias pour les noms de classe PyQt5
QtCore.pyqtSignal = QtCore.Signal
QtCore.pyqtSlot = QtCore.Slot
QtCore.pyqtProperty = QtCore.Property
""")
    
    print(f"Module de compatibilité créé: {compat_init}")

def update_run_script():
    """Met à jour le script d'exécution pour vérifier PySide6 au lieu de PyQt5."""
    script_path = "VPN_anicet/run_modern_ui.py"
    
    with open(script_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remplacer la vérification de PyQt5 par PySide6
    content = content.replace(
        "ERROR: PyQt5 and PyQtWebEngine are required. Install with:\npip install PyQt5 PyQtWebEngine",
        "ERROR: PySide6 is required. Install with:\npip install PySide6"
    )
    
    # Mettre à jour toute autre référence à PyQt5
    content = content.replace("PyQt5", "PySide6")
    content = content.replace("PyQtWebEngine", "PySide6")
    
    with open(script_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Script d'exécution mis à jour: {script_path}")

def main():
    # Vérifier si nous sommes dans le bon répertoire
    if not os.path.exists("VPN_anicet"):
        print("Erreur: Ce script doit être exécuté depuis le répertoire parent de VPN_anicet.")
        sys.exit(1)
    
    # Installer les dépendances
    install_dependencies()
    
    # Trouver tous les fichiers Python
    python_files = find_python_files("VPN_anicet")
    
    # Modifier chaque fichier
    for file_path in python_files:
        modify_file(file_path)
    
    # Créer un module de compatibilité
    create_compatibility_layer()
    
    # Mettre à jour le script d'exécution
    update_run_script()
    
    print("\nMigration terminée avec succès!")
    print("Vous pouvez maintenant exécuter l'application avec: python VPN_anicet/run_modern_ui.py")

if __name__ == "__main__":
    main()