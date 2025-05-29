#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AniData VPN - Tkinter UI
# © 2023-2024 AniData - All Rights Reserved

import os
import sys
import json
import random
import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime, timedelta
import webbrowser
import tempfile
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Ensure the project root is in Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Define color scheme
COLORS = {
    'primary': '#3B82F6',  # Blue
    'success': '#22C55E',  # Green
    'danger': '#EF4444',   # Red
    'warning': '#F59E0B',  # Amber
    'background': '#F9FAFB',  # Light gray
    'text': '#1F2937',     # Dark gray
    'light': '#F3F4F6',    # Very light gray
    'dark': '#374151',     # Medium gray
}

# Try to import core modules
try:
    from core.protocols.wireguard.wireguard import WireGuardManager
    core_available = True
except ImportError:
    core_available = False
    
class WireGuardManager:
    """Fallback class if core module is not available"""
    def __init__(self, **kwargs):
        self.servers = []
        
    def connect(self, config):
        # Simulate connection
        print(f"Connecting to {config.get('server', {}).get('country', 'Unknown')}")
        return True
        
    def disconnect(self):
        # Simulate disconnection
        print("Disconnecting...")
        return True
        
    def get_status(self):
        # Return dummy status
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
                print(f"Error getting status: {str(e)}")
            
            # Sleep for 3 seconds
            time.sleep(3)
    
    def stop(self):
        self.running = False

class BandwidthGraph:
    """Graph for displaying bandwidth usage"""
    def __init__(self, parent):
        self.parent = parent
        self.times = np.array([])
        self.download_data = np.array([])
        self.upload_data = np.array([])
        self.start_time = datetime.now()
        self.time_window = 60  # 60 seconds of data
        
        # Create matplotlib figure
        self.figure = plt.Figure(figsize=(5, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Setup plot
        self.download_line, = self.ax.plot([], [], 'g-', label='Download')
        self.upload_line, = self.ax.plot([], [], 'r-', label='Upload')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Speed (MB/s)')
        self.ax.set_title('Bandwidth')
        self.ax.legend()
        self.ax.grid(True)
        
        # Initial plot setup
        self.ax.set_xlim(0, self.time_window)
        self.ax.set_ylim(0, 1)
        
    def update_bandwidth(self, download_speed, upload_speed):
        current_time = (datetime.now() - self.start_time).total_seconds()
        
        # Append new data
        self.times = np.append(self.times, current_time)
        self.download_data = np.append(self.download_data, download_speed)
        self.upload_data = np.append(self.upload_data, upload_speed)
        
        # Remove old data outside the time window
        mask = self.times > current_time - self.time_window
        self.times = self.times[mask]
        self.download_data = self.download_data[mask]
        self.upload_data = self.upload_data[mask]
        
        # Update plot
        self.download_line.set_data(self.times, self.download_data)
        self.upload_line.set_data(self.times, self.upload_data)
        
        # Auto-scale Y axis if needed
        max_value = max(np.max(self.download_data) if len(self.download_data) > 0 else 0,
                      np.max(self.upload_data) if len(self.upload_data) > 0 else 0)
        if max_value > 0:
            self.ax.set_ylim(0, max_value * 1.1)
            
        # Set X axis range to show the time window
        self.ax.set_xlim(max(0, current_time - self.time_window), max(self.time_window, current_time))
        
        # Redraw canvas
        self.canvas.draw()
    
    def reset(self):
        self.times = np.array([])
        self.download_data = np.array([])
        self.upload_data = np.array([])
        self.start_time = datetime.now()
        self.download_line.set_data([], [])
        self.upload_line.set_data([], [])
        self.canvas.draw()

class MapFrame(ttk.Frame):
    """Frame for displaying map"""
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.parent = parent
        
        # Create a header for the map
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        server_count_label = ttk.Label(header_frame, text="AniData VPN - 165 Pays Disponibles", font=('Helvetica', 14, 'bold'), foreground="#3B82F6")
        server_count_label.pack(side=tk.LEFT)
        
        # Create a label for map (placeholder)
        self.map_label = ttk.Label(self, text="Carte de Couverture Mondiale")
        self.map_label.pack(fill=tk.X)
        
        # Add a frame for map when available
        self.map_frame = ttk.Frame(self)
        self.map_frame.pack(fill=tk.BOTH, expand=True)
        
        # Display static map info
        self.display_static_map()
        
        # Add server count display
        count_frame = ttk.Frame(self)
        count_frame.pack(fill=tk.X, pady=5)
        self.server_count = ttk.Label(count_frame, 
                                      text="Chargement des serveurs...", 
                                      font=('Helvetica', 10, 'italic'))
        self.server_count.pack(side=tk.RIGHT)
        
    def display_static_map(self):
        """Display a static world map"""
        regions_frame = ttk.Frame(self.map_frame)
        regions_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add total count text
        total_label = ttk.Label(regions_frame, 
                               text="Réseau Mondial Sécurisé: 165 Pays", 
                               font=('Helvetica', 12, 'bold'),
                               foreground="#22C55E")
        total_label.pack(pady=(0, 10))
        
        # Create a grid to display region coverage
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

class ServerListFrame(ttk.Frame):
    """Frame for displaying server list"""
    def __init__(self, parent, on_select_callback):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.on_select_callback = on_select_callback
        
        # Create header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Servers", font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT)
        
        # Create search entry
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_servers)
        
        # Create treeview for servers
        self.tree = ttk.Treeview(self, columns=("country", "city", "protocols"), show="headings")
        self.tree.heading("country", text="Country")
        self.tree.heading("city", text="City")
        self.tree.heading("protocols", text="Protocols")
        self.tree.column("country", width=100)
        self.tree.column("city", width=100)
        self.tree.column("protocols", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_server_selected)
        
        # Store servers data
        self.servers = []
        
    def populate_servers(self, servers):
        """Populate server list"""
        self.servers = servers
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add servers to treeview
        for i, server in enumerate(servers):
            protocols = ", ".join(server.get("protocols", []))
            self.tree.insert("", tk.END, iid=str(i), values=(
                server.get("country", "Unknown"), 
                server.get("city", ""), 
                protocols
            ))
            
        # Update the server count in the map frame if it exists
        if hasattr(self.parent, "map_frame") and hasattr(self.parent.map_frame, "server_count"):
            self.parent.map_frame.server_count.config(
                text=f"Total serveurs: {len(servers)} dans {len(set(s.get('country', '') for s in servers))} pays")
            
    def filter_servers(self, event=None):
        """Filter servers based on search query"""
        query = self.search_entry.get().lower()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add filtered servers
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
        """Handle server selection"""
        selection = self.tree.selection()
        if selection:
            index = int(selection[0])
            server = self.servers[index]
            self.on_select_callback(server)

class ConnectionFrame(ttk.Frame):
    """Frame for connection controls"""
    def __init__(self, parent, on_connect, on_disconnect):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        
        # Status variables
        self.is_connected = False
        self.selected_server = None
        
        # Create server info frame
        server_frame = ttk.Frame(self)
        server_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(server_frame, text="Selected Server:").pack(side=tk.LEFT, padx=(0, 5))
        self.server_info = ttk.Label(server_frame, text="None selected")
        self.server_info.pack(side=tk.LEFT)
        
        # Create status frame
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, padx=(0, 5))
        self.status_label = ttk.Label(status_frame, text="Disconnected")
        self.status_label.pack(side=tk.LEFT)
        
        # Create uptime frame
        uptime_frame = ttk.Frame(self)
        uptime_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(uptime_frame, text="Uptime:").pack(side=tk.LEFT, padx=(0, 5))
        self.uptime_label = ttk.Label(uptime_frame, text="00:00:00")
        self.uptime_label.pack(side=tk.LEFT)
        
        # Create button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.connect_btn = ttk.Button(button_frame, text="Connect", command=self.connect_clicked)
        self.connect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.connect_btn.state(['disabled'])
        
        self.disconnect_btn = ttk.Button(button_frame, text="Disconnect", command=self.disconnect_clicked)
        self.disconnect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.disconnect_btn.state(['disabled'])
        
    def set_selected_server(self, server):
        """Set the selected server"""
        self.selected_server = server
        self.server_info.config(text=f"{server.get('country', 'Unknown')} - {server.get('city', '')}")
        self.connect_btn.state(['!disabled'])
        
    def connect_clicked(self):
        """Handle connect button click"""
        if self.selected_server:
            self.on_connect(self.selected_server)
            
    def disconnect_clicked(self):
        """Handle disconnect button click"""
        self.on_disconnect()
        
    def update_status(self, is_connected, server, uptime):
        """Update connection status"""
        self.is_connected = is_connected
        
        if is_connected:
            self.status_label.config(text="Connected")
            self.uptime_label.config(text=uptime)
            self.connect_btn.state(['disabled'])
            self.disconnect_btn.state(['!disabled'])
            
            if server:
                self.server_info.config(text=f"{server.get('country', 'Unknown')} - {server.get('city', '')}")
        else:
            self.status_label.config(text="Disconnected")
            self.uptime_label.config(text="00:00:00")
            if self.selected_server:
                self.connect_btn.state(['!disabled'])
            self.disconnect_btn.state(['disabled'])

class StatisticsFrame(ttk.Frame):
    """Frame for displaying connection statistics"""
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.parent = parent
        
        # Create header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Statistics", font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT)
        
        # Create grid for statistics
        self.grid_frame = ttk.Frame(self)
        self.grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # Download speed
        ttk.Label(self.grid_frame, text="Download Speed:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.download_speed = ttk.Label(self.grid_frame, text="0.00 MB/s")
        self.download_speed.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Upload speed
        ttk.Label(self.grid_frame, text="Upload Speed:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.upload_speed = ttk.Label(self.grid_frame, text="0.00 MB/s")
        self.upload_speed.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Total downloaded
        ttk.Label(self.grid_frame, text="Total Downloaded:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.total_downloaded = ttk.Label(self.grid_frame, text="0.00 MB")
        self.total_downloaded.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Total uploaded
        ttk.Label(self.grid_frame, text="Total Uploaded:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.total_uploaded = ttk.Label(self.grid_frame, text="0.00 MB")
        self.total_uploaded.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
    def update_statistics(self, download_speed, upload_speed, total_downloaded, total_uploaded):
        """Update statistics"""
        self.download_speed.config(text=download_speed)
        self.upload_speed.config(text=upload_speed)
        self.total_downloaded.config(text=total_downloaded)
        self.total_uploaded.config(text=total_uploaded)

class SettingsFrame(ttk.Frame):
    """Frame for settings"""
    def __init__(self, parent, on_settings_changed):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.on_settings_changed = on_settings_changed
        
        # Create header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Settings", font=('Helvetica', 14, 'bold')).pack(side=tk.LEFT)
        
        # Create notebook for settings categories
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # General settings
        general_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(general_frame, text="General")
        
        # Theme selector
        theme_frame = ttk.Frame(general_frame)
        theme_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=(0, 5))
        self.theme_var = tk.StringVar(value="Light")
        self.theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=["Light", "Dark"])
        self.theme_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.theme_combo.bind("<<ComboboxSelected>>", self.save_settings)
        
        # Auto-connect
        auto_connect_frame = ttk.Frame(general_frame)
        auto_connect_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.auto_connect_var = tk.BooleanVar(value=False)
        self.auto_connect_check = ttk.Checkbutton(auto_connect_frame, text="Auto-connect on startup", 
                                              variable=self.auto_connect_var, command=self.save_settings)
        self.auto_connect_check.pack(side=tk.LEFT)
        
        # Network settings
        network_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(network_frame, text="Network")
        
        # Leak protection
        leak_frame = ttk.Frame(network_frame)
        leak_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(leak_frame, text="Leak Protection").pack(anchor=tk.W)
        
        self.dns_leak_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(leak_frame, text="DNS Leak Protection", 
                     variable=self.dns_leak_var, command=self.save_settings).pack(anchor=tk.W, padx=(20, 0))
        
        self.ip_leak_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(leak_frame, text="IP Leak Protection", 
                     variable=self.ip_leak_var, command=self.save_settings).pack(anchor=tk.W, padx=(20, 0))
        
        self.killswitch_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(leak_frame, text="Kill Switch", 
                     variable=self.killswitch_var, command=self.save_settings).pack(anchor=tk.W, padx=(20, 0))
        
        # Protocol settings
        protocol_frame = ttk.Frame(network_frame)
        protocol_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(protocol_frame, text="Default Protocol:").pack(side=tk.LEFT, padx=(0, 5))
        self.protocol_var = tk.StringVar(value="WireGuard")
        self.protocol_combo = ttk.Combobox(protocol_frame, textvariable=self.protocol_var, 
                                       values=["WireGuard", "OpenVPN", "IKEv2"])
        self.protocol_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.protocol_combo.bind("<<ComboboxSelected>>", self.save_settings)
        
        # Save button
        save_frame = ttk.Frame(self)
        save_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.save_btn = ttk.Button(save_frame, text="Save Settings", command=self.save_settings)
        self.save_btn.pack(side=tk.RIGHT)
        
    def save_settings(self, event=None):
        """Save settings"""
        settings = {
            'theme': self.theme_var.get().lower(),
            'auto_connect': self.auto_connect_var.get(),
            'leak_protection': {
                'dns': self.dns_leak_var.get(),
                'ip': self.ip_leak_var.get(),
                'killswitch': self.killswitch_var.get()
            },
            'protocol': self.protocol_var.get().lower()
        }
        
        self.on_settings_changed(settings)

class AniDataVPNApp:
    """Main application class"""
    def __init__(self, root):
        self.root = root
        self.root.title("AniData VPN - 165 Pays")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        
        # Initialize VPN manager
        if core_available:
            home_dir = os.path.expanduser("~/.anidata")
            config_dir = os.path.join(home_dir, "config/wireguard")
            servers_file = os.path.join(home_dir, "servers/config.json")
            self.vpn_manager = WireGuardManager(config_dir=config_dir, servers_file=servers_file)
        else:
            self.vpn_manager = WireGuardManager()
            
        # Setup variables
        self.current_server = None
        self.servers = []
        self.protocol = "wireguard"
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create paned window for left and right panels
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Create left and right frames
        self.left_frame = ttk.Frame(self.paned_window)
        self.right_frame = ttk.Frame(self.paned_window)
        
        # Add frames to paned window
        self.paned_window.add(self.left_frame, weight=2)
        self.paned_window.add(self.right_frame, weight=1)
        
        # Create map frame
        self.map_frame = MapFrame(self.left_frame)
        self.map_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create server list frame
        self.server_list = ServerListFrame(self.left_frame, self.on_server_selected)
        self.server_list.pack(fill=tk.BOTH, expand=True)
        
        # Create connection frame
        self.connection_widget = ConnectionFrame(self.right_frame, self.connect_vpn, self.disconnect_vpn)
        self.connection_widget.pack(fill=tk.X, pady=(0, 10))
        
        # Create statistics frame
        self.stats_widget = StatisticsFrame(self.right_frame)
        self.stats_widget.pack(fill=tk.X, pady=(0, 10))
        
        # Create bandwidth graph
        graph_frame = ttk.LabelFrame(self.right_frame, text="Bandwidth")
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.bandwidth_graph = BandwidthGraph(graph_frame)
        
        # Create settings frame
        self.settings_widget = SettingsFrame(self.right_frame, self.save_settings)
        self.settings_widget.pack(fill=tk.X)
        
        # Load initial data
        self.load_servers()
        self.load_settings()
        
        # Start status thread
        self.start_status_monitoring()
        
        # Setup window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def start_status_monitoring(self):
        """Start VPN status monitoring thread"""
        self.status_thread = VPNStatusThread(self.vpn_manager, self.update_status)
        self.status_thread.start()
        
    def load_servers(self):
        """Load server data"""
        try:
            # First try to load from VPN manager
            self.servers = self.vpn_manager.servers
            
            # If no servers or if we want to load the complete list
            if not self.servers:
                # Try to load from the countries JSON file
                countries_path = os.path.join(current_dir, "data", "countries.json")
                if os.path.exists(countries_path):
                    try:
                        with open(countries_path, 'r', encoding='utf-8') as f:
                            self.servers = json.load(f)
                            print(f"Loaded {len(self.servers)} servers from countries.json")
                            if self.servers:
                                self.server_list.populate_servers(self.servers)
                                return
                    except Exception as e:
                        print(f"Error loading countries.json: {str(e)}")
                
                # Fall back to demo servers if needed
                self.load_fallback_servers()
                
        except Exception as e:
            print(f"Error loading server data: {str(e)}")
            self.load_fallback_servers()
            
        # Display total countries information
        if self.servers:
            country_count = len(set(s.get('country', '') for s in self.servers))
            print(f"Loaded {len(self.servers)} servers in {country_count} countries")
    
    def generate_all_servers(self):
        """Generate servers for all 165 countries"""
        all_servers = []
        
        # List of all countries by region
        regions = {
            "Europe": [
                "Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina", 
                "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", 
                "France", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia", 
                "Liechtenstein", "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", 
                "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal", "Romania", "Russia", 
                "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", 
                "Ukraine", "United Kingdom", "Vatican City"
            ],
            "Asia": [
                "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", 
                "Cambodia", "China", "Georgia", "India", "Indonesia", "Iran", "Iraq", "Israel", 
                "Japan", "Jordan",