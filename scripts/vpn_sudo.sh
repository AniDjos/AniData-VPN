#!/bin/bash
# VPN_anicet - Script d'élévation de privilèges pour les opérations VPN
# © 2023 AniData - All Rights Reserved

# Vérifier si le script est exécuté en tant que root
if [[ $EUID -ne 0 ]]; then
    echo "Ce script doit être exécuté en tant que root" 
    exit 1
fi

# Définir les opérations autorisées
ALLOWED_OPERATIONS=("create_interface" "delete_interface" "set_ip" "set_route" "set_dns" "set_wg")

# Vérifier que l'opération est autorisée
if [[ $# -lt 1 || ! " ${ALLOWED_OPERATIONS[*]} " =~ " $1 " ]]; then
    echo "Usage: $0 <operation> [arguments...]"
    echo "Operations autorisées: ${ALLOWED_OPERATIONS[*]}"
    exit 1
fi

OPERATION=$1
shift

# Exécuter l'opération demandée
case $OPERATION in
    create_interface)
        # Format attendu: create_interface <interface_name>
        if [[ $# -ne 1 ]]; then
            echo "Usage: $0 create_interface <interface_name>"
            exit 1
        fi
        INTERFACE=$1
        
        # Vérifier que le nom d'interface est valide (anidata0, anidata1, etc.)
        if [[ ! $INTERFACE =~ ^anidata[0-9]+$ ]]; then
            echo "Nom d'interface invalide. Doit être de la forme anidataX où X est un chiffre."
            exit 1
        fi
        
        # Créer l'interface WireGuard
        ip link add $INTERFACE type wireguard
        exit $?
        ;;
        
    delete_interface)
        # Format attendu: delete_interface <interface_name>
        if [[ $# -ne 1 ]]; then
            echo "Usage: $0 delete_interface <interface_name>"
            exit 1
        fi
        INTERFACE=$1
        
        # Vérifier que le nom d'interface est valide
        if [[ ! $INTERFACE =~ ^anidata[0-9]+$ ]]; then
            echo "Nom d'interface invalide. Doit être de la forme anidataX où X est un chiffre."
            exit 1
        fi
        
        # Supprimer l'interface
        ip link set down dev $INTERFACE
        ip link del $INTERFACE
        exit $?
        ;;
        
    set_ip)
        # Format attendu: set_ip <interface_name> <ip_address> <mtu>
        if [[ $# -ne 3 ]]; then
            echo "Usage: $0 set_ip <interface_name> <ip_address> <mtu>"
            exit 1
        fi
        INTERFACE=$1
        IP_ADDRESS=$2
        MTU=$3
        
        # Vérifier que le nom d'interface est valide
        if [[ ! $INTERFACE =~ ^anidata[0-9]+$ ]]; then
            echo "Nom d'interface invalide. Doit être de la forme anidataX où X est un chiffre."
            exit 1
        fi
        
        # Configurer l'IP et MTU
        ip addr add $IP_ADDRESS dev $INTERFACE
        ip link set mtu $MTU dev $INTERFACE
        ip link set up dev $INTERFACE
        exit $?
        ;;
        
    set_route)
        # Format attendu: set_route <interface_name> <default_gateway>
        if [[ $# -ne 2 ]]; then
            echo "Usage: $0 set_route <interface_name> <default_gateway>"
            exit 1
        fi
        INTERFACE=$1
        DEFAULT_GW=$2
        
        # Vérifier que le nom d'interface est valide
        if [[ ! $INTERFACE =~ ^anidata[0-9]+$ ]]; then
            echo "Nom d'interface invalide. Doit être de la forme anidataX où X est un chiffre."
            exit 1
        fi
        
        # Activer le forwarding IP
        echo 1 > /proc/sys/net/ipv4/ip_forward
        
        # Configurer la route par défaut
        ip route add default dev $INTERFACE
        exit $?
        ;;
        
    set_dns)
        # Format attendu: set_dns <dns_file>
        if [[ $# -ne 1 ]]; then
            echo "Usage: $0 set_dns <dns_file>"
            exit 1
        fi
        DNS_FILE=$1
        
        # Vérifier que le fichier existe
        if [[ ! -f $DNS_FILE ]]; then
            echo "Fichier DNS introuvable: $DNS_FILE"
            exit 1
        fi
        
        # Sauvegarder resolv.conf et appliquer le nouveau
        if [[ ! -f /etc/resolv.conf.anidata.bak ]]; then
            cp /etc/resolv.conf /etc/resolv.conf.anidata.bak
        fi
        cp $DNS_FILE /etc/resolv.conf
        exit $?
        ;;
        
    set_wg)
        # Format attendu: set_wg <interface_name> <private_key_file> <peer_public_key> <endpoint> <allowed_ips> <keepalive>
        if [[ $# -ne 6 ]]; then
            echo "Usage: $0 set_wg <interface_name> <private_key_file> <peer_public_key> <endpoint> <allowed_ips> <keepalive>"
            exit 1
        fi
        INTERFACE=$1
        PRIVATE_KEY_FILE=$2
        PEER_PUBLIC_KEY=$3
        ENDPOINT=$4
        ALLOWED_IPS=$5
        KEEPALIVE=$6
        
        # Vérifier que le nom d'interface est valide
        if [[ ! $INTERFACE =~ ^anidata[0-9]+$ ]]; then
            echo "Nom d'interface invalide. Doit être de la forme anidataX où X est un chiffre."
            exit 1
        fi
        
        # Vérifier que le fichier de clé privée existe
        if [[ ! -f $PRIVATE_KEY_FILE ]]; then
            echo "Fichier de clé privée introuvable: $PRIVATE_KEY_FILE"
            exit 1
        fi
        
        # Configurer WireGuard
        wg set $INTERFACE private-key $PRIVATE_KEY_FILE
        wg set $INTERFACE peer $PEER_PUBLIC_KEY endpoint $ENDPOINT allowed-ips $ALLOWED_IPS persistent-keepalive $KEEPALIVE
        exit $?
        ;;
        
    *)
        echo "Opération non reconnue: $OPERATION"
        exit 1
        ;;
esac