import sys
import os
import json
import time
from datetime import datetime, timedelta
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import QWebEngineView
from .bandwidth_graph import BandwidthGraph
import pyqtgraph as pg

# Lovable.ai inspired color scheme
COLORS = {
    'primary': '#6366F1',      # Indigo
    'secondary': '#A855F7',    # Purple
    'success': '#22C55E',      # Green
    'danger': '#EF4444',       # Red
    'warning': '#F59E0B',      # Amber
    'info': '#3B82F6',         # Blue
    'light': '#F3F4F6',        # Gray-100
    'dark': '#111827',         # Gray-900
    'white': '#FFFFFF',
    'background': '#F9FAFB',   # Gray-50
    'text': '#1F2937',         # Gray-800
}

class ModernButton(QPushButton):
    def __init__(self, text='', parent=None, color='primary'):
        super().__init__(text, parent)
        self.color = COLORS[color]
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(40)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {self.color}dd;
            }}
            QPushButton:pressed {{
                background-color: {self.color}aa;
            }}
        """)

class ModernCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 16px;
                border: 1px solid #E5E7EB;
            }
        """)

class ModernMapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.map_card = ModernCard()
        self.map_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 16px;
                border: 1px solid #E5E7EB;
            }
        """)
        self.map_layout = QVBoxLayout(self.map_card)
        
        self.web_view = QWebEngineView()
        self.map_layout.addWidget(self.web_view)
        
        layout.addWidget(self.map_card)

    def load_map(self, html_path):
        self.web_view.load(QUrl.fromLocalFile(html_path))

class ProtocolSelector(QWidget):
    protocol_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        
        self.protocol_label = QLabel("Protocol:")
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["WireGuard", "OpenVPN"])
        
        layout.addWidget(self.protocol_label)
        layout.addWidget(self.protocol_combo)
        
        self.protocol_combo.currentTextChanged.connect(
            lambda t: self.protocol_changed.emit(t.lower())
        )
        
        self.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                background: white;
            }
        """)

class ServerListWidget(QWidget):
    server_selected = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search servers...")
        self.search_box.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background: white;
            }
        """)
        
        self.server_list = QListWidget()
        self.server_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background: white;
                padding: 4px;
                margin-top: 8px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background: #EEF2FF;
                color: #6366F1;
            }
            QListWidget::item:hover {
                background: #F3F4F6;
            }
        """)
        
        layout.addWidget(self.search_box)
        layout.addWidget(self.server_list)
        
        self.search_box.textChanged.connect(self.filter_servers)
        self.server_list.itemClicked.connect(self.on_server_selected)
        
    def populate_servers(self, servers):
        self.servers = servers
        self.server_list.clear()
        for server in servers:
            protocols = ", ".join(p.upper() for p in server.get('protocols', []))
            item = QListWidgetItem(f"{server['country']} - {server['city']} ({protocols})")
            item.setData(Qt.UserRole, server)
            self.server_list.addItem(item)
            
    def filter_servers(self, text):
        for i in range(self.server_list.count()):
            item = self.server_list.item(i)
            server = item.data(Qt.UserRole)
            if text.lower() in server['country'].lower() or text.lower() in server['city'].lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
                
    def on_server_selected(self, item):
        server = item.data(Qt.UserRole)
        self.server_selected.emit(server)

class ModernConnectionWidget(QWidget):
    connect_clicked = Signal()
    disconnect_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        self.status_card = ModernCard()
        status_layout = QVBoxLayout(self.status_card)
        
        # Connection status
        self.status_label = QLabel("Not Connected")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #EF4444;
                padding: 8px;
                border-radius: 4px;
                background-color: #FEF2F2;
            }
        """)
        
        # Server info
        self.server_info = QLabel("No server selected")
        self.server_info.setStyleSheet("color: #6B7280;")
        
        # Connection time
        self.uptime_label = QLabel("Duration: --:--:--")
        self.uptime_label.setStyleSheet("color: #6B7280;")
        
        # Buttons
        button_layout = QHBoxLayout()
        self.connect_btn = ModernButton("Connect", color='success')
        self.disconnect_btn = ModernButton("Disconnect", color='danger')
        self.disconnect_btn.setEnabled(False)
        
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.disconnect_btn)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.server_info)
        status_layout.addWidget(self.uptime_label)
        status_layout.addLayout(button_layout)
        
        layout.addWidget(self.status_card)
        
        # Connect signals
        self.connect_btn.clicked.connect(self.connect_clicked.emit)
        self.disconnect_btn.clicked.connect(self.disconnect_clicked.emit)
        
    def update_status(self, connected, server=None, uptime=None):
        if connected and server:
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #22C55E;
                    padding: 8px;
                    border-radius: 4px;
                    background-color: #F0FDF4;
                }
            """)
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            
            # Only show city if it exists
            location = server['country']
            if server.get('city'):
                location += f" - {server['city']}"
            self.server_info.setText(f"Connected to {location}")
        else:
            self.status_label.setText("Not Connected")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #EF4444;
                    padding: 8px;
                    border-radius: 4px;
                    background-color: #FEF2F2;
                }
            """)
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.server_info.setText("Select a server to connect")
            
        if uptime and connected:
            self.uptime_label.setText(f"Duration: {uptime}")
        else:
            self.uptime_label.setText("Duration: --:--:--")

class ModernStatisticsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        self.stats_card = ModernCard()
        stats_layout = QGridLayout(self.stats_card)
        
        # Create stat widgets
        self.download_speed = self._create_stat_widget("Download", "0 MB/s", "↓")
        self.upload_speed = self._create_stat_widget("Upload", "0 MB/s", "↑")
        self.total_downloaded = self._create_stat_widget("Total Downloaded", "0 MB", "📥")
        self.total_uploaded = self._create_stat_widget("Total Uploaded", "0 MB", "📤")
        
        # Add to layout
        stats_layout.addWidget(self.download_speed, 0, 0)
        stats_layout.addWidget(self.upload_speed, 0, 1)
        stats_layout.addWidget(self.total_downloaded, 1, 0)
        stats_layout.addWidget(self.total_uploaded, 1, 1)
        
        layout.addWidget(self.stats_card)
        
    def _create_stat_widget(self, title, value, icon):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header = QLabel(f"{icon} {title}")
        header.setStyleSheet("color: #6B7280; font-size: 14px;")
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #111827; font-size: 18px; font-weight: bold;")
        
        layout.addWidget(header)
        layout.addWidget(value_label)
        
        return widget
        
    def update_statistics(self, download_speed, upload_speed, total_downloaded, total_uploaded):
        self.download_speed.findChild(QLabel, "", Qt.FindChildOption.FindChildrenRecursively).setText(download_speed)
        self.upload_speed.findChild(QLabel, "", Qt.FindChildOption.FindChildrenRecursively).setText(upload_speed)
        self.total_downloaded.findChild(QLabel, "", Qt.FindChildOption.FindChildrenRecursively).setText(total_downloaded)
        self.total_uploaded.findChild(QLabel, "", Qt.FindChildOption.FindChildrenRecursively).setText(total_uploaded)

class ModernSettingsWidget(QWidget):
    settings_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        self.settings_card = ModernCard()
        settings_layout = QVBoxLayout(self.settings_card)
        
        # Theme selection
        theme_group = QGroupBox("Theme")
        theme_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                margin-top: 1em;
                padding: 1em;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        
        theme_layout = QVBoxLayout(theme_group)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
        """)
        theme_layout.addWidget(self.theme_combo)
        
        # Auto-connect settings
        auto_connect_group = QGroupBox("Auto-connect")
        auto_connect_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                margin-top: 1em;
                padding-top: 1em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
        """)
        
        auto_connect_layout = QVBoxLayout(auto_connect_group)
        self.auto_connect_check = QCheckBox("Connect on startup")
        self.auto_connect_check.setStyleSheet("""
            QCheckBox {
                padding: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        auto_connect_layout.addWidget(self.auto_connect_check)
        
        # Add groups to layout
        settings_layout.addWidget(theme_group)
        settings_layout.addWidget(auto_connect_group)
        
        # Save button
        self.save_btn = ModernButton("Save Settings", color='primary')
        settings_layout.addWidget(self.save_btn)
        
        layout.addWidget(self.settings_card)
        
        # Connect signals
        self.save_btn.clicked.connect(self.save_settings)
        
    def save_settings(self):
        settings = {
            'theme': self.theme_combo.currentText().lower(),
            'auto_connect': self.auto_connect_check.isChecked()
        }
        self.settings_changed.emit(settings)

class ModernMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AniData VPN")
        self.setMinimumSize(1000, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Create left and right panels
        left_panel = QWidget()
        right_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        right_layout = QVBoxLayout(right_panel)
        
        # Create widgets
        self.map_widget = ModernMapWidget()
        self.server_list = ModernServerListWidget()
        self.protocol_selector = ProtocolSelector()
        self.connection_widget = ModernConnectionWidget()
        self.stats_widget = ModernStatisticsWidget()
        self.bandwidth_graph = BandwidthGraph()
        self.settings_widget = ModernSettingsWidget()
        
        # Add widgets to layouts
        left_layout.addWidget(self.map_widget, stretch=2)
        left_layout.addWidget(self.server_list, stretch=1)
        
        right_layout.addWidget(self.protocol_selector)
        right_layout.addWidget(self.connection_widget)
        right_layout.addWidget(self.stats_widget)
        right_layout.addWidget(self.bandwidth_graph)
        right_layout.addWidget(self.settings_widget)
        
        # Set panel sizes
        left_panel.setMinimumWidth(400)
        right_panel.setMinimumWidth(300)
        
        # Add panels to main layout
        layout.addWidget(left_panel, stretch=2)
        layout.addWidget(right_panel, stretch=1)
        
        # Apply modern styling to the main window
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
            }}
            QWidget {{
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
        """)
        
        # Create system tray icon
        self.create_tray_icon()
        
    def create_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # Create tray menu
        tray_menu = QMenu()
        connect_action = tray_menu.addAction("Connect")
        disconnect_action = tray_menu.addAction("Disconnect")
        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("Quit")
        
        # Connect actions
        connect_action.triggered.connect(self.connection_widget.connect_clicked.emit)
        disconnect_action.triggered.connect(self.connection_widget.disconnect_clicked.emit)
        quit_action.triggered.connect(self.close)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide style
    app.setStyle("Fusion")
    
    window = ModernMainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()