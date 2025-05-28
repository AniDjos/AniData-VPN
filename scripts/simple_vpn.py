#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AniData VPN - Ultra Simple UI
# © 2023-2025 AniData - All Rights Reserved

import os
import sys
import json
import time
import random
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font
from PIL import Image, ImageTk, ImageDraw

# Répertoire des configurations
HOME_DIR = os.path.expanduser("~/.anidata")
CONFIG_DIR = os.path.join(HOME_DIR, "config")
SERVERS_FILE = os.path.join(HOME_DIR, "servers/expanded_config.json")
EXTENDED_SERVERS = True  # Flag indiquant que nous utilisons la configuration étendue

# Assurez-vous que les répertoires existent
os.makedirs(os.path.join(HOME_DIR, "config"), exist_ok=True)
os.makedirs(os.path.join(HOME_DIR, "servers"), exist_ok=True)

# Vérifier si le fichier de configuration des serveurs existe
def check_server_config():
    if not os.path.exists(SERVERS_FILE):
        # Essayer de le copier depuis le répertoire du projet
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # Chercher d'abord la configuration étendue
            src_file = os.path.join(project_root, "infrastructure/servers/expanded_config.json")
            if not os.path.exists(src_file):
                src_file = os.path.join(project_root, "infrastructure/servers/config_expanded.json")
            if not os.path.exists(src_file):
                src_file = os.path.join(project_root, "infrastructure/servers/config.json")
            
            if os.path.exists(src_file):
                import shutil
                print(f"Utilisation du fichier de configuration: {src_file}")
                shutil.copy2(src_file, SERVERS_FILE)
            else:
                # Créer une configuration minimale
                servers = {
                    "servers": [
                        {
                            "id": "fr-01",
                            "region": "Europe",
                            "country": "France",
                            "city": "Paris",
                            "ip": "178.32.53.94",
                            "protocols": ["wireguard", "openvpn"],
                            "status": "active"
                        },
                        {
                            "id": "us-01",
                            "region": "North America",
                            "country": "United States",
                            "city": "New York",
                            "ip": "104.156.231.229",
                            "protocols": ["wireguard", "openvpn"],
                            "status": "active"
                        },
                        {
                            "id": "jp-01",
                            "region": "Asia",
                            "country": "Japan",
                            "city": "Tokyo",
                            "ip": "103.122.102.76",
                            "protocols": ["wireguard", "openvpn"],
                            "status": "active"
                        }
                    ]
                }
                with open(SERVERS_FILE, 'w') as f:
                    json.dump(servers, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la création du fichier de configuration des serveurs: {e}")

# Charger les serveurs depuis le fichier de configuration
def load_servers():
    try:
        if os.path.exists(SERVERS_FILE):
            with open(SERVERS_FILE, 'r') as f:
                data = json.load(f)
                return data.get("servers", [])
        return []
    except Exception as e:
        print(f"Erreur lors du chargement des serveurs: {e}")
        return []

# Vérifier si WireGuard est installé
def check_wireguard():
    try:
        result = subprocess.run(["which", "wg"], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

# Simuler une connexion VPN (pour démonstration)
def simulate_vpn_connection(server):
    # En réalité, cette fonction appellerait le module WireGuard
    print(f"Connexion simulée au serveur {server['country']}, {server['city']}...")
    time.sleep(2)  # Simuler un délai de connexion
    return True

# Simuler une déconnexion VPN (pour démonstration)
def simulate_vpn_disconnection():
    print("Déconnexion simulée...")
    time.sleep(1)
    return True

# Classe principale de l'application
class SimpleVPNApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AniData VPN - Édition 163 Pays")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Définir l'icône de l'application si disponible
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "..", "ui", "assets", "icon.png")
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
        except Exception as e:
            print(f"Impossible de charger l'icône: {e}")
        
        # Définir les couleurs du thème Bleu Azur (#007FFF)
        self.colors = {
            "primary": "#007FFF",       # Bleu Azur - couleur principale
            "secondary": "#4DA6FF",     # Bleu Azur plus clair
            "accent": "#99CCFF",        # Bleu Azur très clair
            "light_accent": "#E6F2FF",  # Bleu Azur pâle
            "white": "#FFFFFF",         # Blanc pur
            "text_dark": "#003366",     # Bleu foncé (pour le texte foncé)
            "text_light": "#FFFFFF",    # Blanc (pour le texte clair)
            "success": "#00CC66",       # Vert (pour le succès)
            "warning": "#FFCC00",       # Jaune (pour avertissement)
            "error": "#FF3333",         # Rouge (pour l'erreur)
            "background": "#007FFF",    # Bleu Azur - couleur de fond principale
        }
        
        # Créer et appliquer l'image de fond
        self.create_background()
        
        # Appliquer le thème à la fenêtre principale
        # Note: Le fond est maintenant géré par le canvas avec l'image de dégradé
        
        # Créer un style personnalisé
        self.style = ttk.Style()
        self.style.configure("TFrame", background=self.colors["white"])
        self.style.configure("TLabel", background=self.colors["white"], foreground=self.colors["text_dark"])
        self.style.configure("TButton", background=self.colors["primary"], foreground=self.colors["text_light"])
        self.style.configure("TCheckbutton", background=self.colors["white"])
        
        # Style pour les headers du Treeview
        self.style.configure("Treeview.Heading", background=self.colors["primary"], foreground=self.colors["text_light"], font=('Helvetica', 10, 'bold'))
        self.style.configure("Treeview", background=self.colors["white"], fieldbackground=self.colors["white"])
        self.style.map("Treeview", background=[('selected', self.colors["secondary"])], foreground=[('selected', self.colors["text_light"])])
        
        # Style pour les LabelFrame
        self.style.configure("TLabelframe", background=self.colors["white"])
        self.style.configure("TLabelframe.Label", background=self.colors["primary"], foreground=self.colors["text_light"], font=('Helvetica', 10, 'bold'))
        self.style.map("TLabelframe.Label", background=[('', self.colors["primary"])])
        
        # Style pour les widgets sur fond transparent ou bleu azur
        self.style.configure("Transparent.TFrame", background='')
        self.style.configure("Transparent.TLabel", background='', foreground=self.colors["text_light"])
        
        # Styles spécifiques pour fond Bleu Azur
        self.style.configure("BlueAzure.TFrame", background=self.colors["primary"])
        self.style.configure("BlueAzure.TLabel", background=self.colors["primary"], foreground=self.colors["text_light"])
        self.style.configure("BlueAzure.TButton", background=self.colors["secondary"], foreground=self.colors["text_light"])
        
        # État de la connexion
        self.connected = False
        self.selected_server = None
        self.connection_time = None
        
        # Création de l'interface
        self.create_ui()
        
        # Charger les serveurs
        self.load_server_list()
        
        # Vérifier WireGuard
        if not check_wireguard():
            messagebox.showwarning(
                "WireGuard non installé", 
                "WireGuard n'est pas installé sur votre système.\n\n"
                "Pour une fonctionnalité complète, installez-le avec:\n"
                "sudo apt-get install wireguard-tools\n\n"
                "L'application fonctionnera en mode simulation."
            )
    
    def create_background(self):
        """Crée un fond Bleu Azur uniforme avec des éléments décoratifs pour l'application"""
        # Obtenir les dimensions de la fenêtre
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        
        # Créer une image avec la couleur Bleu Azur uniforme
        # Convertir la couleur hexadécimale en RGB
        main_color = (0, 127, 255)  # Bleu Azur (#007FFF)
        image = Image.new('RGBA', (width, height), color=(*main_color, 255))
        draw = ImageDraw.Draw(image)
        
        # Définir des couleurs variantes pour les éléments décoratifs
        colors = [
            (0, 127, 255),    # Bleu Azur (#007FFF) - couleur principale
            (51, 153, 255),   # Bleu Azur légèrement plus clair
            (77, 166, 255),   # Bleu Azur clair
            (153, 204, 255)   # Bleu Azur très clair
        ]
        
        # Ajouter des éléments graphiques pour donner de la profondeur
        # Cercles décoratifs avec différentes teintes de bleu azur
        for i in range(20):
            x = random.randint(-100, width)
            y = random.randint(-100, height)
            size = random.randint(80, 300)
            opacity = random.randint(20, 60)  # Plus transparent pour un effet subtil
            r, g, b = colors[random.randint(0, len(colors)-1)]
            draw.ellipse((x, y, x+size, y+size), fill=(r, g, b, opacity))
        
        # Ajouter quelques lignes horizontales décoratives pour la structure
        for i in range(10):
            y_pos = random.randint(0, height)
            line_width = random.randint(50, width//2)
            x_start = random.randint(0, width-line_width)
            opacity = random.randint(30, 70)
            draw.line([(x_start, y_pos), (x_start+line_width, y_pos)], 
                     fill=(255, 255, 255, opacity), width=2)
        
        # Convertir en PhotoImage pour Tkinter
        self.bg_image = ImageTk.PhotoImage(image)
        
        # Créer un canvas comme conteneur principal
        self.canvas = tk.Canvas(self.root, width=width, height=height, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Ajouter l'image au canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
        
        # Créer un frame principal transparent pour contenir les widgets
        self.main_container = ttk.Frame(self.canvas, style="Transparent.TFrame")
        self.canvas.create_window(width//2, height//2, window=self.main_container, anchor=tk.CENTER, width=width-40, height=height-40)

    def create_ui(self):
        # Créer une police personnalisée pour les titres
        title_font = font.Font(family="Helvetica", size=12, weight="bold")
        
        # Créer un cadre principal avec un titre
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Logo (texte stylisé)
        logo_label = tk.Label(header_frame, text="AniData VPN", 
                             font=("Helvetica", 18, "bold"), 
                             fg=self.colors["white"], 
                             bg=self.colors["primary"],
                             padx=10, pady=5,
                             relief=tk.RAISED,
                             borderwidth=2)
        logo_label.pack(side=tk.LEFT, padx=5)
        
        # Frame principale avec un séparateur
        main_frame = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Frame gauche - Liste des serveurs
        left_frame = ttk.Frame(main_frame)
        main_frame.add(left_frame, weight=1)
        
        # Titre de la liste des serveurs
        server_title_frame = ttk.Frame(left_frame)
        server_title_frame.pack(fill=tk.X, pady=5)
        server_title = tk.Label(server_title_frame, 
                              text="Serveurs disponibles", 
                              font=title_font, 
                              fg=self.colors["text_light"],
                              bg=self.colors["primary"],
                              padx=10, pady=5,
                              relief=tk.RAISED)
        server_title.pack(fill=tk.X)
        
        # Liste des serveurs
        self.server_list = ttk.Treeview(left_frame, columns=("country", "city", "status"), show="headings")
        self.server_list.heading("country", text="Pays")
        self.server_list.heading("city", text="Ville")
        self.server_list.heading("status", text="Statut")
        self.server_list.column("country", width=100)
        self.server_list.column("city", width=100)
        self.server_list.column("status", width=70)
        
        # Scrollbar pour la liste des serveurs
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.server_list.yview)
        self.server_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.server_list.pack(fill=tk.BOTH, expand=True, pady=5)
        self.server_list.bind("<<TreeviewSelect>>", self.on_server_select)
        
        # Frame droite - Contrôles de connexion
        right_frame = ttk.Frame(main_frame)
        main_frame.add(right_frame, weight=2)
        
        # Frame de statut
        status_frame = ttk.LabelFrame(right_frame, text="Statut de connexion")
        status_frame.pack(fill=tk.BOTH, expand=False, pady=10)
        
        # Informations de connexion
        info_frame = ttk.Frame(status_frame)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Styliser les labels d'information
        label_style = {"width": 15, "anchor": "w"}
        value_style = {"width": 25, "anchor": "w"}
        
        ttk.Label(info_frame, text="Statut:", **label_style).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.status_label = tk.Label(info_frame, text="Déconnecté", 
                                   fg=self.colors["error"], 
                                   bg=self.colors["white"],
                                   font=("Helvetica", 10, "bold"),
                                   **value_style)
        self.status_label.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(info_frame, text="Serveur:", **label_style).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.server_label = tk.Label(info_frame, text="Aucun", 
                                   fg=self.colors["text_dark"], 
                                   bg=self.colors["white"],
                                   **value_style)
        self.server_label.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(info_frame, text="IP:", **label_style).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.ip_label = tk.Label(info_frame, text="Non connecté", 
                               fg=self.colors["text_dark"], 
                               bg=self.colors["white"],
                               **value_style)
        self.ip_label.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(info_frame, text="Temps de connexion:", **label_style).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.uptime_label = tk.Label(info_frame, text="00:00:00", 
                                   fg=self.colors["text_dark"], 
                                   bg=self.colors["white"],
                                   **value_style)
        self.uptime_label.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Frame de contrôle
        control_frame = ttk.LabelFrame(right_frame, text="Contrôles")
        control_frame.pack(fill=tk.BOTH, expand=False, pady=10)
        
        # Protocole
        protocol_frame = ttk.Frame(control_frame)
        protocol_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(protocol_frame, text="Protocole:", width=15, anchor="w").pack(side=tk.LEFT, padx=5)
        self.protocol_var = tk.StringVar(value="WireGuard")
        protocol_combo = ttk.Combobox(protocol_frame, textvariable=self.protocol_var, state="readonly", width=20)
        protocol_combo["values"] = ("WireGuard", "OpenVPN", "IKEv2")
        protocol_combo.pack(side=tk.LEFT, padx=5)
        
        # Boutons de connexion
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Bouton Connecter stylisé
        self.connect_button = tk.Button(
            button_frame, 
            text="Connecter", 
            command=self.connect,
            bg=self.colors["primary"],
            fg=self.colors["text_light"],
            activebackground=self.colors["secondary"],
            activeforeground=self.colors["text_light"],
            font=("Helvetica", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=5,
            cursor="hand2"
        )
        self.connect_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Bouton Déconnecter stylisé
        self.disconnect_button = tk.Button(
            button_frame, 
            text="Déconnecter", 
            command=self.disconnect,
            bg=self.colors["accent"],
            fg=self.colors["text_dark"],
            activebackground=self.colors["secondary"],
            activeforeground=self.colors["text_light"],
            font=("Helvetica", 10, "bold"),
            relief=tk.RAISED,
            borderwidth=2,
            state=tk.DISABLED,
            padx=10,
            pady=5,
            cursor="hand2"
        )
        self.disconnect_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Options de sécurité
        security_frame = ttk.LabelFrame(right_frame, text="Options de sécurité")
        security_frame.pack(fill=tk.BOTH, expand=False, pady=10)
        
        # Styliser les checkbuttons
        self.kill_switch_var = tk.BooleanVar(value=True)
        kill_switch_check = tk.Checkbutton(
            security_frame, 
            text="Kill Switch", 
            variable=self.kill_switch_var,
            bg=self.colors["white"],
            fg=self.colors["text_dark"],
            activebackground=self.colors["light_accent"],
            activeforeground=self.colors["text_dark"],
            selectcolor=self.colors["accent"]
        )
        kill_switch_check.pack(anchor=tk.W, padx=10, pady=5)
        
        self.dns_leak_var = tk.BooleanVar(value=True)
        dns_leak_check = tk.Checkbutton(
            security_frame, 
            text="Protection contre les fuites DNS", 
            variable=self.dns_leak_var,
            bg=self.colors["white"],
            fg=self.colors["text_dark"],
            activebackground=self.colors["light_accent"],
            activeforeground=self.colors["text_dark"],
            selectcolor=self.colors["accent"]
        )
        dns_leak_check.pack(anchor=tk.W, padx=10, pady=5)
        
        # Frame de statistiques
        stats_frame = ttk.LabelFrame(right_frame, text="Statistiques")
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        stats_inner_frame = ttk.Frame(stats_frame)
        stats_inner_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Styliser les labels de statistiques
        ttk.Label(stats_inner_frame, text="Téléchargement:", width=15, anchor="w").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.download_label = tk.Label(
            stats_inner_frame, 
            text="0 KB/s", 
            fg=self.colors["text_dark"], 
            bg=self.colors["white"],
            width=15,
            anchor="w"
        )
        self.download_label.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(stats_inner_frame, text="Envoi:", width=15, anchor="w").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.upload_label = tk.Label(
            stats_inner_frame, 
            text="0 KB/s", 
            fg=self.colors["text_dark"], 
            bg=self.colors["white"],
            width=15,
            anchor="w"
        )
        self.upload_label.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(stats_inner_frame, text="Latence:", width=15, anchor="w").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.latency_label = tk.Label(
            stats_inner_frame, 
            text="0 ms", 
            fg=self.colors["text_dark"], 
            bg=self.colors["white"],
            width=15,
            anchor="w"
        )
        self.latency_label.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Ajouter un pied de page
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        footer_label = tk.Label(
            footer_frame, 
            text="© 2023-2025 AniData - Tous droits réservés", 
            fg=self.colors["primary"],
            bg=self.colors["white"],
            font=("Helvetica", 8)
        )
        footer_label.pack(side=tk.RIGHT)
        
        # Démarrer la mise à jour périodique
        self.update_uptime()
    
    def load_server_list(self):
        # Effacer la liste actuelle
        for item in self.server_list.get_children():
            self.server_list.delete(item)
        
        # Charger les serveurs
        servers = load_servers()
        
        # Ajouter les serveurs à la liste
        for server in servers:
            # Déterminer la région pour le style
            region = server.get("region", "").lower()
            tag = "default"
            
            if "europe" in region:
                tag = "europe"
            elif "north america" in region:
                tag = "namerica"
            elif "asia" in region:
                tag = "asia"
            elif "south america" in region:
                tag = "samerica"
            elif "africa" in region:
                tag = "africa"
            elif "oceania" in region:
                tag = "oceania"
            
            # Insérer le serveur avec son tag de région
            self.server_list.insert("", tk.END, iid=server["id"], values=(
                server.get("country", "Unknown"),
                server.get("city", "Unknown"),
                server.get("status", "active")
            ), tags=[json.dumps(server), tag])
            
        # Configurer les tags pour les couleurs par région (nuances de Bleu Azur)
        self.server_list.tag_configure("europe", background=self.colors["light_accent"])
        self.server_list.tag_configure("namerica", background="#CCE0FF")  # Bleu Azur très pâle
        self.server_list.tag_configure("asia", background="#99CCFF")      # Bleu Azur très clair
        self.server_list.tag_configure("samerica", background="#66B2FF")  # Bleu Azur clair
        self.server_list.tag_configure("africa", background="#4DA6FF")    # Bleu Azur moyen
        self.server_list.tag_configure("oceania", background="#3399FF")   # Bleu Azur soutenu
    
    def on_server_select(self, event):
        selection = self.server_list.selection()
        if selection:
            item_id = selection[0]
            tags = self.server_list.item(item_id, "tags")
            if tags:
                self.selected_server = json.loads(tags[0])
                self.server_label.config(text=f"{self.selected_server['country']}, {self.selected_server['city']}")
    
    def connect(self):
        if not self.selected_server:
            messagebox.showwarning("Aucun serveur sélectionné", "Veuillez sélectionner un serveur avant de vous connecter.")
            return
            
        # Afficher un message de connexion
        self.status_label.config(text="Connexion en cours...", fg=self.colors["secondary"])
        self.root.update()
        
        # Vérifier WireGuard si protocole WireGuard sélectionné
        if self.protocol_var.get() == "WireGuard" and not check_wireguard():
            response = messagebox.askquestion(
                "WireGuard non installé", 
                "WireGuard n'est pas installé. Voulez-vous l'installer maintenant?\n\n"
                "(Nécessite des droits administrateur)",
                icon='warning'
            )
            if response == 'yes':
                try:
                    if sys.platform == "linux":
                        subprocess.run(["pkexec", "apt-get", "install", "-y", "wireguard-tools"], check=True)
                    else:
                        messagebox.showinfo("Installation manuelle requise", 
                                         "Veuillez installer WireGuard manuellement pour votre système d'exploitation.")
                except Exception as e:
                    messagebox.showerror("Erreur d'installation", f"Erreur lors de l'installation de WireGuard: {e}")
                    return
            else:
                # Continuer en mode simulation
                pass
        
        # Simuler une connexion
        success = simulate_vpn_connection(self.selected_server)
        
        if success:
            self.connected = True
            self.connection_time = time.time()
            
            # Mettre à jour l'interface
            self.status_label.config(text="Connecté", fg=self.colors["text_dark"])
            self.ip_label.config(text=f"{self.selected_server['ip']} (VPN)")
            
            # Mettre à jour les boutons
            self.connect_button.config(state=tk.DISABLED, bg=self.colors["accent"])
            self.disconnect_button.config(state=tk.NORMAL, bg=self.colors["primary"])
            
            # Démarrer les mises à jour des statistiques
            self.update_statistics()
    
    def disconnect(self):
        if not self.connected:
            return
        
        # Simuler une déconnexion
        success = simulate_vpn_disconnection()
        
        if success:
            self.connected = False
            self.connection_time = None
            
            # Mettre à jour l'interface
            self.status_label.config(text="Déconnecté", fg=self.colors["text_dark"])
            self.ip_label.config(text="Non connecté")
            
            # Mettre à jour les boutons
            self.connect_button.config(state=tk.NORMAL, bg=self.colors["primary"])
            self.disconnect_button.config(state=tk.DISABLED, bg=self.colors["secondary"])
            
            # Réinitialiser les statistiques
            self.download_label.config(text="0 KB/s")
            self.upload_label.config(text="0 KB/s")
            self.latency_label.config(text="0 ms")
            self.uptime_label.config(text="00:00:00")
    
    def update_uptime(self):
        if self.connected and self.connection_time:
            elapsed = int(time.time() - self.connection_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            self.uptime_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Programmer la prochaine mise à jour
        self.root.after(1000, self.update_uptime)
    
    def update_statistics(self):
        if self.connected:
            # Simuler des statistiques aléatoires
            download = random.randint(50, 2000)
            upload = random.randint(20, 500)
            latency = random.randint(5, 200)
            
            self.download_label.config(text=f"{download} KB/s")
            self.upload_label.config(text=f"{upload} KB/s")
            self.latency_label.config(text=f"{latency} ms")
            
            # Programmer la prochaine mise à jour
            self.root.after(2000, self.update_statistics)

# Point d'entrée principal
if __name__ == "__main__":
    # Vérifier la configuration
    check_server_config()
    
    # Créer et lancer l'application
    root = tk.Tk()
    app = SimpleVPNApp(root)
    root.mainloop()