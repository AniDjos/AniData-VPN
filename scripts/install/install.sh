#!/bin/bash

# AniData VPN Installation Script
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
    echo -e "${YELLOW}Next Generation VPN - Installation Script${NC}\n"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}Please run as root or with sudo privileges${NC}"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    echo -e "${BLUE}Checking system requirements...${NC}"
    
    # Check OS
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
        echo -e "- Detected OS: ${GREEN}$OS $VER${NC}"
    else
        echo -e "${RED}Unsupported operating system${NC}"
        exit 1
    fi
    
    # Check RAM
    MEM_TOTAL=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    MEM_TOTAL_GB=$(echo "scale=2; $MEM_TOTAL/1024/1024" | bc)
    echo -e "- Available RAM: ${GREEN}${MEM_TOTAL_GB}GB${NC}"
    
    if (( $(echo "$MEM_TOTAL_GB < 1.5" | bc -l) )); then
        echo -e "${RED}Insufficient RAM. Minimum 2GB recommended.${NC}"
        exit 1
    fi
    
    # Check disk space
    DISK_SPACE=$(df -h / | awk 'NR==2 {print $4}' | sed 's/G//')
    echo -e "- Available disk space: ${GREEN}${DISK_SPACE}GB${NC}"
    
    if (( $(echo "$DISK_SPACE < 5" | bc -l) )); then
        echo -e "${RED}Insufficient disk space. Minimum 5GB required.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}System requirements check passed!${NC}\n"
}

# Install dependencies
install_dependencies() {
    echo -e "${BLUE}Installing dependencies...${NC}"
    
    # Update package lists
    if [[ "$OS" == "ubuntu" || "$OS" == "debian" ]]; then
        apt-get update
        apt-get install -y python3 python3-pip python3-dev build-essential libssl-dev \
            libffi-dev python3-setuptools python3-venv curl wget git iptables net-tools \
            network-manager ufw wireguard openvpn libsodium-dev
    elif [[ "$OS" == "fedora" || "$OS" == "centos" || "$OS" == "rhel" ]]; then
        dnf update -y
        dnf install -y python3 python3-pip python3-devel gcc openssl-devel \
            libffi-devel curl wget git iptables NetworkManager ufw wireguard-tools \
            openvpn libsodium-devel
    elif [[ "$OS" == "arch" || "$OS" == "manjaro" ]]; then
        pacman -Sy --noconfirm
        pacman -S --noconfirm python python-pip gcc openssl \
            libffi curl wget git iptables networkmanager ufw wireguard-tools \
            openvpn libsodium
    else
        echo -e "${RED}Unsupported distribution: $OS${NC}"
        exit 1
    fi
    
    # Install Python dependencies
    echo -e "${BLUE}Installing Python dependencies...${NC}"
    python3 -m pip install --upgrade pip
    python3 -m pip install scapy pyroute2 paramiko cryptography pycryptodome \
        tensorflow pytorch dnspython requests flask argon2-cffi numpy pandas
    
    echo -e "${GREEN}Dependencies installed successfully!${NC}\n"
}

# Configure firewall
configure_firewall() {
    echo -e "${BLUE}Configuring firewall...${NC}"
    
    # Enable UFW
    ufw --force enable
    
    # Set default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH
    ufw allow ssh
    
    # Allow VPN protocols
    ufw allow 1194/udp # OpenVPN
    ufw allow 1194/tcp # OpenVPN
    ufw allow 1701/udp # L2TP
    ufw allow 500/udp  # IKEv2
    ufw allow 4500/udp # IKEv2 NAT-T
    ufw allow 51820/udp # WireGuard
    
    echo -e "${GREEN}Firewall configured successfully!${NC}\n"
}

# Configure network
configure_network() {
    echo -e "${BLUE}Configuring network settings...${NC}"
    
    # Enable IP forwarding
    echo 1 > /proc/sys/net/ipv4/ip_forward
    echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
    
    # Prevent IP spoofing
    echo "net.ipv4.conf.all.rp_filter = 1" >> /etc/sysctl.conf
    echo "net.ipv4.conf.default.rp_filter = 1" >> /etc/sysctl.conf
    
    # Disable ICMP redirects
    echo "net.ipv4.conf.all.accept_redirects = 0" >> /etc/sysctl.conf
    echo "net.ipv4.conf.all.send_redirects = 0" >> /etc/sysctl.conf
    echo "net.ipv4.conf.default.accept_redirects = 0" >> /etc/sysctl.conf
    echo "net.ipv4.conf.default.send_redirects = 0" >> /etc/sysctl.conf
    
    # Apply sysctl changes
    sysctl -p
    
    echo -e "${GREEN}Network settings configured successfully!${NC}\n"
}

# Create installation directory
create_directories() {
    echo -e "${BLUE}Creating installation directories...${NC}"
    
    # Create directories
    mkdir -p /opt/anidata/bin
    mkdir -p /opt/anidata/config
    mkdir -p /opt/anidata/logs
    mkdir -p /opt/anidata/data
    mkdir -p /opt/anidata/certs
    
    # Set permissions
    chmod 700 /opt/anidata/config
    chmod 700 /opt/anidata/certs
    
    echo -e "${GREEN}Installation directories created successfully!${NC}\n"
}

# Install core components
install_core() {
    echo -e "${BLUE}Installing core components...${NC}"
    
    # Copy core files
    if [ -d "../core" ]; then
        cp -r ../core/* /opt/anidata/
        echo -e "${GREEN}Core components installed successfully!${NC}\n"
    else
        echo -e "${RED}Core directory not found!${NC}"
        exit 1
    fi
}

# Install UI components
install_ui() {
    echo -e "${BLUE}Installing UI components...${NC}"
    
    # Copy UI files
    if [ -d "../ui" ]; then
        cp -r ../ui/* /opt/anidata/
        echo -e "${GREEN}UI components installed successfully!${NC}\n"
    else
        echo -e "${RED}UI directory not found!${NC}"
        exit 1
    fi
}

# Generate certificates
generate_certificates() {
    echo -e "${BLUE}Generating certificates...${NC}"
    
    # Generate CA key and certificate
    openssl genrsa -out /opt/anidata/certs/ca.key 4096
    openssl req -new -x509 -days 3650 -key /opt/anidata/certs/ca.key \
        -out /opt/anidata/certs/ca.crt -subj "/CN=AniData VPN CA"
    
    # Generate server key and certificate
    openssl genrsa -out /opt/anidata/certs/server.key 4096
    openssl req -new -key /opt/anidata/certs/server.key \
        -out /opt/anidata/certs/server.csr -subj "/CN=AniData VPN Server"
    openssl x509 -req -days 3650 -in /opt/anidata/certs/server.csr \
        -CA /opt/anidata/certs/ca.crt -CAkey /opt/anidata/certs/ca.key \
        -set_serial 01 -out /opt/anidata/certs/server.crt
    
    # Generate Diffie-Hellman parameters
    openssl dhparam -out /opt/anidata/certs/dh.pem 2048
    
    # Set permissions
    chmod 600 /opt/anidata/certs/*
    
    echo -e "${GREEN}Certificates generated successfully!${NC}\n"
}

# Create system service
create_service() {
    echo -e "${BLUE}Creating system service...${NC}"
    
    # Create systemd service file
    cat > /etc/systemd/system/anidata.service << EOF
[Unit]
Description=AniData VPN Service
After=network.target

[Service]
Type=simple
ExecStart=/opt/anidata/bin/anidata-service
Restart=on-failure
RestartSec=5
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable anidata.service
    
    echo -e "${GREEN}System service created successfully!${NC}\n"
}

# Create symbolic links
create_symlinks() {
    echo -e "${BLUE}Creating symbolic links...${NC}"
    
    # Create symlinks for command-line utilities
    ln -sf /opt/anidata/bin/anidata /usr/local/bin/anidata
    
    echo -e "${GREEN}Symbolic links created successfully!${NC}\n"
}

# Main installation function
main() {
    display_logo
    check_root
    check_requirements
    
    echo -e "${YELLOW}Starting AniData VPN installation...${NC}\n"
    
    install_dependencies
    configure_firewall
    configure_network
    create_directories
    install_core
    install_ui
    generate_certificates
    create_service
    create_symlinks
    
    echo -e "\n${GREEN}AniData VPN has been successfully installed!${NC}"
    echo -e "${YELLOW}To start the service, run: ${NC}systemctl start anidata.service"
    echo -e "${YELLOW}To launch the UI, run: ${NC}anidata-ui"
    echo -e "\n${BLUE}Thank you for choosing AniData VPN!${NC}\n"
}

# Run the installation
main

exit 0