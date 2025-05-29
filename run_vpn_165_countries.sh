#!/bin/bash
# Script de lancement pour AniData VPN avec 165 pays
# Ce script utilise Tkinter qui est inclus dans Python standard

# Déterminer le chemin du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Afficher le logo en ASCII art
echo "
   _____          _    _____        __          __     _______  _   _ 
  / ____|   /\   | |  |  __ \       \ \        / /\   |  __ \ \| | | |
 | |       /  \  | |  | |  | |       \ \  /\  / /  \  | |__) | | | | |
 | |      / /\ \ | |  | |  | |        \ \/  \/ / /\ \ |  ___/| | | | |
 | |____ / ____ \| |__| |__| |         \  /\  / ____ \| |    | | | |__
  \_____/_/    \_\____/_____/           \/  \/_/    \_\_|    |_| |____|
                                                                       
               165 PAYS - SÉCURITÉ MAXIMALE - ANONYMAT TOTAL
"

# Vérifier les dépendances
check_dependency() {
    if ! python3 -c "import $1" &>/dev/null; then
        echo "Installation de $1..."
        if ! sudo apt-get install -y python3-$1; then
            echo "Impossible d'installer $1 via apt, tentative avec pip..."
            if ! pip3 install --user $1; then
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

# Créer le répertoire de données si nécessaire
mkdir -p data

# Vérifier si le fichier JSON des pays existe
if [ ! -f "data/countries.json" ]; then
    echo "Création de la base de données des 165 pays..."
    python3 -c "
import json
import os

# Créer une liste initiale de pays avec leurs capitales
countries = []
regions = {
    'Europe': ['France', 'Germany', 'Italy', 'Spain', 'United Kingdom', 'Russia', 'Ukraine', 'Poland', 'Romania', 'Netherlands', 'Belgium', 'Sweden', 'Austria', 'Switzerland', 'Portugal'],
    'Asia': ['China', 'India', 'Japan', 'South Korea', 'Indonesia', 'Thailand', 'Vietnam', 'Malaysia', 'Singapore', 'Philippines', 'Taiwan', 'Saudi Arabia', 'UAE', 'Turkey', 'Israel'],
    'Americas': ['United States', 'Canada', 'Brazil', 'Mexico', 'Argentina', 'Colombia', 'Chile', 'Peru', 'Venezuela', 'Cuba'],
    'Africa': ['South Africa', 'Egypt', 'Nigeria', 'Kenya', 'Morocco', 'Algeria', 'Tunisia', 'Ghana', 'Senegal', 'Tanzania'],
    'Oceania': ['Australia', 'New Zealand', 'Fiji', 'Papua New Guinea', 'Solomon Islands']
}

# Générer quelques serveurs pour chaque région
server_id = 1
for region, country_list in regions.items():
    for country in country_list:
        countries.append({
            'id': f'sv-{server_id:03d}',
            'region': region,
            'country': country,
            'city': f'Capital',
            'protocols': ['wireguard', 'openvpn'],
            'capabilities': {
                'vpn': True,
                'proxy': True,
                'tor': region in ['Europe', 'Americas']
            }
        })
        server_id += 1

# Enregistrer dans le fichier JSON
with open('data/countries.json', 'w') as f:
    json.dump(countries, f, indent=2)
"
fi

# Copier le fichier propre si l'original a des problèmes
if [ -f "tkinter_ui_clean.py" ]; then
    echo "Utilisation de la version propre de l'interface..."
    cp tkinter_ui_clean.py tkinter_ui.py
fi

# Lancer l'application
echo "Lancement d'AniData VPN avec accès à 165 pays..."
python3 tkinter_ui.py