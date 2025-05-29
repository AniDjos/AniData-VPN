import os
import sys
import json
from PySide6.QtCore import QObject, Signal
from . import main
from .modern_ui import ModernMainWindow, COLORS

# Ensure the project root is in Python path
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class VPNBridge(QObject):
    status_updated = Signal(bool, object, str)  # Changed dict to object to allow None
    statistics_updated = Signal(str, str, str, str)
    
    def __init__(self):
        super().__init__()
        try:
            from core.protocols.wireguard.wireguard import WireGuardManager
            home_dir = os.path.expanduser("~/.anidata")
            config_dir = os.path.join(home_dir, "config/wireguard")
            servers_file = os.path.join(home_dir, "servers/config.json")
            self.vpn_manager = WireGuardManager(config_dir=config_dir, servers_file=servers_file)
        except ImportError:
            self.vpn_manager = main.WireGuardManager()
        
        self.status_thread = None
        self.current_server = None
        self.servers = []
        self.settings = {}
        self.protocol = "wireguard"  # Default protocol
        
    def setup_modern_ui(self, window: ModernMainWindow):
        self.window = window
        
        # Connect signals from UI to logic
        self.window.server_list.server_selected.connect(self.on_server_selected)
        self.window.connection_widget.connect_clicked.connect(self.connect_vpn)
        self.window.connection_widget.disconnect_clicked.connect(self.disconnect_vpn)
        self.window.settings_widget.settings_changed.connect(self.save_settings)
        
        # Connect signals from logic to UI
        self.status_updated.connect(self.window.connection_widget.update_status)
        self.statistics_updated.connect(self.window.stats_widget.update_statistics)
        
        # Initialize status monitoring
        self.status_thread = main.VPNStatusThread(self.vpn_manager)
        self.status_thread.status_updated.connect(self.update_status)
        self.status_thread.start()
        
        # Load initial data
        self.load_servers()
        self.load_settings()
        
    def load_servers(self):
        """Load server data from configuration file"""
        try:
            self.servers = self.vpn_manager.servers
            if not self.servers:
                self.load_fallback_servers()
                return
                
            # Convert server format if needed
            formatted_servers = []
            for server in self.servers:
                formatted_server = {
                    'id': server.get('id', ''),
                    'country': server.get('country', 'Unknown'),
                    'city': server.get('city', ''),
                    'protocols': server.get('protocols', ['wireguard']),
                    'bandwidth': server.get('bandwidth', 0),
                    'status': server.get('status', 'active'),
                    'coordinates': server.get('coordinates', {'latitude': 0, 'longitude': 0}),
                    'capabilities': server.get('capabilities', {})
                }
                formatted_servers.append(formatted_server)
            
            self.servers = formatted_servers
            self.window.server_list.populate_servers(self.servers)
            
        except Exception as e:
            print(f"Error loading server data: {str(e)}")
            self.load_fallback_servers()
            
    def load_fallback_servers(self):
        """Load fallback server data for demo purposes"""
        servers = [
            {
                "id": "fr-01",
                "region": "Europe",
                "country": "France",
                "city": "Paris",
                "protocols": ["wireguard", "openvpn", "ikev2"],
                "capabilities": {
                    "vpn": True,
                    "proxy": True,
                    "tor": False
                }
            },
            {
                "id": "us-01",
                "region": "North America",
                "country": "United States",
                "city": "New York",
                "protocols": ["wireguard", "openvpn"],
                "capabilities": {
                    "vpn": True,
                    "proxy": True,
                    "tor": False
                }
            }
        ]
        self.window.server_list.populate_servers(servers)
        
    def load_settings(self):
        if hasattr(self, 'settings'):
            leak_protection = self.settings.get('leak_protection', {})
            theme = 'dark' if self.settings.get('dark_mode', False) else 'light'
            auto_connect = self.settings.get('auto_connect', False)
        else:
            theme = 'light'
            auto_connect = False
            
        self.window.settings_widget.theme_combo.setCurrentText(theme.capitalize())
        self.window.settings_widget.auto_connect_check.setChecked(auto_connect)
        self.apply_theme(theme)
        
    def save_settings(self, settings):
        main.save_settings(settings)
        self.apply_theme(settings['theme'])
        
    def apply_theme(self, theme):
        if theme == 'dark':
            COLORS.update({
                'background': '#1F2937',
                'text': '#F9FAFB',
                'light': '#374151',
            })
        else:
            COLORS.update({
                'background': '#F9FAFB',
                'text': '#1F2937',
                'light': '#F3F4F6',
            })
            
        self.window.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}
            QWidget {{
                color: {COLORS['text']};
            }}
        """)
        
    def on_server_selected(self, server):
        self.current_server = server
        self.window.connection_widget.server_info.setText(f"Selected: {server['country']} - {server['city']}")
        self.window.connection_widget.connect_btn.setEnabled(True)
        
    def connect_vpn(self):
        if not self.current_server:
            return
            
        try:
            # Configure connection based on selected protocol
            connection_config = {
                'server': self.current_server,
                'protocol': self.protocol,
                'port': 51820 if self.protocol == 'wireguard' else 1194,
            }
            
            self.vpn_manager.connect(connection_config)
            self.status_updated.emit(True, self.current_server, "00:00:00")
            
            # Start bandwidth monitoring
            if hasattr(self.window, 'bandwidth_graph'):
                self.window.bandwidth_graph.reset()
                self.window.bandwidth_graph.start_monitoring()
                
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.status_updated.emit(False, None, None)
            
    def disconnect_vpn(self):
        try:
            self.vpn_manager.disconnect()
            # Use dummy server object when disconnected
            self.status_updated.emit(False, {
                'country': 'Not Connected',
                'city': '',
                'id': '',
                'protocols': [],
                'capabilities': {}
            }, "00:00:00")
        except Exception as e:
            print(f"Failed to disconnect: {e}")
            
    def update_status(self, status):
        is_connected = status.get('connected', False)
        uptime = status.get('uptime', "00:00:00")
        stats = status.get('statistics', {})
        
        # Update bandwidth graph if available
        if hasattr(self.window, 'bandwidth_graph') and is_connected:
            download_speed = stats.get('download_speed', 0)
            upload_speed = stats.get('upload_speed', 0)
            self.window.bandwidth_graph.update_bandwidth(download_speed, upload_speed)
        
        # Create a dummy server object if not connected
        current_server = self.current_server if is_connected else {
            'country': 'Not Connected',
            'city': '',
            'id': '',
            'protocols': [],
            'capabilities': {}
        }
        
        self.status_updated.emit(is_connected, current_server, uptime)
        
        # Update statistics
        download_speed = f"{stats.get('download_speed', 0):.2f} MB/s"
        upload_speed = f"{stats.get('upload_speed', 0):.2f} MB/s"
        total_downloaded = f"{stats.get('total_downloaded', 0):.2f} MB"
        total_uploaded = f"{stats.get('total_uploaded', 0):.2f} MB"
        
        self.statistics_updated.emit(
            download_speed,
            upload_speed,
            total_downloaded,
            total_uploaded
        )
        
    def cleanup(self):
        if self.status_thread:
            self.status_thread.stop()
            self.status_thread.wait()

def run_modern_ui():
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = ModernMainWindow()
    
    bridge = VPNBridge()
    bridge.setup_modern_ui(window)
    
    window.show()
    result = app.exec_()
    
    bridge.cleanup()
    sys.exit(result)

if __name__ == '__main__':
    run_modern_ui()