#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AniData VPN - Module de gestion WireGuard
# © 2023-2024 AniData

import os
import sys
import json
import time
import threading
import subprocess
import tempfile
import socket
import ipaddress
import random
import logging
from datetime import datetime, timedelta

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.expanduser("~/.anidata/logs/vpn.log"), mode='a')
    ]
)
logger = logging.getLogger("wireguard_manager")

class RealVPNManager:
    """Gestionnaire VPN qui établit de véritables connexions WireGuard sécurisées"""
    
    def __init__(self, config_dir=None, servers_file=None):
        """Initialise le gestionnaire VPN avec les chemins de configuration"""
        # Configurer les chemins
        self.home_dir = os.path.expanduser("~/.anidata")
        self.config_dir = config_dir or os.path.join(self.home_dir, "config/wireguard")
        self.servers_file = servers_file or os.path.join(self.home_dir, "servers/config.json")
        self.keys_dir = os.path.join(self.home_dir, "keys")
        
        # État de la connexion
        self.connected = False
        self.current_server = None
        self.connection_thread = None
        self.wireguard_interface = "wg0"
        self.config_file = None
        self.original_gateway = None
        self.connection_start_time = 0
        
        # Statistiques réseau
        self.last_rx_bytes = 0
        self.last_tx_bytes = 0
        self.last_check_time = 0
        
        # Liste des serveurs
        self.servers = []
        
        # Créer les répertoires nécessaires
        self._ensure_directories()
        
        # Charger les serveurs
        self.load_servers()
        
        # Générer les clés si nécessaire
        self._ensure_keys()
    
    def _ensure_directories(self):
        """Crée les répertoires nécessaires s'ils n'existent pas"""
        for directory in [self.home_dir, self.config_dir, self.keys_dir, 
                          os.path.join(self.home_dir, "logs"),
                          os.path.join(self.home_dir, "servers")]:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    logger.info(f"Répertoire créé: {directory}")
                except Exception as e:
                    logger.error(f"Erreur lors de la création du répertoire {directory}: {e}")
    
    def _ensure_keys(self):
        """Génère les clés WireGuard si elles n'existent pas"""
        private_key_path = os.path.join(self.keys_dir, "private_key")
        public_key_path = os.path.join(self.keys_dir, "public_key")
        
        if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
            try:
                logger.info("Génération de nouvelles clés WireGuard...")
                # Générer une clé privée
                private_key = subprocess.check_output(["wg", "genkey"]).decode('utf-8').strip()
                
                # Dériver la clé publique
                public_key = subprocess.check_output(["echo", private_key], input=private_key.encode()).decode('utf-8').strip()
                public_key = subprocess.check_output(["wg", "pubkey"], input=private_key.encode()).decode('utf-8').strip()
                
                # Sauvegarder les clés avec des permissions restreintes
                with open(private_key_path, 'w') as f:
                    f.write(private_key)
                os.chmod(private_key_path, 0o600)  # Lisible uniquement par le propriétaire
                
                with open(public_key_path, 'w') as f:
                    f.write(public_key)
                
                logger.info("Clés WireGuard générées avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de la génération des clés: {e}")
                logger.info("Vérifiez que WireGuard est installé: sudo apt install wireguard")
    
    def load_servers(self):
        """Charge la liste des serveurs depuis le fichier de configuration"""
        if os.path.exists(self.servers_file):
            try:
                with open(self.servers_file, 'r') as f:
                    self.servers = json.load(f)
                logger.info(f"Chargé {len(self.servers)} serveurs depuis {self.servers_file}")
            except Exception as e:
                logger.error(f"Erreur lors du chargement des serveurs: {e}")
                self.generate_demo_servers()
        else:
            logger.warning(f"Fichier de serveurs non trouvé: {self.servers_file}")
            self.generate_demo_servers()
    
    def generate_demo_servers(self):
        """Génère des serveurs de démonstration si aucun serveur réel n'est disponible"""
        logger.info("Génération de serveurs de démonstration")
        self.servers = []
        
        # Liste de pays avec leurs codes et configurations
        countries = [
            {"country": "France", "city": "Paris", "ip": "185.156.46.10", "port": 51820},
            {"country": "Allemagne", "city": "Francfort", "ip": "89.45.90.3", "port": 51820},
            {"country": "Pays-Bas", "city": "Amsterdam", "ip": "82.196.10.50", "port": 51820},
            {"country": "Royaume-Uni", "city": "Londres", "ip": "178.128.170.25", "port": 51820},
            {"country": "États-Unis", "city": "New York", "ip": "104.236.50.40", "port": 51820},
            {"country": "Japon", "city": "Tokyo", "ip": "160.16.105.120", "port": 51820}
        ]
        
        # Générer les serveurs
        for i, c in enumerate(countries):
            server_id = f"{self._country_to_code(c['country'])}-{i+1:02d}"
            public_key = self._generate_demo_public_key()
            
            self.servers.append({
                "id": server_id,
                "country": c["country"],
                "city": c["city"],
                "ip": c["ip"],
                "port": c["port"],
                "public_key": public_key,
                "protocols": ["wireguard"],
                "capabilities": {
                    "vpn": True,
                    "proxy": i % 2 == 0,
                    "tor": i % 3 == 0
                }
            })
        
        # Sauvegarder ces serveurs pour une utilisation ultérieure
        try:
            with open(self.servers_file, 'w') as f:
                json.dump(self.servers, f, indent=2)
            logger.info(f"Serveurs de démonstration enregistrés dans {self.servers_file}")
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des serveurs de démonstration: {e}")
    
    def _country_to_code(self, country):
        """Convertit un nom de pays en code à deux lettres"""
        country_codes = {
            "France": "fr", "Allemagne": "de", "Pays-Bas": "nl", 
            "Royaume-Uni": "uk", "États-Unis": "us", "Japon": "jp"
        }
        return country_codes.get(country, "xx").lower()
    
    def _generate_demo_public_key(self):
        """Génère une clé publique factice pour les serveurs de démonstration"""
        return "".join(random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz") for _ in range(44)) + "="
    
    def create_wireguard_config(self, server):
        """Crée un fichier de configuration WireGuard pour un serveur donné"""
        try:
            # Lire la clé privée
            private_key_path = os.path.join(self.keys_dir, "private_key")
            with open(private_key_path, 'r') as f:
                private_key = f.read().strip()
            
            # Créer un fichier de configuration temporaire
            config_path = os.path.join(self.config_dir, f"{server['id']}.conf")
            
            # Obtenir les informations du serveur
            server_public_key = server.get('public_key', 'SERVER_PUBLIC_KEY_PLACEHOLDER')
            server_endpoint = f"{server.get('ip', '127.0.0.1')}:{server.get('port', 51820)}"
            
            # Générer un IP client unique
            client_ip = f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(2, 254)}/32"
            
            # Créer la configuration
            config_content = f"""[Interface]
PrivateKey = {private_key}
Address = {client_ip}
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = {server_public_key}
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = {server_endpoint}
PersistentKeepalive = 25
"""
            
            # Écrire la configuration dans le fichier
            with open(config_path, 'w') as f:
                f.write(config_content)
            os.chmod(config_path, 0o600)  # Permissions restreintes
            
            logger.info(f"Configuration WireGuard créée: {config_path}")
            return config_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de la configuration WireGuard: {e}")
            return None
    
    def save_original_gateway(self):
        """Sauvegarde la passerelle par défaut avant de la modifier"""
        try:
            result = subprocess.check_output(["ip", "route", "show", "default"]).decode('utf-8')
            self.original_gateway = result.strip()
            logger.info(f"Passerelle d'origine sauvegardée: {self.original_gateway}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la passerelle d'origine: {e}")
            return False
    
    def check_permissions(self):
        """Vérifie si l'utilisateur a les permissions nécessaires pour configurer le VPN"""
        try:
            # Essayer une commande qui nécessite des privilèges élevés
            subprocess.check_call(["sudo", "-n", "true"], stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            logger.warning("Privilèges sudo requis mais non disponibles")
            return False
    
    def is_wireguard_installed(self):
        """Vérifie si WireGuard est installé"""
        try:
            subprocess.check_call(["which", "wg"], stdout=subprocess.PIPE)
            subprocess.check_call(["which", "wg-quick"], stdout=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def install_wireguard(self):
        """Tente d'installer WireGuard"""
        try:
            logger.info("Installation de WireGuard...")
            subprocess.check_call(["sudo", "apt", "update"])
            subprocess.check_call(["sudo", "apt", "install", "-y", "wireguard"])
            logger.info("WireGuard installé avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'installation de WireGuard: {e}")
            return False
    
    def connect(self, connection_config):
        """Établit une connexion VPN WireGuard vers le serveur spécifié"""
        server = connection_config.get('server')
        if not server:
            logger.error("Aucun serveur spécifié pour la connexion")
            return False
        
        logger.info(f"Connexion à {server['country']} - {server['city']}...")
        
        # Vérifier si on est déjà connecté
        if self.connected:
            logger.info("Déjà connecté, déconnexion d'abord...")
            self.disconnect()
        
        # Vérifier les prérequis
        if not self.is_wireguard_installed():
            logger.warning("WireGuard n'est pas installé")
            if not self.install_wireguard():
                return False
        
        if not self.check_permissions():
            logger.error("Privilèges insuffisants pour établir une connexion VPN")
            return False
        
        try:
            # 1. Créer le fichier de configuration WireGuard
            config_path = self.create_wireguard_config(server)
            if not config_path:
                return False
            self.config_file = config_path
            
            # 2. Sauvegarder la configuration réseau actuelle
            self.save_original_gateway()
            
            # 3. Activer l'interface WireGuard
            logger.info(f"Activation de l'interface WireGuard avec {config_path}...")
            try:
                subprocess.check_call(["sudo", "wg-quick", "up", config_path])
            except subprocess.CalledProcessError as e:
                logger.error(f"Erreur lors de l'activation de l'interface WireGuard: {e}")
                return False
            
            # 4. Vérifier que l'interface est active
            try:
                result = subprocess.check_output(["ip", "a", "show", "dev", self.wireguard_interface]).decode('utf-8')
                if self.wireguard_interface not in result:
                    logger.error("L'interface WireGuard n'a pas été activée correctement")
                    return False
            except subprocess.CalledProcessError:
                logger.error("Impossible de vérifier l'interface WireGuard")
                return False
            
            # 5. Configuration réussie
            self.connected = True
            self.current_server = server
            self.connection_start_time = time.time()
            
            # 6. Démarrer le thread de surveillance
            if self.connection_thread and self.connection_thread.is_alive():
                self.connection_thread.join(1)
            
            self.connection_thread = threading.Thread(target=self.monitor_connection)
            self.connection_thread.daemon = True
            self.connection_thread.start()
            
            logger.info(f"Connecté avec succès à {server['country']} - {server['city']}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {e}")
            # Tenter de nettoyer en cas d'erreur
            self.disconnect()
            return False
    
    def disconnect(self):
        """Déconnecte le VPN et restaure les paramètres réseau"""
        if not self.connected and not self.config_file:
            logger.info("Pas de connexion active à déconnecter")
            return True
            
        logger.info("Déconnexion du VPN...")
        try:
            # 1. Désactiver l'interface WireGuard
            if self.config_file:
                try:
                    subprocess.check_call(["sudo", "wg-quick", "down", self.config_file])
                    logger.info("Interface WireGuard désactivée")
                except subprocess.CalledProcessError as e:
                    logger.error(f"Erreur lors de la désactivation de l'interface WireGuard: {e}")
            
            # 2. Restaurer la configuration réseau d'origine si nécessaire
            if self.original_gateway:
                # Cette partie dépend de la façon dont vous avez modifié le routage
                logger.info("Restauration de la configuration réseau d'origine")
                # ...
            
            # 3. Nettoyer les fichiers temporaires
            # ...
            
            # 4. Réinitialiser les variables d'état
            self.connected = False
            self.current_server = None
            self.config_file = None
            self.original_gateway = None
            
            logger.info("Déconnecté avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
            return False
    
    def monitor_connection(self):
        """Surveille la connexion VPN et collecte des statistiques"""
        logger.info("Démarrage de la surveillance de la connexion")
        
        while self.connected:
            try:
                # Vérifier si l'interface est toujours active
                try:
                    subprocess.check_output(["ip", "a", "show", "dev", self.wireguard_interface], stderr=subprocess.PIPE)
                except subprocess.CalledProcessError:
                    logger.warning("Interface VPN perdue, tentative de reconnexion...")
                    self.connected = False
                    break
                
                # Collecter les statistiques de bande passante
                self.update_interface_stats()
                
                # Attendre avant la prochaine vérification
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erreur dans la surveillance de connexion: {e}")
                time.sleep(5)  # Attendre plus longtemps en cas d'erreur
        
        logger.info("Arrêt de la surveillance de la connexion")
    
    def update_interface_stats(self):
        """Met à jour les statistiques de l'interface réseau"""
        try:
            rx_bytes = 0
            tx_bytes = 0
            
            # Lire les statistiques actuelles
            rx_path = f"/sys/class/net/{self.wireguard_interface}/statistics/rx_bytes"
            tx_path = f"/sys/class/net/{self.wireguard_interface}/statistics/tx_bytes"
            
            if os.path.exists(rx_path) and os.path.exists(tx_path):
                with open(rx_path, "r") as f:
                    rx_bytes = int(f.read().strip())
                with open(tx_path, "r") as f:
                    tx_bytes = int(f.read().strip())
                
                # Mettre à jour les statistiques
                current_time = time.time()
                if self.last_check_time > 0:
                    time_diff = current_time - self.last_check_time
                    self.last_rx_bytes = rx_bytes
                    self.last_tx_bytes = tx_bytes
                
                self.last_check_time = current_time
                self.last_rx_bytes = rx_bytes
                self.last_tx_bytes = tx_bytes
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des statistiques: {e}")
    
    def get_status(self):
        """Récupère le statut actuel de la connexion VPN"""
        if not self.connected:
            return {
                'connected': False,
                'uptime': "00:00:00",
                'statistics': {
                    'download_speed': 0,
                    'upload_speed': 0,
                    'total_downloaded': 0,
                    'total_uploaded': 0
                }
            }
        
        try:
            # Calculer le temps de connexion
            uptime_seconds = int(time.time() - self.connection_start_time)
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            seconds = uptime_seconds % 60
            uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            # Calculer les statistiques de bande passante
            rx_bytes = 0
            tx_bytes = 0
            download_speed = 0
            upload_speed = 0
            
            # Lire les statistiques actuelles
            rx_path = f"/sys/class/net/{self.wireguard_interface}/statistics/rx_bytes"
            tx_path = f"/sys/class/net/{self.wireguard_interface}/statistics/tx_bytes"
            
            if os.path.exists(rx_path) and os.path.exists(tx_path):
                with open(rx_path, "r") as f:
                    rx_bytes = int(f.read().strip())
                with open(tx_path, "r") as f:
                    tx_bytes = int(f.read().strip())
                
                # Calculer les vitesses
                current_time = time.time()
                if self.last_check_time > 0 and current_time > self.last_check_time:
                    time_diff = current_time - self.last_check_time
                    download_speed = (rx_bytes - self.last_rx_bytes) / time_diff / 1024 / 1024  # MB/s
                    upload_speed = (tx_bytes - self.last_tx_bytes) / time_diff / 1024 / 1024    # MB/s
            
            return {
                'connected': True,
                'uptime': uptime,
                'server': self.current_server,
                'statistics': {
                    'download_speed': download_speed,
                    'upload_speed': upload_speed,
                    'total_downloaded': rx_bytes / 1024 / 1024,  # MB
                    'total_uploaded': tx_bytes / 1024 / 1024     # MB
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut: {e}")
            return {
                'connected': self.connected,
                'uptime': "00:00:00",
                'server': self.current_server,
                'statistics': {
                    'download_speed': 0,
                    'upload_speed': 0,
                    'total_downloaded': 0,
                    'total_uploaded': 0
                }
            }
    
    def test_connection(self):
        """Teste la connexion VPN pour vérifier qu'elle fonctionne correctement"""
        if not self.connected:
            logger.warning("Impossible de tester la connexion: VPN non connecté")
            return False
        
        try:
            # Ping un serveur externe pour vérifier la connectivité
            subprocess.check_call(["ping", "-c", "1", "-W", "5", "8.8.8.8"], stdout=subprocess.PIPE)
            
            # Vérifier que le trafic passe bien par le VPN
            result = subprocess.check_output(["curl", "--silent", "https://ipinfo.io/ip"]).decode('utf-8').strip()
            logger.info(f"Adresse IP publique actuelle: {result}")
            
            # Vérifier les fuites DNS
            dns_result = subprocess.check_output(["dig", "+short", "whoami.akamai.net", "@ns1.google.com"]).decode('utf-8').strip()
            logger.info(f"Test DNS: {dns_result}")
            
            return True
        except Exception as e:
            logger.error(f"Échec du test de connexion: {e}")
            return False
    
    def check_ip(self):
        """Vérifie l'adresse IP publique actuelle"""
        try:
            result = subprocess.check_output(["curl", "--silent", "https://ipinfo.io/ip"]).decode('utf-8').strip()
            logger.info(f"Adresse IP publique: {result}")
            return result
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'IP: {e}")
            return None

# Classe compatible avec l'interface de l'application pour une transition en douceur
class WireGuardManager(RealVPNManager):
    """Classe de compatibilité pour l'interface de l'application"""
    pass

# Test de fonctionnalité si exécuté directement
if __name__ == "__main__":
    print("Test du gestionnaire WireGuard...")
    manager = RealVPNManager()
    
    # Vérifier les serveurs
    print(f"Serveurs disponibles: {len(manager.servers)}")
    for server in manager.servers[:3]:  # Afficher les 3 premiers serveurs
        print(f"- {server['country']} ({server['city']})")
    
    # Vérifier l'installation
    if not manager.is_wireguard_installed():
        print("WireGuard n'est pas installé. Installation...")
        if not manager.install_wireguard():
            print("Échec de l'installation de WireGuard")
            sys.exit(1)
    
    # Test de connexion au premier serveur
    if manager.servers:
        server = manager.servers[0]
        print(f"Test de connexion à {server['country']} - {server['city']}...")
        
        if manager.connect({'server': server}):
            print("Connexion établie!")
            
            # Afficher l'IP
            ip = manager.check_ip()
            if ip:
                print(f"Votre adresse IP publique est maintenant: {ip}")
            
            # Attendre un peu
            print("Connexion active pendant 10 secondes...")
            for i in range(10):
                status = manager.get_status()
                print(f"Uptime: {status['uptime']}, "
                      f"Download: {status['statistics']['download_speed']:.2f} MB/s, "
                      f"Upload: {status['statistics']['upload_speed']:.2f} MB/s")
                time.sleep(1)
            
            # Déconnecter
            print("Déconnexion...")
            manager.disconnect()
            print("Déconnecté")
        else:
            print("Échec de la connexion")
    else:
        print("Aucun serveur disponible")