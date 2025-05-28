#!/bin/bash
# AniData VPN - Tkinter UI Launch Script
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
echo -e "${YELLOW}Next Generation VPN - Interface Tkinter Simple${NC}\n"

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
            echo -e "${RED}Impossible de détecter le gestionnaire de paquets. Veuillez installer tkinter manuellement:${NC}"
            echo -e "  Pour Debian/Ubuntu: sudo apt-get install python3-tk"
            echo -e "  Pour Fedora: sudo dnf install python3-tkinter"
            echo -e "  Pour Arch: sudo pacman -S python-tkinter"
            exit 1
        fi
        
        # Check if installation succeeded
        if ! python3 -c "import tkinter" &> /dev/null; then
            echo -e "${RED}L'installation de tkinter a échoué. Veuillez l'installer manuellement.${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}Tkinter est installé.${NC}"
    
    echo -e "${GREEN}Toutes les dépendances sont installées.${NC}\n"
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
    
    echo -e "${GREEN}Configuration prête.${NC}\n"
}

# Launch UI
launch_ui() {
    echo -e "${BLUE}Lancement de l'interface Tkinter AniData VPN...${NC}"
    
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
    check_dependencies
    prepare_config
    launch_ui
}

# Run the script
main

exit 0