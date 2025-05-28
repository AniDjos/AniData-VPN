#!/bin/bash
# AniData VPN - Extended Servers Launch Script
# © 2023-2024 AniData - All Rights Reserved

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Display logo
echo -e "${BLUE}"
echo "    _          _ ____        _        __     ______  _   _ "
echo "   / \   _ __ (_)  _ \  __ _| |_ __ _\ \   / /  _ \| \ | |"
echo "  / _ \ | '_ \| | | | |/ _\` | __/ _\` |\ \ / /| |_) |  \| |"
echo " / ___ \| | | | | |_| | (_| | || (_| | \ V / |  __/| |\  |"
echo "/_/   \_\_| |_|_|____/ \__,_|\__\__,_|  \_/  |_|   |_| \_|"
echo -e "${NC}"
echo -e "${CYAN}Next Generation VPN - 163 Countries Edition${NC}\n"

# Detect script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"

# Check for required dependencies
check_dependencies() {
    echo -e "${BLUE}Vérification des dépendances...${NC}"
    
    # Check for Python 3
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 n'est pas installé. Veuillez l'installer et réessayer.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Python 3 est installé.${NC}"
    
    # Check for tkinter
    if ! python3 -c "import tkinter" &> /dev/null; then
        echo -e "${YELLOW}Tkinter n'est pas installé. Installation...${NC}"
        if command -v apt-get &> /dev/null; then
            sudo apt-get install -y python3-tk
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-tkinter
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm python-tkinter
        else
            echo -e "${RED}Impossible de détecter le gestionnaire de paquets. Veuillez installer tkinter manuellement.${NC}"
            exit 1
        fi
        
        # Check if installation succeeded
        if ! python3 -c "import tkinter" &> /dev/null; then
            echo -e "${RED}L'installation de tkinter a échoué. Veuillez l'installer manuellement.${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}Tkinter est installé.${NC}"
    
    # Check for PIL
    if ! python3 -c "import PIL" &> /dev/null; then
        echo -e "${YELLOW}Pillow (PIL) n'est pas installé. Installation...${NC}"
        python3 -m pip install --user Pillow
        
        # Check if installation succeeded
        if ! python3 -c "import PIL" &> /dev/null; then
            echo -e "${RED}L'installation de Pillow a échoué. Veuillez l'installer manuellement.${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}Pillow est installé.${NC}"
    
    # Check for WireGuard tools
    if ! command -v wg &> /dev/null; then
        echo -e "${YELLOW}WireGuard tools n'est pas installé.${NC}"
        echo -e "Vous aurez besoin d'installer WireGuard pour une connexion complète:"
        echo -e "  sudo apt-get install wireguard-tools"
        echo -e "  ou"
        echo -e "  sudo dnf install wireguard-tools"
        echo -e "  ou"
        echo -e "  sudo pacman -S wireguard-tools"
        echo -e "Continuer sans WireGuard (fonctionnalités limitées)? (o/n)"
        read -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Oo]$ ]]; then
            echo -e "${YELLOW}Installation de WireGuard...${NC}"
            if command -v apt-get &> /dev/null; then
                sudo apt-get install -y wireguard-tools iproute2
            elif command -v dnf &> /dev/null; then
                sudo dnf install -y wireguard-tools iproute
            elif command -v pacman &> /dev/null; then
                sudo pacman -S --noconfirm wireguard-tools iproute2
            else
                echo -e "${RED}Impossible de détecter le gestionnaire de paquets. Veuillez installer wireguard-tools manuellement.${NC}"
                echo -e "${YELLOW}L'application fonctionnera en mode limité.${NC}"
            fi
        fi
    else
        echo -e "${GREEN}WireGuard est installé.${NC}"
    fi
    
    echo -e "${GREEN}Toutes les dépendances sont installées.${NC}\n"
}

# Prepare configuration
prepare_config() {
    echo -e "${BLUE}Préparation de la configuration étendue...${NC}"
    
    # Create user config directory
    USER_CONFIG_DIR="$HOME/.anidata"
    mkdir -p "$USER_CONFIG_DIR/config/wireguard"
    mkdir -p "$USER_CONFIG_DIR/servers"
    
    # Ensure we have the extended configuration
    EXTENDED_CONFIG="$PROJECT_ROOT/infrastructure/servers/new_expanded_config.json"
    USER_SERVER_CONFIG="$USER_CONFIG_DIR/servers/expanded_config.json"
    
    if [ ! -f "$EXTENDED_CONFIG" ]; then
        # Try generating it
        echo -e "${YELLOW}Configuration étendue non trouvée, génération...${NC}"
        cd "$PROJECT_ROOT"
        python3 scripts/update_servers.py -i infrastructure/servers/config.json -o infrastructure/servers/new_expanded_config.json
        if [ ! -f "$EXTENDED_CONFIG" ]; then
            echo -e "${RED}Impossible de générer la configuration étendue.${NC}"
            # Try the other variants
            if [ -f "$PROJECT_ROOT/infrastructure/servers/expanded_config.json" ]; then
                EXTENDED_CONFIG="$PROJECT_ROOT/infrastructure/servers/expanded_config.json"
                USER_SERVER_CONFIG="$USER_CONFIG_DIR/servers/expanded_config.json"
                echo -e "${GREEN}Utilisation de expanded_config.json à la place.${NC}"
            elif [ -f "$PROJECT_ROOT/infrastructure/servers/config_expanded.json" ]; then
                EXTENDED_CONFIG="$PROJECT_ROOT/infrastructure/servers/config_expanded.json"
                USER_SERVER_CONFIG="$USER_CONFIG_DIR/servers/expanded_config.json"
                echo -e "${GREEN}Utilisation de config_expanded.json à la place.${NC}"
            else
                echo -e "${RED}Aucune configuration étendue trouvée. Utilisation de la configuration standard.${NC}"
                EXTENDED_CONFIG="$PROJECT_ROOT/infrastructure/servers/config.json"
                USER_SERVER_CONFIG="$USER_CONFIG_DIR/servers/config.json"
            fi
        else
            echo -e "${GREEN}Configuration étendue générée avec succès (163 serveurs).${NC}"
        fi
    fi
    
    # Copy server configuration
    if [ -f "$EXTENDED_CONFIG" ]; then
        echo -e "${YELLOW}Copie de la configuration étendue des serveurs...${NC}"
        cp "$EXTENDED_CONFIG" "$USER_SERVER_CONFIG"
        echo -e "${GREEN}Configuration étendue copiée.${NC}"
    fi
    
    echo -e "${GREEN}Configuration prête.${NC}\n"
}

# Launch UI
launch_ui() {
    echo -e "${BLUE}Lancement de l'interface AniData VPN avec 163 pays...${NC}"
    
    cd "$PROJECT_ROOT"
    python3 scripts/simple_vpn.py
    
    # Check exit code
    if [ $? -ne 0 ]; then
        echo -e "${RED}L'application a rencontré une erreur.${NC}"
        exit 1
    fi
}

# Main function
main() {
    echo -e "${CYAN}AniData VPN - Édition 163 Pays${NC}"
    check_dependencies
    prepare_config
    launch_ui
}

# Run the script
main

exit 0