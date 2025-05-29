import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer
import pyqtgraph as pg
import numpy as np
from datetime import datetime

class BandwidthGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the plot widget
        self.graphWidget = pg.PlotWidget()
        layout.addWidget(self.graphWidget)
        
        # Configure graph appearance
        self.graphWidget.setBackground('white')
        self.graphWidget.showGrid(x=True, y=True, alpha=0.3)
        
        # Set up download and upload curves
        self.download_curve = self.graphWidget.plot(pen={'color': '#22C55E', 'width': 2}, name='Download')
        self.upload_curve = self.graphWidget.plot(pen={'color': '#EF4444', 'width': 2}, name='Upload')
        
        # Setup legend
        self.graphWidget.addLegend()
        
        # Setup data storage
        self.time_window = 60  # 60 seconds of data
        self.times = np.array([])
        self.download_data = np.array([])
        self.upload_data = np.array([])
        
        # Setup axes
        self.graphWidget.setLabel('left', 'Speed (MB/s)')
        self.graphWidget.setLabel('bottom', 'Time (s)')
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)  # Update every second
        
        # Start time
        self.start_time = datetime.now()
        
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
        
    def update_plot(self):
        if len(self.times) > 0:
            self.download_curve.setData(self.times, self.download_data)
            self.upload_curve.setData(self.times, self.upload_data)
            
            # Auto-scale Y axis if needed
            max_value = max(np.max(self.download_data) if len(self.download_data) > 0 else 0,
                          np.max(self.upload_data) if len(self.upload_data) > 0 else 0)
            if max_value > 0:
                self.graphWidget.setYRange(0, max_value * 1.1)
                
            # Set X axis range to show the time window
            current_time = (datetime.now() - self.start_time).total_seconds()
            self.graphWidget.setXRange(max(0, current_time - self.time_window), current_time)
            
    def reset(self):
        self.times = np.array([])
        self.download_data = np.array([])
        self.upload_data = np.array([])
        self.start_time = datetime.now()
        self.download_curve.setData([], [])
        self.upload_curve.setData([], [])

    def start_monitoring(self):
        self.timer.start()
        
    def stop_monitoring(self):
        self.timer.stop()

if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import random
    
    app = QApplication(sys.argv)
    graph = BandwidthGraph()
    graph.show()
    
    # Demo update
    def demo_update():
        download = random.uniform(0, 10)
        upload = random.uniform(0, 5)
        graph.update_bandwidth(download, upload)
    
    timer = QTimer()
    timer.timeout.connect(demo_update)
    timer.start(1000)
    
    sys.exit(app.exec_())