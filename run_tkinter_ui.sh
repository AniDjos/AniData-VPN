#!/bin/bash
# Script de lancement pour l'interface Tkinter d'AniData VPN

# Déterminer le chemin du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Vérifier les dépendances
check_dependency() {
    if ! python3 -c "import $1" &>/dev/null; then
        echo "Installation de $1..."
        if ! sudo apt-get install -y python3-$1; then
            echo "Impossible d'installer $1 via apt, tentative avec pip..."
            if ! pip3 install $1; then
                echo "Erreur: Impossible d'installer $1. Veuillez l'installer manuellement."
                exit 1
            fi
        fi
    fi
}

# Vérifier les dépendances essentielles
echo "Vérification des dépendances..."
check_dependency tk
check_dependency numpy
check_dependency matplotlib

# Lancer l'application
echo "Lancement d'AniData VPN (interface Tkinter)..."
python3 tkinter_ui.py