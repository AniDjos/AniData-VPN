#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AniData VPN - Main UI Application
# © 2023 AniData - All Rights Reserved

import os
import sys
import json
import time
import random
import threading
import subprocess
import shutil
from typing import Dict, List, Optional

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QPushButton, QLabel, QComboBox,
                                QTabWidget, QFrame, QSplitter, QProgressBar,
                                QSystemTrayIcon, QMenu, QAction, QMessageBox,
                                QCheckBox, QGroupBox, QFormLayout, QLineEdit,
                                QToolButton, QStackedWidget, QTableWidget,
                                QTableWidgetItem, QHeaderView)
    from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPainter, QPen
    from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QThread, QSettings, QUrl
    from PyQt5.QtWebEngineWidgets import QWebEngineView
except ImportError:
    print("ERROR: PyQt5 and PyQtWebEngine are required. Install with:")
    print("pip install PyQt5 PyQtWebEngine")
    sys.exit(1)

# Attempt to import core modules
try:
    from core.protocols.wireguard.wireguard import WireGuardManager as OriginalWireGuardManager
    
    # Wrapper class to use user-specific directories
    class WireGuardManager(OriginalWireGuardManager):
        def __init__(self, *args, **kwargs):
            # Use home directory instead of /opt/anidata
            home_dir = os.path.expanduser("~/.anidata")
            config_dir = os.path.join(home_dir, "config/wireguard")
            servers_file = os.path.join(home_dir, "servers/config.json")
            
            # Ensure directories exist
            os.makedirs(config_dir, exist_ok=True)
            os.makedirs(os.path.dirname(servers_file), exist_ok=True)
            
            # Setup sudoers script
            self._setup_sudo_script()
            
            super().__init__(config_dir=config_dir, servers_file=servers_file)
            
        def _setup_sudo_script(self):
            """Copy and set permissions for sudo script if needed"""
            try:
                project_root = os.path.join(os.path.dirname(__file__), "../..")
                script_src = os.path.join(project_root, "scripts/vpn_sudo.sh")
                script_dst = os.path.expanduser("~/.anidata/vpn_sudo.sh")
                
                if os.path.exists(script_src):
                    if not os.path.exists(script_dst) or not os.access(script_dst, os.X_OK):
                        shutil.copy2(script_src, script_dst)
                        os.chmod(script_dst, 0o755)
                        
                        # Setup sudoers entry
                        self._setup_sudoers()
            except Exception as e:
                print(f"Warning: Failed to setup sudo script: {e}")
                
        def _setup_sudoers(self):
            """Setup sudoers entry for the script"""
            try:
                # Check if we need to add a sudoers entry
                username = os.environ.get('USER', os.environ.get('USERNAME', 'user'))
                sudo_line = f"{username} ALL=(ALL) NOPASSWD: {os.path.expanduser('~/.anidata/vpn_sudo.sh')}"
                
                # Create a temporary sudoers file
                tmp_sudoers = os.path.expanduser("~/.anidata/anidata_sudoers")
                with open(tmp_sudoers, 'w') as f:
                    f.write(f"{sudo_line}\n")
                
                try:
                    # Show dialog to user explaining what we're doing
                    QMessageBox.information(None, "Élévation de privilèges",
                                           "AniData VPN a besoin de droits administrateur pour configurer l'interface réseau.\n\n"
                                           "Vous allez être invité à entrer votre mot de passe d'administrateur pour configurer les droits nécessaires.")
                    
                    # Use pkexec/gksudo to add the sudoers entry
                    cmd = f"pkexec sh -c 'cp {tmp_sudoers} /etc/sudoers.d/anidata_vpn && chmod 440 /etc/sudoers.d/anidata_vpn'"
                    subprocess.run(cmd, shell=True, check=True)
                except subprocess.CalledProcessError:
                    print("Warning: Failed to setup sudoers entry. Connections will require password each time.")
                    
                # Clean up temp file
                if os.path.exists(tmp_sudoers):
                    os.unlink(tmp_sudoers)
                    
            except Exception as e:
                print(f"Warning: Failed to setup sudoers: {e}")
            except Exception as e:
                print(f"Erreur d'initialisation de WireGuard: {str(e)}")
                # Fallback to mock implementation
                self.servers = []
                self._wireguard_available = False
            
except ImportError:
    print("WARNING: Could not import core modules. Running in UI-only mode.")
    
    # Placeholder class for demonstration
    class WireGuardManager:
        def __init__(self, *args, **kwargs):
            self.servers = []
            self._wireguard_available = False
            
        def get_server(self, server_id=None):
            return None
            
        def connect(self, *args, **kwargs):
            # Check if WireGuard tools are installed
            try:
                result = subprocess.run(["which", "wg"], capture_output=True, text=True)
                if result.returncode != 0:
                    return {"success": False, "error": "WireGuard tools are not installed. Please install 'wireguard-tools' package."}
            except Exception:
                pass
                
            # Check for sudo script
            sudo_script = os.path.expanduser("~/.anidata/vpn_sudo.sh")
            if not os.path.exists(sudo_script) or not os.access(sudo_script, os.X_OK):
                return {"success": False, "error": "Les scripts d'élévation de privilèges ne sont pas configurés correctement."}
                
            # For UI-only mode, we simulate a successful connection after a delay
            time.sleep(2)  # Simulate connection delay
            server_id = kwargs.get('server_id')
            
            # Find server in server list for the response
            server = None
            for s in self.servers:
                if s.get('id') == server_id:
                    server = s
                    break
                    
            if server:
                return {
                    "success": True,
                    "server": {
                        "id": server.get("id"),
                        "country": server.get("country"),
                        "city": server.get("city")
                    },
                    "interface": "demo0",
                    "config_file": "/home/user/.anidata/config/demo.conf",
                    "public_key": "DemoPublicKey123456789ABCDEF="
                }
            
            return {"success": False, "error": "Running in UI-only mode (server not found)"}
            
        def disconnect(self):
            return {"success": True, "message": "Disconnected in UI-only mode"}
            
        def get_status(self):
            # If we've successfully "connected" in the UI, show as connected
            if hasattr(self, '_connected') and self._connected:
                return {
                    "connected": True,
                    "server": self._connected_server,
                    "protocol": self._connected_protocol,
                    "connection_info": {
                        "interface": "demo0",
                        "local_ip": "10.10.10.2",
                        "remote_endpoint": f"{self._connected_server.get('ip', '0.0.0.0')}:51820",
                        "transfer_rx": f"{random.randint(1, 100)} MB",
                        "transfer_tx": f"{random.randint(1, 50)} MB",
                        "latest_handshake": "1 minute ago"
                    }
                }
            return {"connected": False, "message": "Running in UI-only mode"}


# Default application settings
DEFAULT_SETTINGS = {
    "auto_connect": False,
    "default_protocol": "wireguard",
    "startup_connect": False,
    "minimize_to_tray": True,
    "default_server": None,
    "theme": "lovable",
    "kill_switch": True,
    "dns_leak_protection": True,
    "ipv6_leak_protection": True,
}


class VPNStatusThread(QThread):
    """Thread for monitoring VPN connection status"""
    status_updated = pyqtSignal(dict)
    
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.running = True
        
    def run(self):
        while self.running:
            try:
                status = self.manager.get_status()
                self.status_updated.emit(status)
            except Exception as e:
                print(f"Error getting status: {str(e)}")
            
            # Sleep for 3 seconds
            time.sleep(3)
    
    def stop(self):
        self.running = False
        self.wait()


class MapWidget(QWebEngineView):
    """Widget for displaying interactive world map with server locations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Load the HTML map file
        map_path = os.path.join(os.path.dirname(__file__), '..', 'maps', 'world_map.html')
        
        # If the map file doesn't exist, create a simple one
        if not os.path.exists(map_path):
            self._create_simple_map(map_path)
            
        self.load(QUrl.fromLocalFile(map_path))
    
    def _create_simple_map(self, map_path):
        """Create a simple HTML map if the actual map file doesn't exist"""
        os.makedirs(os.path.dirname(map_path), exist_ok=True)
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AniData VPN Server Map</title>
            <style>
                body { margin: 0; padding: 0; background-color: #2c3e50; color: white; font-family: Arial, sans-serif; }
                #map-container { width: 100%; height: 100vh; display: flex; justify-content: center; align-items: center; }
                h2 { text-align: center; }
            </style>
        </head>
        <body>
            <div id="map-container">
                <h2>AniData VPN Interactive Map<br>(Placeholder)</h2>
            </div>
        </body>
        </html>
        """
        
        with open(map_path, 'w') as f:
            f.write(html_content)


# Import random module for simulation
import random

class ServerListWidget(QWidget):
    """Widget for displaying and selecting VPN servers"""
    
    server_selected = pyqtSignal(dict)
    
    def __init__(self, servers, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.servers = servers
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Search bar (placeholder)
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search servers...")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Server table
        self.server_table = QTableWidget()
        self.server_table.setColumnCount(4)
        self.server_table.setHorizontalHeaderLabels(["Location", "Load", "Ping", "Features"])
        self.server_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.server_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.server_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.server_table.setSelectionMode(QTableWidget.SingleSelection)
        self.server_table.itemClicked.connect(self.on_server_selected)
        
        # Populate with servers
        self.populate_servers()
        
        layout.addWidget(self.server_table)
        
        # Set layout margins
        layout.setContentsMargins(0, 0, 0, 0)
        
    def populate_servers(self):
        """Populate the server table with server data"""
        self.server_table.setRowCount(0)  # Clear table
        
        for server in self.servers:
            row = self.server_table.rowCount()
            self.server_table.insertRow(row)
            
            # Location (Country, City)
            location = f"{server.get('country', 'Unknown')}, {server.get('city', 'Unknown')}"
            location_item = QTableWidgetItem(location)
            self.server_table.setItem(row, 0, location_item)
            
            # Load (simulated)
            load = f"{random.randint(10, 90)}%"
            load_item = QTableWidgetItem(load)
            self.server_table.setItem(row, 1, load_item)
            
            # Ping (simulated)
            ping = f"{random.randint(5, 300)} ms"
            ping_item = QTableWidgetItem(ping)
            self.server_table.setItem(row, 2, ping_item)
            
            # Features
            features = []
            capabilities = server.get('capabilities', {})
            if capabilities.get('multi_hop', False):
                features.append("Multi-hop")
            if capabilities.get('obfuscation', False):
                features.append("Obfuscation")
            if capabilities.get('streaming', False):
                features.append("Streaming")
            if capabilities.get('p2p', False):
                features.append("P2P")
                
            features_str = ", ".join(features) if features else "Standard"
            features_item = QTableWidgetItem(features_str)
            self.server_table.setItem(row, 3, features_item)
            
            # Store server data in the first column item
            location_item.setData(Qt.UserRole, server)
    
    def on_server_selected(self, item):
        """Handle server selection"""
        # Get the server data from the first column of the selected row
        row = item.row()
        server = self.server_table.item(row, 0).data(Qt.UserRole)
        if server:
            self.server_selected.emit(server)


class ConnectionWidget(QWidget):
    """Widget for connecting to VPN servers"""
    
    connect_clicked = pyqtSignal()
    disconnect_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.selected_server = None
        self.connect_icon = ""
        self.disconnect_icon = ""
        self.initUI()
        
    def update_button_icons(self):
        """Update button icons based on the current theme"""
        if hasattr(self.parent, 'theme_assets'):
            # Set connect button icon
            connect_icon_path = self.parent.theme_assets["connect_icon"]
            if os.path.exists(connect_icon_path):
                self.connect_button.setIcon(QIcon(connect_icon_path))
                
            # Set disconnect button icon
            disconnect_icon_path = self.parent.theme_assets["disconnect_icon"]
            if os.path.exists(disconnect_icon_path):
                self.disconnect_button.setIcon(QIcon(disconnect_icon_path))
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Connection status
        status_group = QGroupBox("Connection Status")
        status_layout = QFormLayout()
        
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addRow("Status:", self.status_label)
        
        self.server_label = QLabel("None")
        status_layout.addRow("Server:", self.server_label)
        
        self.protocol_label = QLabel("None")
        status_layout.addRow("Protocol:", self.protocol_label)
        
        self.ip_label = QLabel("Not connected")
        status_layout.addRow("IP Address:", self.ip_label)
        
        self.uptime_label = QLabel("0:00:00")
        status_layout.addRow("Uptime:", self.uptime_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Connection controls
        controls_group = QGroupBox("Connection Controls")
        controls_layout = QVBoxLayout()
        
        # Protocol selection
        protocol_layout = QHBoxLayout()
        protocol_label = QLabel("Protocol:")
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["WireGuard", "OpenVPN", "IKEv2", "Stealth"])
        protocol_layout.addWidget(protocol_label)
        protocol_layout.addWidget(self.protocol_combo)
        controls_layout.addLayout(protocol_layout)
        
        # Connect/Disconnect buttons
        buttons_layout = QHBoxLayout()
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "..", "assets", "connect.png")))
        self.connect_button.clicked.connect(self.on_connect_clicked)
        self.connect_button.setMinimumHeight(40)
        
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "..", "assets", "disconnect.png")))
        self.disconnect_button.clicked.connect(self.disconnect_clicked)
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.setMinimumHeight(40)
        
        buttons_layout.addWidget(self.connect_button)
        buttons_layout.addWidget(self.disconnect_button)
        controls_layout.addLayout(buttons_layout)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Security options
        security_group = QGroupBox("Security Options")
        security_layout = QVBoxLayout()
        
        self.kill_switch_check = QCheckBox("Kill Switch")
        self.kill_switch_check.setToolTip("Blocks all traffic when VPN is disconnected")
        security_layout.addWidget(self.kill_switch_check)
        
        self.dns_leak_check = QCheckBox("DNS Leak Protection")
        security_layout.addWidget(self.dns_leak_check)
        
        self.ipv6_leak_check = QCheckBox("IPv6 Leak Protection")
        security_layout.addWidget(self.ipv6_leak_check)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        # Add stretch to push everything to the top
        layout.addStretch(1)
        
    def set_selected_server(self, server):
        """Set the selected server"""
        self.selected_server = server
        self.server_label.setText(f"{server.get('country', 'Unknown')}, {server.get('city', 'Unknown')}")
        
    def on_connect_clicked(self):
        """Handle connect button click"""
        if not self.selected_server:
            QMessageBox.warning(self, "No Server Selected", 
                                "Please select a server from the server list before connecting.")
            return
        
        # Get selected protocol
        protocol = self.protocol_combo.currentText().lower()
        
        # Emit connect signal with server and protocol
        self.connect_clicked.emit({
            "server": self.selected_server,
            "protocol": protocol,
            "kill_switch": self.kill_switch_check.isChecked(),
            "dns_leak_protection": self.dns_leak_check.isChecked(),
            "ipv6_leak_protection": self.ipv6_leak_check.isChecked()
        })
    
    def update_status(self, status):
        """Update connection status display"""
        connected = status.get("connected", False)
        
        if connected:
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            
            # Update server info if available
            server = status.get("server", {})
            if server:
                self.server_label.setText(f"{server.get('country', 'Unknown')}, {server.get('city', 'Unknown')}")
            
            # Update protocol
            protocol = status.get("protocol", self.protocol_combo.currentText())
            self.protocol_label.setText(protocol)
            
            # Update IP (simulated)
            self.ip_label.setText("192.168.x.x (VPN)")
            
            # Start uptime counter if not already running
            if not hasattr(self, 'uptime_timer') or not self.uptime_timer.isActive():
                self.uptime_start = time.time()
                self.uptime_timer = QTimer(self)
                self.uptime_timer.timeout.connect(self.update_uptime)
                self.uptime_timer.start(1000)  # Update every second
        else:
            self.status_label.setText("Disconnected")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.protocol_label.setText("None")
            self.ip_label.setText("Not connected")
            
            # Stop uptime timer if running
            if hasattr(self, 'uptime_timer') and self.uptime_timer.isActive():
                self.uptime_timer.stop()
            
            self.uptime_label.setText("0:00:00")
    
    def update_uptime(self):
        """Update the uptime display"""
        elapsed = int(time.time() - self.uptime_start)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        self.uptime_label.setText(f"{hours}:{minutes:02d}:{seconds:02d}")


# Import random for simulated statistics
import random

class StatisticsWidget(QWidget):
    """Widget for displaying VPN connection statistics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Traffic graph (placeholder)
        graph_group = QGroupBox("Traffic Graph")
        graph_layout = QVBoxLayout()
        
        self.graph_placeholder = QLabel("Traffic graph will be displayed here")
        self.graph_placeholder.setAlignment(Qt.AlignCenter)
        self.graph_placeholder.setStyleSheet("background-color: #334455; padding: 50px;")
        graph_layout.addWidget(self.graph_placeholder)
        
        graph_group.setLayout(graph_layout)
        layout.addWidget(graph_group)
        
        # Connection statistics
        stats_group = QGroupBox("Connection Statistics")
        stats_layout = QFormLayout()
        
        self.download_label = QLabel("0 B/s")
        stats_layout.addRow("Download:", self.download_label)
        
        self.upload_label = QLabel("0 B/s")
        stats_layout.addRow("Upload:", self.upload_label)
        
        self.total_down_label = QLabel("0 B")
        stats_layout.addRow("Total Download:", self.total_down_label)
        
        self.total_up_label = QLabel("0 B")
        stats_layout.addRow("Total Upload:", self.total_up_label)
        
        self.latency_label = QLabel("0 ms")
        stats_layout.addRow("Latency:", self.latency_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Add stretch to push everything to the top
        layout.addStretch(1)
        
    def update_statistics(self, status):
        """Update connection statistics display"""
        connected = status.get("connected", False)
        
        if connected:
            # Get server region for region-specific latency simulation
            server = status.get("server", {})
            region = server.get("region", "").lower() if server else ""
            
            # Simulate better latency for nearby regions and worse for distant ones
            if region == "europe":
                latency = random.randint(5, 50)
            elif region in ["north america", "asia"]:
                latency = random.randint(80, 150)
            else:
                latency = random.randint(150, 300)
                
            # Simulate bandwidth based on server capabilities
            bandwidth = server.get("bandwidth", 5000) if server else 5000
            download_speed = random.randint(bandwidth // 10, bandwidth // 2)
            upload_speed = random.randint(bandwidth // 20, bandwidth // 4)
            
            # In a real implementation, this would use actual data
            # For this demo, we'll use simulated values
            self.download_label.setText(f"{download_speed} KB/s")
            self.upload_label.setText(f"{upload_speed} KB/s")
            
            # Accumulate total (in a real app, this would persist between updates)
            current_down = self.total_down_label.text().split()[0]
            current_up = self.total_up_label.text().split()[0]
            
            try:
                total_down = float(current_down) + random.uniform(0.1, 1.0)
                total_up = float(current_up) + random.uniform(0.05, 0.5)
            except ValueError:
                total_down = random.uniform(0.1, 1.0)
                total_up = random.uniform(0.05, 0.5)
            
            self.total_down_label.setText(f"{total_down:.2f} MB")
            self.total_up_label.setText(f"{total_up:.2f} MB")
            
            self.latency_label.setText(f"{latency} ms")
        else:
            self.download_label.setText("0 B/s")
            self.upload_label.setText("0 B/s")
            self.latency_label.setText("0 ms")
            # Don't reset total counters


class SettingsWidget(QWidget):
    """Widget for configuring VPN settings"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, settings=None, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.settings = settings or DEFAULT_SETTINGS.copy()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout()
        
        self.auto_connect_check = QCheckBox("Auto-connect to last server")
        self.auto_connect_check.setChecked(self.settings.get("auto_connect", False))
        general_layout.addWidget(self.auto_connect_check)
        
        self.startup_check = QCheckBox("Connect on application startup")
        self.startup_check.setChecked(self.settings.get("startup_connect", False))
        general_layout.addWidget(self.startup_check)
        
        self.minimize_check = QCheckBox("Minimize to system tray")
        self.minimize_check.setChecked(self.settings.get("minimize_to_tray", True))
        general_layout.addWidget(self.minimize_check)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # Protocol settings
        protocol_group = QGroupBox("Protocol Settings")
        protocol_layout = QFormLayout()
        
        self.default_protocol_combo = QComboBox()
        self.default_protocol_combo.addItems(["wireguard", "openvpn", "ikev2", "stealth"])
        default_protocol = self.settings.get("default_protocol", "wireguard")
        index = self.default_protocol_combo.findText(default_protocol)
        if index >= 0:
            self.default_protocol_combo.setCurrentIndex(index)
        protocol_layout.addRow("Default Protocol:", self.default_protocol_combo)
        
        protocol_group.setLayout(protocol_layout)
        layout.addWidget(protocol_group)
        
        # UI settings
        ui_group = QGroupBox("User Interface")
        ui_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light", "lovable"])
        theme = self.settings.get("theme", "dark")
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        ui_layout.addRow("Theme:", self.theme_combo)
        
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)
        
        # Add stretch to push everything to the top
        layout.addStretch(1)
        
    def save_settings(self):
        """Save settings and emit settings_changed signal"""
        self.settings = {
            "auto_connect": self.auto_connect_check.isChecked(),
            "startup_connect": self.startup_check.isChecked(),
            "minimize_to_tray": self.minimize_check.isChecked(),
            "default_protocol": self.default_protocol_combo.currentText(),
            "theme": self.theme_combo.currentText(),
        }
        
        self.settings_changed.emit(self.settings)
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Ensure user config directory exists
        home_dir = os.path.expanduser("~/.anidata")
        os.makedirs(home_dir, exist_ok=True)
        
        self.vpn_manager = WireGuardManager()
        self.settings = QSettings("AniData", "VPN")
        self.load_settings()
        
        # Theme-specific assets paths
        self.theme_assets = {
            "connect_icon": "",
            "disconnect_icon": "",
            "settings_icon": "",
            "tray_icon": "",
            "logo": ""
        }
        self.update_theme_assets(self.app_settings.get("theme", "dark"))
        
    def update_theme_assets(self, theme):
        """Update asset paths based on the selected theme"""
        base_dir = os.path.dirname(__file__)
        
        if theme == "lovable":
            # Use lovable.ai style assets
            self.theme_assets = {
                "connect_icon": os.path.join(base_dir, "..", "assets", "lovable", "connect.png"),
                "disconnect_icon": os.path.join(base_dir, "..", "assets", "lovable", "disconnect.png"),
                "settings_icon": os.path.join(base_dir, "..", "assets", "lovable", "settings.png"),
                "tray_icon": os.path.join(base_dir, "..", "assets", "lovable", "tray_icon.png"),
                "logo": os.path.join(base_dir, "..", "assets", "lovable", "logo.png")
            }
        else:
            # Use default assets
            self.theme_assets = {
                "connect_icon": os.path.join(base_dir, "..", "assets", "connect.png"),
                "disconnect_icon": os.path.join(base_dir, "..", "assets", "disconnect.png"),
                "settings_icon": os.path.join(base_dir, "..", "assets", "settings.png"),
                "tray_icon": os.path.join(base_dir, "..", "assets", "tray_icon.png"),
                "logo": os.path.join(base_dir, "..", "assets", "logo.png")
            }
        
        # Start status monitoring thread
        self.status_thread = VPNStatusThread(self.vpn_manager)
        self.status_thread.status_updated.connect(self.update_status)
        self.status_thread.start()
        
        # Try to load server data
        self.load_server_data()
        
    def initUI(self):
        """Initialize the user interface"""
        self.setWindowTitle("AniData VPN")
        self.setMinimumSize(900, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Header with logo
        header_layout = QHBoxLayout()
        
        # Logo
        logo_path = self.theme_assets["logo"]
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path).scaledToHeight(60, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
            header_layout.addWidget(logo_label)
        
        # Title
        title_label = QLabel("AniData VPN")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Add stretch to push logo and title to the left
        header_layout.addStretch(1)
        
        # Settings button
        settings_button = QToolButton()
        settings_button.setIcon(QIcon(self.theme_assets["settings_icon"]))
        settings_button.setIconSize(QSize(24, 24))
        settings_button.clicked.connect(self.show_settings)
        header_layout.addWidget(settings_button)
        
        main_layout.addLayout(header_layout)
        
        # Main content - split view
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Server list
        self.server_widget = ServerListWidget(self.vpn_manager.servers, self)
        self.server_widget.server_selected.connect(self.on_server_selected)
        splitter.addWidget(self.server_widget)
        
        # Right side - Tabs (Connection, Map, Statistics)
        tabs = QTabWidget()
        
        # Connection tab
        self.connection_widget = ConnectionWidget(self)
        self.connection_widget.connect_clicked.connect(self.on_connect)
        self.connection_widget.disconnect_clicked.connect(self.on_disconnect)
        tabs.addTab(self.connection_widget, "Connection")
        
        # Map tab
        self.map_widget = MapWidget(self)
        tabs.addTab(self.map_widget, "World Map")
        
        # Statistics tab
        self.statistics_widget = StatisticsWidget(self)
        tabs.addTab(self.statistics_widget, "Statistics")
        
        splitter.addWidget(tabs)
        
        # Set splitter sizes (40% left, 60% right)
        splitter.setSizes([40, 60])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # System tray icon
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = self.theme_assets["tray_icon"]
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        connect_action = QAction("Connect", self)
        connect_action.triggered.connect(self.tray_connect)
        tray_menu.addAction(connect_action)
        
        disconnect_action = QAction("Disconnect", self)
        disconnect_action.triggered.connect(self.on_disconnect)
        tray_menu.addAction(disconnect_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close_application)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Apply theme
        self.apply_theme()
        
    def load_settings(self):
        """Load application settings"""
        self.app_settings = DEFAULT_SETTINGS.copy()
        
        for key in DEFAULT_SETTINGS.keys():
            if self.settings.contains(key):
                self.app_settings[key] = self.settings.value(key)
        
    def save_settings(self):
        """Save application settings"""
        for key, value in self.app_settings.items():
            self.settings.setValue(key, value)
    
    def apply_theme(self):
        """Apply the selected theme to the application"""
        theme = self.app_settings.get("theme")
        
        # Update assets paths based on theme
        self.update_theme_assets(theme)
        
        if theme == "lovable":
            # Lovable.ai theme
            css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "lovable_theme.css")
            if os.path.exists(css_path):
                with open(css_path, 'r') as file:
                    self.setStyleSheet(file.read())
            else:
                # Fallback if CSS file is missing
                print("Warning: lovable_theme.css not found, using light theme instead")
                self.app_settings["theme"] = "light"
                self.apply_theme()
                return
        elif theme == "dark":
            # Dark theme
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #2c3e50; color: #ecf0f1; }
                QTabWidget::pane { border: 1px solid #34495e; }
                QTabWidget::tab-bar { left: 5px; }
                QTabBar::tab { background-color: #34495e; color: #ecf0f1; padding: 8px 12px; margin-right: 2px; }
                QTabBar::tab:selected { background-color: #3498db; }
                QPushButton { background-color: #3498db; color: white; border: none; padding: 8px 16px; }
                QPushButton:hover { background-color: #2980b9; }
                QPushButton:disabled { background-color: #95a5a6; }
                QComboBox { background-color: #34495e; color: #ecf0f1; padding: 5px; }
                QLineEdit { background-color: #34495e; color: #ecf0f1; padding: 5px; }
                QGroupBox { border: 1px solid #34495e; margin-top: 12px; padding-top: 15px; }
                QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }
                QTableWidget { gridline-color: #34495e; }
                QHeaderView::section { background-color: #34495e; color: #ecf0f1; padding: 5px; }
            """)
        else:
            # Light theme (default)
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #ecf0f1; color: #2c3e50; }
                QTabWidget::pane { border: 1px solid #bdc3c7; }
                QTabWidget::tab-bar { left: 5px; }
                QTabBar::tab { background-color: #bdc3c7; color: #2c3e50; padding: 8px 12px; margin-right: 2px; }
                QTabBar::tab:selected { background-color: #3498db; color: white; }
                QPushButton { background-color: #3498db; color: white; border: none; padding: 8px 16px; }
                QPushButton:hover { background-color: #2980b9; }
                QPushButton:disabled { background-color: #95a5a6; }
                QComboBox { background-color: white; color: #2c3e50; padding: 5px; }
                QLineEdit { background-color: white; color: #2c3e50; padding: 5px; }
                QGroupBox { border: 1px solid #bdc3c7; margin-top: 12px; padding-top: 15px; }
                QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }
                QTableWidget { gridline-color: #bdc3c7; }
                QHeaderView::section { background-color: #bdc3c7; color: #2c3e50; padding: 5px; }
            """)
        
        # Update UI elements with new icons
        if hasattr(self, 'connection_widget'):
            self.connection_widget.update_button_icons()
    
    def load_server_data(self):
        """Load server data from configuration file"""
        try:
            # Try to load from server configuration file
            home_dir = os.path.expanduser("~/.anidata")
            project_root = os.path.join(os.path.dirname(__file__), "../..")
            
            # First try loading from project directory
            servers_file = os.path.join(project_root, "infrastructure/servers/config.json")
            
            # If not found, try user home directory
            if not os.path.exists(servers_file):
                servers_file = os.path.join(home_dir, "servers/config.json")
                
                # If still not found, copy from project if available
                if not os.path.exists(servers_file) and os.path.exists(os.path.join(project_root, "infrastructure/servers/config.json")):
                    os.makedirs(os.path.dirname(servers_file), exist_ok=True)
                    import shutil
                    shutil.copy2(
                        os.path.join(project_root, "infrastructure/servers/config.json"),
                        servers_file
                    )
            
            if os.path.exists(servers_file):
                with open(servers_file, 'r') as f:
                    data = json.load(f)
                    self.vpn_manager.servers = data.get("servers", [])
            else:
                # Use fallback data if file not found
                self.load_fallback_server_data()
                
            # Refresh server list widget
            self.server_widget.servers = self.vpn_manager.servers
            self.server_widget.populate_servers()
            
        except Exception as e:
            print(f"Error loading server data: {str(e)}")
            self.load_fallback_server_data()
    
    def load_fallback_server_data(self):
        """Load fallback server data for demo purposes"""
        # Sample server data for UI demonstration
        self.vpn_manager.servers = [
            {
                "id": "fr-01",
                "region": "Europe",
                "country": "France",
                "city": "Paris",
                "protocols": ["wireguard", "openvpn", "ikev2"],
                "capabilities": {
                    "multi_hop": True,
                    "obfuscation": True,
                    "streaming": True,
                    "p2p": True
                }
            },
            {
                "id": "us-01",
                "region": "North America",
                "country": "United States",
                "city": "New York",
                "protocols": ["wireguard", "openvpn", "ikev2", "stealth"],
                "capabilities": {
                    "multi_hop": True,
                    "obfuscation": True,
                    "streaming": True,
                    "p2p": False
                }
            },
            {
                "id": "jp-01",
                "region": "Asia",
                "country": "Japan",
                "city": "Tokyo",
                "protocols": ["wireguard", "openvpn"],
                "capabilities": {
                    "multi_hop": True,
                    "obfuscation": False,
                    "streaming": True,
                    "p2p": False
                }
            }
        ]
        
        # Update the server list widget
        if hasattr(self, 'server_widget'):
            self.server_widget.servers = self.vpn_manager.servers
            self.server_widget.populate_servers()
    
    def on_server_selected(self, server):
        """Handle server selection"""
        self.connection_widget.set_selected_server(server)
        self.statusBar().showMessage(f"Selected server: {server.get('country')}, {server.get('city')}")
    
    def on_connect(self, options):
        """Handle connect button click"""
        server = options.get("server", {})
        protocol = options.get("protocol", "wireguard")
        
        self.statusBar().showMessage(f"Connecting to {server.get('country')}, {server.get('city')} using {protocol}...")
        
        # Save selected options to settings
        self.app_settings["kill_switch"] = options.get("kill_switch", True)
        self.app_settings["dns_leak_protection"] = options.get("dns_leak_protection", True)
        self.app_settings["ipv6_leak_protection"] = options.get("ipv6_leak_protection", True)
        self.app_settings["default_server"] = server.get("id")
        self.save_settings()
        
        # Check if WireGuard tools are installed and sudo script is available
        if protocol.lower() == "wireguard":
            try:
                # Check for WireGuard tools
                result = subprocess.run(["which", "wg"], capture_output=True, text=True)
                if result.returncode != 0:
                    error = "WireGuard tools are not installed. Please install 'wireguard-tools' package."
                    self.statusBar().showMessage(f"Connection failed: {error}")
                    QMessageBox.warning(self, "Connection Failed", f"Failed to connect to VPN: {error}")
                    
                    # Offer to install WireGuard
                    reply = QMessageBox.question(self, "Install WireGuard?", 
                                               "Would you like to install WireGuard tools now?",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    if reply == QMessageBox.Yes:
                        try:
                            self.statusBar().showMessage("Installing WireGuard tools...")
                            install_cmd = "pkexec apt-get install -y wireguard-tools"
                            subprocess.run(install_cmd, shell=True, check=True)
                            self.statusBar().showMessage("WireGuard tools installed. Trying to connect...")
                            # Continue with connection attempt
                        except Exception as e:
                            self.statusBar().showMessage(f"Failed to install WireGuard tools: {str(e)}")
                            return
                    else:
                        return
                
                # Check for sudo script
                sudo_script = os.path.expanduser("~/.anidata/vpn_sudo.sh")
                if not os.path.exists(sudo_script) or not os.access(sudo_script, os.X_OK):
                    # Try to set up the script
                    try:
                        if hasattr(self.vpn_manager, '_setup_sudo_script'):
                            self.vpn_manager._setup_sudo_script()
                        else:
                            error = "Les scripts d'élévation de privilèges ne sont pas configurés correctement."
                            self.statusBar().showMessage(f"Connection failed: {error}")
                            QMessageBox.warning(self, "Connection Failed", error)
                            return
                    except Exception as e:
                        self.statusBar().showMessage(f"Failed to setup sudo script: {str(e)}")
                        return
                        
            except Exception:
                pass
        
        # Connect to VPN
        result = self.vpn_manager.connect(server_id=server.get("id"))
        
        # Check for permission error and suggest running as admin
        if not result.get("success", False) and "Permission" in str(result.get("error", "")):
            error_msg = "Erreur de permission lors de la création de l'interface VPN.\n\n"
            error_msg += "Solutions possibles:\n"
            error_msg += "1. Exécutez l'application en tant qu'administrateur:\n"
            error_msg += "   sudo ./scripts/run_ui.sh\n\n"
            error_msg += "2. Ou accordez les droits nécessaires en exécutant:\n"
            error_msg += "   sudo chmod +s ~/.anidata/vpn_sudo.sh"
            
            QMessageBox.critical(self, "Erreur de Permission", error_msg)
            self.statusBar().showMessage("Échec de connexion: Erreur de permission")
            return
        
        # For UI-only mode, store connection state
        if hasattr(self.vpn_manager, '_connected'):
            self.vpn_manager._connected = result.get("success", False)
            self.vpn_manager._connected_server = server
            self.vpn_manager._connected_protocol = protocol
        
        if result.get("success", False):
            self.statusBar().showMessage(f"Connected to {server.get('country')}, {server.get('city')}")
            
            # Update status in all widgets
            status = {
                "connected": True,
                "server": server,
                "protocol": protocol
            }
            
            self.update_status(status)
        else:
            error = result.get("error", "Unknown error")
            self.statusBar().showMessage(f"Connection failed: {error}")
            QMessageBox.warning(self, "Connection Failed", f"Failed to connect to VPN: {error}")
    
    def on_disconnect(self):
        """Handle disconnect button click"""
        self.statusBar().showMessage("Disconnecting...")
        
        # Disconnect from VPN
        result = self.vpn_manager.disconnect()
        
        # For UI-only mode, update connection state
        if hasattr(self.vpn_manager, '_connected'):
            self.vpn_manager._connected = False
            self.vpn_manager._connected_server = None
            self.vpn_manager._connected_protocol = None
        
        if result.get("success", False):
            self.statusBar().showMessage("Disconnected")
            
            # Update status in all widgets
            status = {"connected": False}
            self.update_status(status)
        else:
            # In UI-only mode, we'll still show as disconnected
            self.statusBar().showMessage("Disconnected")
            status = {"connected": False}
            self.update_status(status)
            
            # Only show error if not in UI-only mode
            if "UI-only mode" not in result.get("error", ""):
                error = result.get("error", "Unknown error")
                self.statusBar().showMessage(f"Disconnection failed: {error}")
                QMessageBox.warning(self, "Disconnection Failed", f"Failed to disconnect from VPN: {error}")
    
    def tray_connect(self):
        """Connect to the last used server from the system tray"""
        server_id = self.app_settings.get("default_server")
        if not server_id:
            self.show()
            QMessageBox.information(self, "No Default Server", 
                                   "No default server is set. Please select a server first.")
            return
        
        # Find the server in the list
        server = None
        for s in self.vpn_manager.servers:
            if s.get("id") == server_id:
                server = s
                break
        
        if not server:
            self.show()
            QMessageBox.information(self, "Server Not Found", 
                                   "Default server not found. Please select a server.")
            return
        
        # Connect using saved settings
        options = {
            "server": server,
            "protocol": self.app_settings.get("default_protocol", "wireguard"),
            "kill_switch": self.app_settings.get("kill_switch", True),
            "dns_leak_protection": self.app_settings.get("dns_leak_protection", True),
            "ipv6_leak_protection": self.app_settings.get("ipv6_leak_protection", True)
        }
        
        self.on_connect(options)
    
    def show_settings(self):
        """Show settings dialog"""
        # Create settings widget if it doesn't exist
        if not hasattr(self, 'settings_widget'):
            self.settings_widget = SettingsWidget(self.app_settings, self)
            self.settings_widget.settings_changed.connect(self.on_settings_changed)
        
        # Create a dialog to show settings
        dialog = QDialog(self)
        dialog.setWindowTitle("AniData VPN Settings")
        dialog.setMinimumWidth(400)
        
        # Apply current theme to dialog
        theme = self.app_settings.get("theme")
        if theme == "lovable":
            css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "lovable_theme.css")
            if os.path.exists(css_path):
                with open(css_path, 'r') as file:
                    dialog.setStyleSheet(file.read())
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(self.settings_widget)
        
        # Add header with logo for lovable theme
        if theme == "lovable":
            header_layout = QHBoxLayout()
            logo_path = self.theme_assets["logo"]
            if os.path.exists(logo_path):
                logo_label = QLabel()
                logo_pixmap = QPixmap(logo_path).scaledToHeight(40, Qt.SmoothTransformation)
                logo_label.setPixmap(logo_pixmap)
                header_layout.addWidget(logo_label)
            
            title_label = QLabel("Settings")
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #6c5ce7;")
            header_layout.addWidget(title_label)
            header_layout.addStretch(1)
            
            # Insert header at the top of the layout
            layout.insertLayout(0, header_layout)
        
        dialog.exec_()
    
    def on_settings_changed(self, new_settings):
        """Handle settings changes"""
        self.app_settings.update(new_settings)
        self.save_settings()
        
        # Apply new theme if changed
        if new_settings.get("theme") != self.app_settings.get("theme"):
            self.apply_theme()
    
    def update_status(self, status):
        """Update status in all widgets"""
        self.connection_widget.update_status(status)
        self.statistics_widget.update_statistics(status)
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.app_settings.get("minimize_to_tray", True):
            event.ignore()
            self.hide()
            
            # Show notification
            self.tray_icon.showMessage(
                "AniData VPN",
                "Application minimized to system tray",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self.close_application()
    
    def close_application(self):
        """Close the application"""
        # Stop status thread
        if hasattr(self, 'status_thread'):
            self.status_thread.stop()
        
        # Disconnect from VPN if connected
        status = self.vpn_manager.get_status()
        if status.get("connected", False):
            self.vpn_manager.disconnect()
        
        # Save settings
        self.save_settings()
        
        # Exit
        QApplication.quit()


def run_as_admin():
    """Check if the application is running with admin privileges"""
    try:
        # Check if we can write to a system directory
        return os.access('/etc', os.W_OK)
    except:
        return False

def create_assets_directory():
    """Create assets directory with placeholder images if it doesn't exist"""
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    # Create placeholder images if they don't exist
    placeholders = {
        "logo.png": (200, 60, (52, 152, 219)),  # Blue logo
        "connect.png": (24, 24, (46, 204, 113)),  # Green connect icon
        "disconnect.png": (24, 24, (231, 76, 60)),  # Red disconnect icon
        "settings.png": (24, 24, (52, 152, 219)),  # Blue settings icon
        "tray_icon.png": (16, 16, (52, 152, 219)),  # Blue tray icon
    }
    
    for filename, (width, height, color) in placeholders.items():
        filepath = os.path.join(assets_dir, filename)
        if not os.path.exists(filepath):
            try:
                from PIL import Image
                img = Image.new('RGB', (width, height), color)
                img.save(filepath)
                print(f"Created placeholder image: {filepath}")
            except ImportError:
                print("PIL (Pillow) is not installed. Cannot create placeholder images.")
                break


def create_maps_directory():
    """Create maps directory with a simple HTML map if it doesn't exist"""
    maps_dir = os.path.join(os.path.dirname(__file__), "..", "maps")
    os.makedirs(maps_dir, exist_ok=True)
    
    map_path = os.path.join(maps_dir, "world_map.html")
    if not os.path.exists(map_path):
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>AniData VPN Server Map</title>
            <style>
                body { margin: 0; padding: 0; background-color: #2c3e50; color: white; font-family: Arial, sans-serif; }
                #map-container { width: 100%; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; }
                h2 { text-align: center; }
                .server-list { margin-top: 20px; width: 80%; max-width: 600px; }
                .server { background-color: #34495e; margin: 10px 0; padding: 10px; border-radius: 5px; display: flex; justify-content: space-between; }
                .server-location { font-weight: bold; }
                .server-status { color: #2ecc71; }
                .europe { border-left: 5px solid #3498db; }
                .northamerica { border-left: 5px solid #e74c3c; }
                .asia { border-left: 5px solid #f1c40f; }
                .southamerica { border-left: 5px solid #2ecc71; }
                .africa { border-left: 5px solid #9b59b6; }
                .oceania { border-left: 5px solid #e67e22; }
            </style>
        </head>
        <body>
            <div id="map-container">
                <h2>AniData VPN Server Network</h2>
                <div class="server-list">
                    <div class="server europe">
                        <span class="server-location">France, Paris</span>
                        <span class="server-status">Active</span>
                    </div>
                    <div class="server northamerica">
                        <span class="server-location">United States, New York</span>
                        <span class="server-status">Active</span>
                    </div>
                    <div class="server asia">
                        <span class="server-location">Japan, Tokyo</span>
                        <span class="server-status">Active</span>
                    </div>
                    <div class="server asia">
                        <span class="server-location">Singapore</span>
                        <span class="server-status">Active</span>
                    </div>
                    <div class="server oceania">
                        <span class="server-location">Australia, Sydney</span>
                        <span class="server-status">Active</span>
                    </div>
                    <div class="server southamerica">
                        <span class="server-location">Brazil, Sao Paulo</span>
                        <span class="server-status">Active</span>
                    </div>
                    <div class="server africa">
                        <span class="server-location">South Africa, Johannesburg</span>
                        <span class="server-status">Active</span>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(map_path, 'w') as f:
            f.write(html_content)
            print(f"Created placeholder map: {map_path}")


def main():
    """Main function"""
    # Create assets and maps directories if they don't exist
    create_assets_directory()
    create_maps_directory()
    
    # Create and start application
    app = QApplication(sys.argv)
    app.setApplicationName("AniData VPN")
    app.setApplicationVersion("1.0.0")
    
    # Check for admin privileges
    if not run_as_admin():
        # Show warning about admin privileges for full functionality
        warning_msg = QMessageBox()
        warning_msg.setIcon(QMessageBox.Warning)
        warning_msg.setWindowTitle("Droits limités")
        warning_msg.setText("AniData VPN s'exécute sans droits administrateur.")
        warning_msg.setInformativeText("Certaines fonctionnalités comme la création d'interfaces VPN "
                                      "pourraient ne pas fonctionner correctement.\n\n"
                                      "Pour une fonctionnalité complète, exécutez l'application avec 'sudo'.")
        warning_msg.setStandardButtons(QMessageBox.Ok)
        warning_msg.exec_()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()