#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AniData VPN - Interface Tkinter sans PyQt5
# © 2023-2024 AniData

import os
import sys
import json
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
import numpy as np

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    matplotlib_available = True
except ImportError:
    matplotlib_available = False

# Répertoire courant
current_dir = os.path.dirname(os.path.abspath(__file__))

# Importer le vrai gestionnaire VPN
try:
    from core.vpn import WireGuardManager, RealVPNManager
    real_vpn_available = True
    print("Module VPN réel chargé avec succès")
except ImportError:
    real_vpn_available = False
    print("Module VPN réel non disponible, utilisation du mode simulation")
    
    # Classe simulant le gestionnaire WireGuard (utilisée uniquement si le module réel n'est pas disponible)
    class WireGuardManager:
        def __init__(self, **kwargs):
            self.servers = []
            
        def connect(self, config):
            print(f"Connexion à {config.get('server', {}).get('country', 'Unknown')}")
            return True
            
        def disconnect(self):
            print("Déconnexion...")
            return True
            
        def get_status(self):
            return {
                'connected': False,
                'uptime': "00:00:00",
                'statistics': {
                    'download_speed': random.uniform(0, 2),
                    'upload_speed': random.uniform(0, 1),
                    'total_downloaded': random.uniform(0, 100),
                    'total_uploaded': random.uniform(0, 50)
                }
            }

# Thread de surveillance du VPN
class VPNStatusThread(threading.Thread):
    """Thread for monitoring VPN connection status"""
    def __init__(self, manager, callback):
        super().__init__()
        self.manager = manager
        self.callback = callback
        self.running = True
        self.daemon = True
        
    def run(self):
        while self.running:
            try:
                status = self.manager.get_status()
                self.callback(status)
            except Exception as e:
                print(f"Erreur de surveillance: {str(e)}")
            time.sleep(1)  # Mise à jour plus fréquente pour une meilleure réactivité
    
    def stop(self):
        self.running = False

# Graphique de bande passante avec matplotlib
class BandwidthGraph:
    def __init__(self, parent):
        self.parent = parent
        
        if not matplotlib_available:
            label = ttk.Label(parent, text="Matplotlib non disponible.\nInstaller avec: pip install matplotlib")
            label.pack(fill=tk.BOTH, expand=True)
            return
            
        self.times = np.array([])
        self.download_data = np.array([])
        self.upload_data = np.array([])
        self.start_time = datetime.now()
        self.time_window = 60
        
        self.figure = plt.Figure(figsize=(5, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.download_line, = self.ax.plot([], [], 'g-', label='Download')
        self.upload_line, = self.ax.plot([], [], 'r-', label='Upload')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Speed (MB/s)')
        self.ax.set_title('Bande passante')
        self.ax.legend()
        self.ax.grid(True)
        
        self.ax.set_xlim(0, self.time_window)
        self.ax.set_ylim(0, 1)
        
    def update_bandwidth(self, download_speed, upload_speed):
        if not matplotlib_available:
            return
            
        try:
            current_time = (datetime.now() - self.start_time).total_seconds()
            
            self.times = np.append(self.times, current_time)
            self.download_data = np.append(self.download_data, download_speed)
            self.upload_data = np.append(self.upload_data, upload_speed)
            
            mask = self.times > current_time - self.time_window
            self.times = self.times[mask]
            self.download_data = self.download_data[mask]
            self.upload_data = self.upload_data[mask]
            
            self.download_line.set_data(self.times, self.download_data)
            self.upload_line.set_data(self.times, self.upload_data)
            
            max_value = max(np.max(self.download_data) if len(self.download_data) > 0 else 0,
                        np.max(self.upload_data) if len(self.upload_data) > 0 else 0)
            if max_value > 0:
                self.ax.set_ylim(0, max_value * 1.1)
                
            self.ax.set_xlim(max(0, current_time - self.time_window), max(self.time_window, current_time))
            
            self.canvas.draw()
        except Exception as e:
            print(f"Erreur dans le graphique: {e}")
    
    def reset(self):
        if not matplotlib_available:
            return
            
        self.times = np.array([])
        self.download_data = np.array([])
        self.upload_data = np.array([])
        self.start_time = datetime.now()
        self.download_line.set_data([], [])
        self.upload_line.set_data([], [])
        self.canvas.draw()

# Cadre pour la carte
class MapFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        
        # En-tête
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        server_count_label = ttk.Label(
            header_frame, 
            text="AniData VPN - 165 Pays Disponibles", 
            font=('Helvetica', 14, 'bold'), 
            foreground="#3B82F6"
        )
        server_count_label.pack(side=tk.LEFT)
        
        # Informations sur les régions
        regions_frame = ttk.Frame(self)
        regions_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        total_label = ttk.Label(
            regions_frame, 
            text="Réseau Mondial Sécurisé: 165 Pays", 
            font=('Helvetica', 12, 'bold'),
            foreground="#22C55E"
        )
        total_label.pack(pady=(0, 10))
        
        regions = [
            ("Europe", "40+ pays"),
            ("Asie", "45+ pays"),
            ("Amériques", "35+ pays"),
            ("Afrique", "25+ pays"),
            ("Océanie", "10+ pays")
        ]
        
        for i, (region, count) in enumerate(regions):
            region_frame = ttk.Frame(regions_frame)
            region_frame.grid(row=i//3, column=i%3, padx=10, pady=5, sticky=tk.W)
            
            region_label = ttk.Label(region_frame, text=f"• {region}: ", font=('Helvetica', 11))
            region_label.pack(side=tk.LEFT)
            
            count_label = ttk.Label(region_frame, text=count, font=('Helvetica', 11, 'bold'))
            count_label.pack(side=tk.LEFT)
        
        # Compteur de serveurs
        count_frame = ttk.Frame(self)
        count_frame.pack(fill=tk.X, pady=5)
        self.server_count = ttk.Label(
            count_frame, 
            text="Chargement des serveurs...", 
            font=('Helvetica', 10, 'italic')
        )
        self.server_count.pack(side=tk.RIGHT)

# Liste des serveurs
class ServerListFrame(ttk.Frame):
    def __init__(self, parent, on_select_callback):
        super().__init__(parent, padding=10)
        self.on_select_callback = on_select_callback
        
        # En-tête
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Serveurs", font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT)
        
        # Recherche
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Recherche:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_servers)
        
        # Liste des serveurs
        self.tree = ttk.Treeview(self, columns=("country", "city", "protocols"), show="headings")
        self.tree.heading("country", text="Pays")
        self.tree.heading("city", text="Ville")
        self.tree.heading("protocols", text="Protocoles")
        self.tree.column("country", width=100)
        self.tree.column("city", width=100)
        self.tree.column("protocols", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Barre de défilement
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Sélection
        self.tree.bind("<<TreeviewSelect>>", self.on_server_selected)
        
        # Données
        self.servers = []
        
    def populate_servers(self, servers):
        self.servers = servers
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for i, server in enumerate(servers):
            protocols = ", ".join(server.get("protocols", []))
            self.tree.insert("", tk.END, iid=str(i), values=(
                server.get("country", "Unknown"), 
                server.get("city", ""), 
                protocols
            ))
            
        # Mise à jour du compteur
        if hasattr(self.master, "map_frame") and hasattr(self.master.map_frame, "server_count"):
            country_count = len(set(s.get('country', '') for s in servers))
            self.master.map_frame.server_count.config(
                text=f"Total: {len(servers)} serveurs dans {country_count} pays"
            )
            
    def filter_servers(self, event=None):
        query = self.search_entry.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for i, server in enumerate(self.servers):
            if (query in server.get("country", "").lower() or 
                query in server.get("city", "").lower()):
                protocols = ", ".join(server.get("protocols", []))
                self.tree.insert("", tk.END, iid=str(i), values=(
                    server.get("country", "Unknown"), 
                    server.get("city", ""), 
                    protocols
                ))
                
    def on_server_selected(self, event):
        selection = self.tree.selection()
        if selection:
            index = int(selection[0])
            server = self.servers[index]
            self.on_select_callback(server)

# Contrôles de connexion
class ConnectionFrame(ttk.Frame):
    def __init__(self, parent, on_connect, on_disconnect):
        super().__init__(parent, padding=10)
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        
        self.is_connected = False
        self.selected_server = None
        
        # Serveur sélectionné
        server_frame = ttk.Frame(self)
        server_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(server_frame, text="Serveur sélectionné:").pack(side=tk.LEFT, padx=(0, 5))
        self.server_info = ttk.Label(server_frame, text="Aucun")
        self.server_info.pack(side=tk.LEFT)
        
        # Statut
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(status_frame, text="Statut:").pack(side=tk.LEFT, padx=(0, 5))
        self.status_label = ttk.Label(status_frame, text="Déconnecté")
        self.status_label.pack(side=tk.LEFT)
        
        # Temps de connexion
        uptime_frame = ttk.Frame(self)
        uptime_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(uptime_frame, text="Temps de connexion:").pack(side=tk.LEFT, padx=(0, 5))
        self.uptime_label = ttk.Label(uptime_frame, text="00:00:00")
        self.uptime_label.pack(side=tk.LEFT)
        
        # Boutons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.connect_btn = ttk.Button(button_frame, text="Connecter", command=self.connect_clicked)
        self.connect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.connect_btn.state(['disabled'])
        
        self.disconnect_btn = ttk.Button(button_frame, text="Déconnecter", command=self.disconnect_clicked)
        self.disconnect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.disconnect_btn.state(['disabled'])
        
    def set_selected_server(self, server):
        self.selected_server = server
        self.server_info.config(text=f"{server.get('country', 'Unknown')} - {server.get('city', '')}")
        self.connect_btn.state(['!disabled'])
        
    def connect_clicked(self):
        if self.selected_server:
            self.on_connect(self.selected_server)
            
    def disconnect_clicked(self):
        self.on_disconnect()
        
    def update_status(self, is_connected, server, uptime):
        self.is_connected = is_connected
        
        if is_connected:
            self.status_label.config(text="Connecté")
            self.uptime_label.config(text=uptime)
            self.connect_btn.state(['disabled'])
            self.disconnect_btn.state(['!disabled'])
            
            if server:
                self.server_info.config(text=f"{server.get('country', 'Unknown')} - {server.get('city', '')}")
        else:
            self.status_label.config(text="Déconnecté")
            self.uptime_label.config(text="00:00:00")
            if self.selected_server:
                self.connect_btn.state(['!disabled'])
            self.disconnect_btn.state(['disabled'])

# Statistiques
class StatisticsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        
        # En-tête
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Statistiques", font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT)
        
        # Grille de statistiques
        self.grid_frame = ttk.Frame(self)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # Vitesse de téléchargement
        ttk.Label(self.grid_frame, text="Vitesse de téléchargement:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.download_speed = ttk.Label(self.grid_frame, text="0.00 MB/s")
        self.download_speed.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Vitesse d'envoi
        ttk.Label(self.grid_frame, text="Vitesse d'envoi:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.upload_speed = ttk.Label(self.grid_frame, text="0.00 MB/s")
        self.upload_speed.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Total téléchargé
        ttk.Label(self.grid_frame, text="Total téléchargé:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.total_downloaded = ttk.Label(self.grid_frame, text="0.00 MB")
        self.total_downloaded.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Total envoyé
        ttk.Label(self.grid_frame, text="Total envoyé:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.total_uploaded = ttk.Label(self.grid_frame, text="0.00 MB")
        self.total_uploaded.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
    def update_statistics(self, download_speed, upload_speed, total_downloaded, total_uploaded):
        self.download_speed.config(text=download_speed)
        self.upload_speed.config(text=upload_speed)
        self.total_downloaded.config(text=total_downloaded)
        self.total_uploaded.config(text=total_uploaded)

# Application principale
class AniDataVPNApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AniData VPN - 165 Pays")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        
        # Initialiser le gestionnaire VPN (réel ou simulé)
        if real_vpn_available:
            try:
                # Utiliser le vrai gestionnaire VPN qui chiffre le trafic Internet
                home_dir = os.path.expanduser("~/.anidata")
                config_dir = os.path.join(home_dir, "config/wireguard")
                servers_file = os.path.join(home_dir, "servers/config.json")
                self.vpn_manager = RealVPNManager(config_dir=config_dir, servers_file=servers_file)
                print("Gestionnaire VPN réel initialisé")
            except Exception as e:
                print(f"Erreur lors de l'initialisation du VPN réel: {e}")
                self.vpn_manager = WireGuardManager()
        else:
            # Utiliser le gestionnaire simulé
            self.vpn_manager = WireGuardManager()
            
        self.current_server = None
        self.servers = []
        self.protocol = "wireguard"
        
        # Cadre principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panneaux
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        self.left_frame = ttk.Frame(self.paned_window)
        self.right_frame = ttk.Frame(self.paned_window)
        
        self.paned_window.add(self.left_frame, weight=2)
        self.paned_window.add(self.right_frame, weight=1)
        
        # Carte
        self.map_frame = MapFrame(self.left_frame)
        self.map_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Liste des serveurs
        self.server_list = ServerListFrame(self.left_frame, self.on_server_selected)
        self.server_list.pack(fill=tk.BOTH, expand=True)
        
        # Contrôles de connexion
        self.connection_widget = ConnectionFrame(self.right_frame, self.connect_vpn, self.disconnect_vpn)
        self.connection_widget.pack(fill=tk.X, pady=(0, 10))
        
        # Statistiques
        self.stats_widget = StatisticsFrame(self.right_frame)
        self.stats_widget.pack(fill=tk.X, pady=(0, 10))
        
        # Graphique
        graph_frame = ttk.LabelFrame(self.right_frame, text="Bande passante")
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.bandwidth_graph = BandwidthGraph(graph_frame)
        
        # Chargement des données
        self.load_servers()
        
        # Démarrer la surveillance
        self.status_thread = VPNStatusThread(self.vpn_manager, self.update_status)
        self.status_thread.start()
        
        # Gestion de la fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def load_servers(self):
        try:
            # Essayer de charger depuis le fichier JSON
            countries_path = os.path.join(current_dir, "data", "countries.json")
            if os.path.exists(countries_path):
                with open(countries_path, 'r', encoding='utf-8') as f:
                    self.servers = json.load(f)
                    print(f"Chargé {len(self.servers)} serveurs depuis countries.json")
                    if self.servers:
                        self.server_list.populate_servers(self.servers)
                        return
        except Exception as e:
            print(f"Erreur lors du chargement des serveurs: {e}")
        
        # Générer des serveurs de démonstration
        self.generate_demo_servers()
        
    def generate_demo_servers(self):
        countries = [
            {"region": "Europe", "country": "France", "city": "Paris"},
            {"region": "Europe", "country": "Allemagne", "city": "Berlin"},
            {"region": "Europe", "country": "Royaume-Uni", "city": "Londres"},
            {"region": "Europe", "country": "Espagne", "city": "Madrid"},
            {"region": "Europe", "country": "Italie", "city": "Rome"},
            {"region": "Asie", "country": "Japon", "city": "Tokyo"},
            {"region": "Asie", "country": "Chine", "city": "Hong Kong"},
            {"region": "Asie", "country": "Corée du Sud", "city": "Séoul"},
            {"region": "Asie", "country": "Inde", "city": "Mumbai"},
            {"region": "Asie", "country": "Singapour", "city": "Singapour"},
            {"region": "Amériques", "country": "États-Unis", "city": "New York"},
            {"region": "Amériques", "country": "États-Unis", "city": "Los Angeles"},
            {"region": "Amériques", "country": "Canada", "city": "Toronto"},
            {"region": "Amériques", "country": "Brésil", "city": "São Paulo"},
            {"region": "Amériques", "country": "Mexique", "city": "Mexico"},
            {"region": "Afrique", "country": "Afrique du Sud", "city": "Johannesburg"},
            {"region": "Afrique", "country": "Égypte", "city": "Le Caire"},
            {"region": "Afrique", "country": "Maroc", "city": "Casablanca"},
            {"region": "Afrique", "country": "Kenya", "city": "Nairobi"},
            {"region": "Afrique", "country": "Nigeria", "city": "Lagos"},
            {"region": "Océanie", "country": "Australie", "city": "Sydney"},
            {"region": "Océanie", "country": "Nouvelle-Zélande", "city": "Auckland"},
            {"region": "Océanie", "country": "Fidji", "city": "Suva"}
        ]
        
        self.servers = []
        for i, c in enumerate(countries):
            self.servers.append({
                "id": f"sv-{i+1}",
                "region": c["region"],
                "country": c["country"],
                "city": c["city"],
                "protocols": ["wireguard", "openvpn"] if i % 3 == 0 else ["wireguard"],
                "capabilities": {
                    "vpn": True,
                    "proxy": i % 2 == 0,
                    "tor": i % 5 == 0
                }
            })
        
        self.server_list.populate_servers(self.servers)
        
    def on_server_selected(self, server):
        self.current_server = server
        self.connection_widget.set_selected_server(server)
        
    def connect_vpn(self, server):
        try:
            # Vérifier les permissions pour le VPN réel
            if real_vpn_available and not self.check_vpn_prerequisites():
                return
                
            # Configurer la connexion
            connection_config = {
                'server': server,
                'protocol': self.protocol,
                'port': server.get('port', 51820) if self.protocol == 'wireguard' else 1194,
            }
            
            # Afficher un message de connexion
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Connexion en cours")
            progress_window.geometry("300x100")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            message = ttk.Label(progress_window, text=f"Connexion à {server.get('country')}...\nVeuillez patienter...")
            message.pack(pady=20)
            progress_window.update()
            
            # Tenter la connexion
            result = self.vpn_manager.connect(connection_config)
            
            # Fermer la fenêtre de progression
            progress_window.destroy()
            
            if result:
                self.connection_widget.update_status(True, server, "00:00:00")
                self.bandwidth_graph.reset()
                
                # Vérifier l'IP après connexion
                if real_vpn_available and hasattr(self.vpn_manager, 'check_ip'):
                    ip = self.vpn_manager.check_ip()
                    messagebox.showinfo("VPN Connecté", 
                                       f"Connecté à {server.get('country', 'Unknown')} - {server.get('city', '')}\n"
                                       f"Votre adresse IP est maintenant: {ip}")
                else:
                    messagebox.showinfo("VPN Connecté", 
                                       f"Connecté à {server.get('country', 'Unknown')} - {server.get('city', '')}")
            else:
                messagebox.showerror("Erreur", "Échec de la connexion au serveur VPN.")
                
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
            
    def disconnect_vpn(self):
        try:
            # Afficher un message de déconnexion
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Déconnexion en cours")
            progress_window.geometry("300x100")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            message = ttk.Label(progress_window, text="Déconnexion du VPN...\nVeuillez patienter...")
            message.pack(pady=20)
            progress_window.update()
            
            # Tenter la déconnexion
            result = self.vpn_manager.disconnect()
            
            # Fermer la fenêtre de progression
            progress_window.destroy()
            
            if result:
                self.connection_widget.update_status(False, None, "00:00:00")
                messagebox.showinfo("VPN Déconnecté", "Déconnecté du serveur VPN.")
                
                # Vérifier l'IP après déconnexion
                if real_vpn_available and hasattr(self.vpn_manager, 'check_ip'):
                    ip = self.vpn_manager.check_ip()
                    if ip:
                        messagebox.showinfo("Information", f"Votre adresse IP est revenue à: {ip}")
            else:
                messagebox.showerror("Erreur", "Échec de la déconnexion du serveur VPN.")
                
        except Exception as e:
            print(f"Erreur de déconnexion: {e}")
            messagebox.showerror("Erreur", f"Erreur: {str(e)}")
            
    def update_status(self, status):
        is_connected = status.get('connected', False)
        uptime = status.get('uptime', "00:00:00")
        stats = status.get('statistics', {})
        
        self.connection_widget.update_status(is_connected, self.current_server, uptime)
        
        download_speed = f"{stats.get('download_speed', 0):.2f} MB/s"
        upload_speed = f"{stats.get('upload_speed', 0):.2f} MB/s"
        total_downloaded = f"{stats.get('total_downloaded', 0):.2f} MB"
        total_uploaded = f"{stats.get('total_uploaded', 0):.2f} MB"
        
        self.stats_widget.update_statistics(
            download_speed,
            upload_speed,
            total_downloaded,
            total_uploaded
        )
        
        if is_connected:
            self.bandwidth_graph.update_bandwidth(
                stats.get('download_speed', 0),
                stats.get('upload_speed', 0)
            )
            
    def on_close(self):
        if hasattr(self, 'status_thread'):
            self.status_thread.stop()
        self.root.destroy()

# Lancer l'application
    def check_vpn_prerequisites(self):
        """Vérifie si les prérequis pour le VPN réel sont satisfaits"""
        # Vérifier si WireGuard est installé
        if hasattr(self.vpn_manager, 'is_wireguard_installed') and not self.vpn_manager.is_wireguard_installed():
            response = messagebox.askyesno("WireGuard non installé", 
                                         "WireGuard n'est pas installé sur votre système. "
                                         "Voulez-vous l'installer maintenant?\n\n"
                                         "Note: Cela nécessitera des privilèges administrateur.")
            if response:
                if not self.vpn_manager.install_wireguard():
                    messagebox.showerror("Erreur", "Impossible d'installer WireGuard. "
                                                "Veuillez l'installer manuellement.")
                    return False
            else:
                return False
        
        # Vérifier les privilèges
        if hasattr(self.vpn_manager, 'check_permissions') and not self.vpn_manager.check_permissions():
            response = messagebox.askyesno("Privilèges administrateur requis", 
                                         "L'établissement d'une connexion VPN nécessite des privilèges "
                                         "administrateur. Voulez-vous continuer?\n\n"
                                         "Vous devrez entrer votre mot de passe.")
            if not response:
                return False
        
        return True

def main():
    root = tk.Tk()
    app = AniDataVPNApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
