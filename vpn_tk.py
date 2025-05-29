#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AniData VPN - Interface simplifiée avec Tkinter

import os
import sys
import json
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime

# Essayer d'importer matplotlib pour les graphiques
try:
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Classe de gestionnaire VPN simplifiée
class VPNManager:
    def __init__(self):
        self.servers = []
        self.connected = False
    
    def connect(self, server):
        print(f"Connexion à {server['country']} - {server['city']}...")
        self.connected = True
        return True
    
    def disconnect(self):
        print("Déconnexion...")
        self.connected = False
        return True
    
    def get_status(self):
        return {
            'connected': self.connected,
            'uptime': "00:10:30" if self.connected else "00:00:00",
            'statistics': {
                'download_speed': random.uniform(0, 5) if self.connected else 0,
                'upload_speed': random.uniform(0, 1) if self.connected else 0,
                'total_downloaded': random.uniform(0, 500) if self.connected else 0,
                'total_uploaded': random.uniform(0, 100) if self.connected else 0
            }
        }

# Thread de surveillance
class StatusThread(threading.Thread):
    def __init__(self, manager, callback):
        super().__init__()
        self.manager = manager
        self.callback = callback
        self.running = True
        self.daemon = True
    
    def run(self):
        while self.running:
            status = self.manager.get_status()
            self.callback(status)
            time.sleep(1)
    
    def stop(self):
        self.running = False

# Application principale
class VPNApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AniData VPN - 165 Pays")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        
        # Manager VPN
        self.manager = VPNManager()
        self.current_server = None
        self.servers = []
        
        # Créer l'interface
        self.create_ui()
        
        # Charger les données
        self.load_servers()
        
        # Démarrer la surveillance
        self.status_thread = StatusThread(self.manager, self.update_status)
        self.status_thread.start()
    
    def create_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panneaux gauche et droite
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Panneau gauche
        left_panel = ttk.Frame(paned)
        paned.add(left_panel, weight=2)
        
        # Titre
        title_frame = ttk.Frame(left_panel)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame, 
            text="AniData VPN - 165 Pays Disponibles", 
            font=('Helvetica', 14, 'bold'),
            foreground="#3B82F6"
        )
        title_label.pack(side=tk.LEFT)
        
        # Carte
        map_frame = ttk.LabelFrame(left_panel, text="Couverture Mondiale")
        map_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        regions_label = ttk.Label(
            map_frame,
            text="Réseau Mondial Sécurisé: 165 Pays",
            font=('Helvetica', 12, 'bold'),
            foreground="#22C55E"
        )
        regions_label.pack(pady=5)
        
        regions = [
            "• Europe: 40+ pays",
            "• Asie: 45+ pays",
            "• Amériques: 35+ pays",
            "• Afrique: 25+ pays",
            "• Océanie: 10+ pays"
        ]
        
        for region in regions:
            region_label = ttk.Label(map_frame, text=region, font=('Helvetica', 11))
            region_label.pack(anchor=tk.W, padx=20, pady=2)
        
        # Liste des serveurs
        servers_frame = ttk.LabelFrame(left_panel, text="Serveurs")
        servers_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barre de recherche
        search_frame = ttk.Frame(servers_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Recherche:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_servers)
        
        # Tableau des serveurs
        self.servers_tree = ttk.Treeview(
            servers_frame, 
            columns=("country", "city", "protocol"), 
            show="headings"
        )
        self.servers_tree.heading("country", text="Pays")
        self.servers_tree.heading("city", text="Ville")
        self.servers_tree.heading("protocol", text="Protocole")
        
        self.servers_tree.column("country", width=150)
        self.servers_tree.column("city", width=150)
        self.servers_tree.column("protocol", width=100)
        
        self.servers_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barre de défilement
        scrollbar = ttk.Scrollbar(servers_frame, orient=tk.VERTICAL, command=self.servers_tree.yview)
        scrollbar.place(relx=1, rely=0, relheight=1, anchor=tk.NE)
        self.servers_tree.configure(yscrollcommand=scrollbar.set)
        
        # Sélection de serveur
        self.servers_tree.bind("<<TreeviewSelect>>", self.on_server_selected)
        
        # Panneau droit
        right_panel = ttk.Frame(paned)
        paned.add(right_panel, weight=1)
        
        # Statut de connexion
        status_frame = ttk.LabelFrame(right_panel, text="Statut")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Serveur sélectionné
        server_frame = ttk.Frame(status_frame)
        server_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(server_frame, text="Serveur:").pack(side=tk.LEFT, padx=(0, 5))
        self.server_label = ttk.Label(server_frame, text="Aucun sélectionné")
        self.server_label.pack(side=tk.LEFT)
        
        # État de connexion
        connection_frame = ttk.Frame(status_frame)
        connection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(connection_frame, text="État:").pack(side=tk.LEFT, padx=(0, 5))
        self.status_label = ttk.Label(connection_frame, text="Déconnecté")
        self.status_label.pack(side=tk.LEFT)
        
        # Temps de connexion
        uptime_frame = ttk.Frame(status_frame)
        uptime_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(uptime_frame, text="Temps:").pack(side=tk.LEFT, padx=(0, 5))
        self.uptime_label = ttk.Label(uptime_frame, text="00:00:00")
        self.uptime_label.pack(side=tk.LEFT)
        
        # Boutons de connexion
        buttons_frame = ttk.Frame(status_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.connect_btn = ttk.Button(buttons_frame, text="Connecter", command=self.connect)
        self.connect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.connect_btn.state(['disabled'])
        
        self.disconnect_btn = ttk.Button(buttons_frame, text="Déconnecter", command=self.disconnect)
        self.disconnect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.disconnect_btn.state(['disabled'])
        
        # Statistiques
        stats_frame = ttk.LabelFrame(right_panel, text="Statistiques")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Download speed
        dl_frame = ttk.Frame(stats_frame)
        dl_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dl_frame, text="Téléchargement:").pack(side=tk.LEFT, padx=(0, 5))
        self.dl_speed_label = ttk.Label(dl_frame, text="0.00 MB/s")
        self.dl_speed_label.pack(side=tk.LEFT)
        
        # Upload speed
        ul_frame = ttk.Frame(stats_frame)
        ul_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(ul_frame, text="Envoi:").pack(side=tk.LEFT, padx=(0, 5))
        self.ul_speed_label = ttk.Label(ul_frame, text="0.00 MB/s")
        self.ul_speed_label.pack(side=tk.LEFT)
        
        # Total downloaded
        total_dl_frame = ttk.Frame(stats_frame)
        total_dl_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(total_dl_frame, text="Total téléchargé:").pack(side=tk.LEFT, padx=(0, 5))
        self.total_dl_label = ttk.Label(total_dl_frame, text="0.00 MB")
        self.total_dl_label.pack(side=tk.LEFT)
        
        # Total uploaded
        total_ul_frame = ttk.Frame(stats_frame)
        total_ul_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(total_ul_frame, text="Total envoyé:").pack(side=tk.LEFT, padx=(0, 5))
        self.total_ul_label = ttk.Label(total_ul_frame, text="0.00 MB")
        self.total_ul_label.pack(side=tk.LEFT)
        
        # Graphique
        if MATPLOTLIB_AVAILABLE:
            graph_frame = ttk.LabelFrame(right_panel, text="Bande passante")
            graph_frame.pack(fill=tk.BOTH, expand=True)
            
            self.figure = plt.Figure(figsize=(5, 3), dpi=100)
            self.ax = self.figure.add_subplot(111)
            self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            self.download_line, = self.ax.plot([], [], 'g-', label='Download')
            self.upload_line, = self.ax.plot([], [], 'r-', label='Upload')
            self.ax.set_xlabel('Temps (s)')
            self.ax.set_ylabel('Vitesse (MB/s)')
            self.ax.set_title('Utilisation de la bande passante')
            self.ax.legend()
            self.ax.grid(True)
            
            self.ax.set_xlim(0, 60)
            self.ax.set_ylim(0, 5)
            
            self.times = []
            self.download_data = []
            self.upload_data = []
            self.start_time = datetime.now()
        else:
            graph_frame = ttk.LabelFrame(right_panel, text="Bande passante")
            graph_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(
                graph_frame, 
                text="Graphique désactivé\nInstaller matplotlib pour l'activer",
                anchor=tk.CENTER
            ).pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def load_servers(self):
        # Essayer de charger depuis un fichier JSON
        try:
            data_path = os.path.join(os.path.dirname(__file__), "data", "countries.json")
            if os.path.exists(data_path):
                with open(data_path, 'r') as f:
                    self.servers = json.load(f)
                print(f"Chargé {len(self.servers)} serveurs depuis countries.json")
            else:
                self.generate_servers()
        except Exception as e:
            print(f"Erreur lors du chargement des serveurs: {e}")
            self.generate_servers()
        
        # Peupler la liste
        self.populate_servers()
    
    def generate_servers(self):
        # Générer des serveurs pour chaque pays
        countries = [
            {"region": "Europe", "country": "France", "city": "Paris"},
            {"region": "Europe", "country": "Allemagne", "city": "Berlin"},
            {"region": "Europe", "country": "Royaume-Uni", "city": "Londres"},
            {"region": "Europe", "country": "Espagne", "city": "Madrid"},
            {"region": "Europe", "country": "Italie", "city": "Rome"},
            {"region": "Europe", "country": "Suisse", "city": "Zurich"},
            {"region": "Europe", "country": "Belgique", "city": "Bruxelles"},
            {"region": "Europe", "country": "Pays-Bas", "city": "Amsterdam"},
            {"region": "Europe", "country": "Suède", "city": "Stockholm"},
            {"region": "Europe", "country": "Norvège", "city": "Oslo"},
            {"region": "Asie", "country": "Japon", "city": "Tokyo"},
            {"region": "Asie", "country": "Chine", "city": "Hong Kong"},
            {"region": "Asie", "country": "Corée du Sud", "city": "Séoul"},
            {"region": "Asie", "country": "Inde", "city": "Mumbai"},
            {"region": "Asie", "country": "Singapour", "city": "Singapour"},
            {"region": "Asie", "country": "Émirats arabes unis", "city": "Dubaï"},
            {"region": "Asie", "country": "Thaïlande", "city": "Bangkok"},
            {"region": "Asie", "country": "Malaisie", "city": "Kuala Lumpur"},
            {"region": "Asie", "country": "Vietnam", "city": "Hô Chi Minh-Ville"},
            {"region": "Amériques", "country": "États-Unis", "city": "New York"},
            {"region": "Amériques", "country": "États-Unis", "city": "Los Angeles"},
            {"region": "Amériques", "country": "Canada", "city": "Toronto"},
            {"region": "Amériques", "country": "Brésil", "city": "São Paulo"},
            {"region": "Amériques", "country": "Mexique", "city": "Mexico"},
            {"region": "Amériques", "country": "Argentine", "city": "Buenos Aires"},
            {"region": "Amériques", "country": "Chili", "city": "Santiago"},
            {"region": "Amériques", "country": "Colombie", "city": "Bogotá"},
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
            protocols = ["wireguard", "openvpn"] if i % 3 == 0 else ["wireguard"]
            self.servers.append({
                "id": f"srv-{i+1:03d}",
                "region": c["region"],
                "country": c["country"],
                "city": c["city"],
                "protocols": protocols,
                "capabilities": {
                    "vpn": True,
                    "proxy": i % 2 == 0,
                    "tor": i % 5 == 0
                }
            })
    
    def populate_servers(self):
        # Effacer la liste actuelle
        for item in self.servers_tree.get_children():
            self.servers_tree.delete(item)
        
        # Ajouter les serveurs
        for i, server in enumerate(self.servers):
            protocols = ", ".join(server.get("protocols", []))
            self.servers_tree.insert(
                "", tk.END, 
                iid=str(i),
                values=(
                    server.get("country", "Inconnu"),
                    server.get("city", ""),
                    protocols
                )
            )
    
    def filter_servers(self, event=None):
        query = self.search_entry.get().lower()
        
        # Effacer la liste actuelle
        for item in self.servers_tree.get_children():
            self.servers_tree.delete(item)
        
        # Ajouter les serveurs filtrés
        for i, server in enumerate(self.servers):
            if (query in server.get("country", "").lower() or 
                query in server.get("city", "").lower()):
                protocols = ", ".join(server.get("protocols", []))
                self.servers_tree.insert(
                    "", tk.END, 
                    iid=str(i),
                    values=(
                        server.get("country", "Inconnu"),
                        server.get("city", ""),
                        protocols
                    )
                )
    
    def on_server_selected(self, event):
        selection = self.servers_tree.selection()
        if selection:
            index = int(selection[0])
            self.current_server = self.servers[index]
            self.server_label.config(text=f"{self.current_server['country']} - {self.current_server['city']}")
            self.connect_btn.state(['!disabled'])
    
    def connect(self):
        if self.current_server:
            if self.manager.connect(self.current_server):
                self.status_label.config(text="Connecté")
                self.connect_btn.state(['disabled'])
                self.disconnect_btn.state(['!disabled'])
                messagebox.showinfo(
                    "Connecté", 
                    f"Connecté à {self.current_server['country']} - {self.current_server['city']}"
                )
                
                # Réinitialiser les données du graphique
                if MATPLOTLIB_AVAILABLE:
                    self.times = []
                    self.download_data = []
                    self.upload_data = []
                    self.start_time = datetime.now()
    
    def disconnect(self):
        if self.manager.disconnect():
            self.status_label.config(text="Déconnecté")
            self.uptime_label.config(text="00:00:00")
            self.connect_btn.state(['!disabled'])
            self.disconnect_btn.state(['disabled'])
            messagebox.showinfo("Déconnecté", "VPN déconnecté avec succès")
    
    def update_status(self, status):
        # Mettre à jour le statut
        is_connected = status.get('connected', False)
        uptime = status.get('uptime', "00:00:00")
        stats = status.get('statistics', {})
        
        # Mettre à jour l'interface
        if is_connected:
            self.status_label.config(text="Connecté")
            self.uptime_label.config(text=uptime)
            self.connect_btn.state(['disabled'])
            self.disconnect_btn.state(['!disabled'])
        else:
            self.status_label.config(text="Déconnecté")
            self.uptime_label.config(text="00:00:00")
            if self.current_server:
                self.connect_btn.state(['!disabled'])
            self.disconnect_btn.state(['disabled'])
        
        # Mettre à jour les statistiques
        self.dl_speed_label.config(text=f"{stats.get('download_speed', 0):.2f} MB/s")
        self.ul_speed_label.config(text=f"{stats.get('upload_speed', 0):.2f} MB/s")
        self.total_dl_label.config(text=f"{stats.get('total_downloaded', 0):.2f} MB")
        self.total_ul_label.config(text=f"{stats.get('total_uploaded', 0):.2f} MB")
        
        # Mettre à jour le graphique
        if MATPLOTLIB_AVAILABLE and is_connected:
            current_time = (datetime.now() - self.start_time).total_seconds()
            self.times.append(current_time)
            self.download_data.append(stats.get('download_speed', 0))
            self.upload_data.append(stats.get('upload_speed', 0))
            
            # Limiter à 60 secondes
            if self.times and self.times[-1] > 60:
                self.times = [t for t in self.times if t > current_time - 60]
                self.download_data = self.download_data[-len(self.times):]
                self.upload_data = self.upload_data[-len(self.times):]
            
            # Mettre à jour le graphique
            self.download_line.set_data(self.times, self.download_data)
            self.upload_line.set_data(self.times, self.upload_data)
            
            # Ajuster les axes
            if self.times:
                self.ax.set_xlim(max(0, current_time - 60), max(60, current_time))
                max_speed = max(
                    max(self.download_data) if self.download_data else 0,
                    max(self.upload_data) if self.upload_data else 0
                )
                if max_speed > 0:
                    self.ax.set_ylim(0, max_speed * 1.1)
            
            self.canvas.draw()
    
    def on_close(self):
        if hasattr(self, 'status_thread'):
            self.status_thread.stop()
        self.root.destroy()

# Lancer l'application
def main():
    root = tk.Tk()
    app = VPNApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
