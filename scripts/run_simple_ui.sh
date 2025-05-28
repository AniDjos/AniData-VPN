#!/bin/bash
# AniData VPN - Simple UI Launch Script
# © 2023 AniData - All Rights Reserved

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Display logo
echo -e "${BLUE}"
echo "    _          _ ____        _        __     ______  _   _ "
echo "   / \   _ __ (_)  _ \  __ _| |_ __ _\ \   / /  _ \| \ | |"
echo "  / _ \ | '_ \| | | | |/ _\` | __/ _\` |\ \ / /| |_) |  \| |"
echo " / ___ \| | | | | |_| | (_| | || (_| | \ V / |  __/| |\  |"
echo "/_/   \_\_| |_|_|____/ \__,_|\__\__,_|  \_/  |_|   |_| \_|"
echo -e "${NC}"
echo -e "${YELLOW}Next Generation VPN - Interface Graphique Simplifiée${NC}\n"

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
    
    # Check for pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}pip3 n'est pas installé. Veuillez l'installer et réessayer.${NC}"
        exit 1
    fi
    
    # Check for PyQt5
    if ! python3 -c "import PyQt5" &> /dev/null; then
        echo -e "${YELLOW}PyQt5 n'est pas installé. Installation...${NC}"
        pip3 install PyQt5
        
        # Check if installation succeeded
        if ! python3 -c "import PyQt5" &> /dev/null; then
            echo -e "${RED}L'installation de PyQt5 a échoué. Veuillez l'installer manuellement:${NC}"
            echo "pip3 install PyQt5"
            exit 1
        fi
    fi
    
    # Check for Pillow (for asset generation)
    if ! python3 -c "import PIL" &> /dev/null; then
        echo -e "${YELLOW}Pillow n'est pas installé. Installation...${NC}"
        pip3 install Pillow
    fi
    
    echo -e "${GREEN}Toutes les dépendances sont installées.${NC}\n"
}

# Check for WireGuard tools
check_wireguard() {
    echo -e "${BLUE}Vérification de WireGuard...${NC}"
    
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
}

# Prepare configuration
prepare_config() {
    echo -e "${BLUE}Préparation de la configuration...${NC}"
    
    # Create user config directory
    USER_CONFIG_DIR="$HOME/.anidata"
    mkdir -p "$USER_CONFIG_DIR/config/wireguard"
    mkdir -p "$USER_CONFIG_DIR/servers"
    
    # Copy server configuration if it exists and hasn't been copied yet
    SERVER_CONFIG="$PROJECT_ROOT/infrastructure/servers/config.json"
    USER_SERVER_CONFIG="$USER_CONFIG_DIR/servers/config.json"
    
    if [ -f "$SERVER_CONFIG" ] && [ ! -f "$USER_SERVER_CONFIG" ]; then
        echo -e "${YELLOW}Copie de la configuration des serveurs...${NC}"
        cp "$SERVER_CONFIG" "$USER_SERVER_CONFIG"
    fi
    
    # Copy and set up sudo script for VPN operations
    SUDO_SCRIPT_SRC="$PROJECT_ROOT/scripts/vpn_sudo.sh"
    SUDO_SCRIPT_DST="$USER_CONFIG_DIR/vpn_sudo.sh"
    
    if [ -f "$SUDO_SCRIPT_SRC" ]; then
        echo -e "${YELLOW}Configuration du script d'élévation de privilèges...${NC}"
        cp "$SUDO_SCRIPT_SRC" "$SUDO_SCRIPT_DST"
        chmod 755 "$SUDO_SCRIPT_DST"
        
        # Inform user about sudo requirements
        echo -e "${YELLOW}Note: La première connexion VPN nécessitera des droits administrateur${NC}"
        echo -e "${YELLOW}pour configurer les interfaces réseau.${NC}"
    fi
    
    echo -e "${GREEN}Configuration prête.${NC}\n"
}

# Launch UI
launch_ui() {
    echo -e "${BLUE}Lancement de l'interface graphique simplifiée AniData VPN...${NC}"
    
    cd "$PROJECT_ROOT"
    python3 -m ui.desktop.simple_ui
    
    # Check exit code
    if [ $? -ne 0 ]; then
        echo -e "${RED}L'application a rencontré une erreur.${NC}"
        exit 1
    fi
}

# Main function
main() {
    check_dependencies
    check_wireguard
    prepare_config
    launch_ui
}

# Run the script
main

exit 0