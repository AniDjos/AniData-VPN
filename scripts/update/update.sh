#!/bin/bash

# AniData VPN Update Script
# © 2023 AniData - All Rights Reserved

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logo
display_logo() {
    echo -e "${BLUE}"
    echo "    _          _ ____        _        __     ______  _   _ "
    echo "   / \   _ __ (_)  _ \  __ _| |_ __ _\ \   / /  _ \| \ | |"
    echo "  / _ \ | '_ \| | | | |/ _\` | __/ _\` |\ \ / /| |_) |  \| |"
    echo " / ___ \| | | | | |_| | (_| | || (_| | \ V / |  __/| |\  |"
    echo "/_/   \_\_| |_|_|____/ \__,_|\__\__,_|  \_/  |_|   |_| \_|"
    echo -e "${NC}"
    echo -e "${YELLOW}Next Generation VPN - Update Script${NC}\n"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}Please run as root or with sudo privileges${NC}"
        exit 1
    fi
}

# Check for running VPN service
check_vpn_service() {
    echo -e "${BLUE}Checking AniData VPN service status...${NC}"
    
    if systemctl is-active --quiet anidata.service; then
        echo -e "${YELLOW}AniData VPN service is running. Stopping for update...${NC}"
        systemctl stop anidata.service
        SERVICE_WAS_RUNNING=true
    else
        echo -e "${YELLOW}AniData VPN service is not running.${NC}"
        SERVICE_WAS_RUNNING=false
    fi
}

# Check for current version
check_current_version() {
    echo -e "${BLUE}Checking current version...${NC}"
    
    if [ -f "/opt/anidata/VERSION" ]; then
        CURRENT_VERSION=$(cat /opt/anidata/VERSION)
        echo -e "Current version: ${GREEN}${CURRENT_VERSION}${NC}"
    else
        echo -e "${YELLOW}No version information found.${NC}"
        CURRENT_VERSION="unknown"
    fi
}

# Check for available updates
check_available_updates() {
    echo -e "${BLUE}Checking for available updates...${NC}"
    
    # In a real implementation, this would contact a remote server
    # For this demo, we'll simulate an available update
    LATEST_VERSION="1.2.0"
    
    if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
        echo -e "${GREEN}You are already running the latest version (${LATEST_VERSION}).${NC}"
        if [ "$FORCE_UPDATE" != "true" ]; then
            exit 0
        fi
        echo -e "${YELLOW}Forcing update reinstallation as requested.${NC}"
    else
        echo -e "${GREEN}Update available: ${YELLOW}${CURRENT_VERSION}${NC} -> ${GREEN}${LATEST_VERSION}${NC}"
    fi
}

# Backup current installation
backup_installation() {
    echo -e "${BLUE}Backing up current installation...${NC}"
    
    BACKUP_DIR="/opt/anidata/backup/$(date +%Y%m%d-%H%M%S)"
    mkdir -p $BACKUP_DIR
    
    # Backup configuration files
    cp -r /opt/anidata/config $BACKUP_DIR/ 2>/dev/null || true
    
    # Backup certificates
    cp -r /opt/anidata/certs $BACKUP_DIR/ 2>/dev/null || true
    
    # Backup custom user data
    cp -r /opt/anidata/data $BACKUP_DIR/ 2>/dev/null || true
    
    echo -e "${GREEN}Installation backed up to ${BACKUP_DIR}${NC}"
}

# Download update package
download_update() {
    echo -e "${BLUE}Downloading update package...${NC}"
    
    # In a real implementation, this would download from a server
    # For this demo, we'll simulate a download
    echo -e "${GREEN}Update package downloaded successfully.${NC}"
}

# Apply update
apply_update() {
    echo -e "${BLUE}Applying update...${NC}"
    
    # Update core files
    echo -e "  ${YELLOW}Updating core components...${NC}"
    cp -r ../core/* /opt/anidata/ 2>/dev/null || true
    
    # Update UI files
    echo -e "  ${YELLOW}Updating UI components...${NC}"
    cp -r ../ui/* /opt/anidata/ 2>/dev/null || true
    
    # Update scripts
    echo -e "  ${YELLOW}Updating scripts...${NC}"
    mkdir -p /opt/anidata/scripts
    cp -r ../scripts/* /opt/anidata/scripts/ 2>/dev/null || true
    
    # Update version file
    echo "$LATEST_VERSION" > /opt/anidata/VERSION
    
    echo -e "${GREEN}Update applied successfully.${NC}"
}

# Update configuration
update_configuration() {
    echo -e "${BLUE}Updating configuration files...${NC}"
    
    # In a real implementation, this would update configurations while preserving user settings
    # For this demo, we'll just display a message
    echo -e "${GREEN}Configuration updated.${NC}"
}

# Restart services
restart_services() {
    echo -e "${BLUE}Restarting services...${NC}"
    
    # Reload systemd configuration
    systemctl daemon-reload
    
    # Restart service if it was running before update
    if [ "$SERVICE_WAS_RUNNING" = true ]; then
        echo -e "${YELLOW}Restarting AniData VPN service...${NC}"
        systemctl start anidata.service
        
        # Verify service is running
        if systemctl is-active --quiet anidata.service; then
            echo -e "${GREEN}AniData VPN service restarted successfully.${NC}"
        else
            echo -e "${RED}Failed to restart AniData VPN service.${NC}"
            echo -e "${YELLOW}Please try starting it manually: 'systemctl start anidata.service'${NC}"
        fi
    else
        echo -e "${YELLOW}AniData VPN service was not running before update.${NC}"
        echo -e "${YELLOW}You can start it with: 'systemctl start anidata.service'${NC}"
    fi
}

# Display update summary
display_summary() {
    echo -e "\n${GREEN}AniData VPN has been updated successfully!${NC}"
    echo -e "Previous version: ${YELLOW}${CURRENT_VERSION}${NC}"
    echo -e "Current version: ${GREEN}${LATEST_VERSION}${NC}"
    echo -e "\n${BLUE}What's new in this version:${NC}"
    echo -e "- Improved connection stability"
    echo -e "- Enhanced security features"
    echo -e "- Better server selection algorithm"
    echo -e "- UI performance improvements"
    echo -e "- Bug fixes and stability improvements"
    echo -e "\n${YELLOW}If you encounter any issues, please report them to our support team.${NC}"
    echo -e "${BLUE}Thank you for using AniData VPN!${NC}\n"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                FORCE_UPDATE=true
                shift
                ;;
            --no-restart)
                NO_RESTART=true
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --force      Force update even if already at the latest version"
                echo "  --no-restart Don't restart services after update"
                echo "  --help       Display this help message"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Main update function
main() {
    # Parse command line arguments
    parse_args "$@"
    
    display_logo
    check_root
    check_vpn_service
    check_current_version
    check_available_updates
    backup_installation
    download_update
    apply_update
    update_configuration
    
    if [ "$NO_RESTART" != "true" ]; then
        restart_services
    else
        echo -e "${YELLOW}Services not restarted as requested.${NC}"
    fi
    
    display_summary
}

# Set default values
FORCE_UPDATE=false
NO_RESTART=false
SERVICE_WAS_RUNNING=false

# Run the update
main "$@"

exit 0