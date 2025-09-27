# admin/tabs/system_stats_tab.py

import psutil
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout
from PyQt6.QtCore import QTimer
from collections import deque

class SystemStatsTab(QWidget):
    def __init__(self):
        super().__init__()
        # Set background to white for pyqtgraph plots
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        # Data stores
        self.cpu_data = deque(maxlen=60)
        self.mem_data = deque(maxlen=60)
        self.time_data = deque(maxlen=60)
        self.time_counter = 0

        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # Update every second

    def init_ui(self):
        layout = QVBoxLayout(self)
        grid_layout = QGridLayout()

        # CPU Plot
        self.cpu_plot = pg.PlotWidget(title="CPU Usage (%)")
        self.cpu_plot.setYRange(0, 100)
        self.cpu_curve = self.cpu_plot.plot(pen='b')
        grid_layout.addWidget(self.cpu_plot, 0, 0)

        # Memory Plot
        self.mem_plot = pg.PlotWidget(title="Memory Usage (%)")
        self.mem_plot.setYRange(0, 100)
        self.mem_curve = self.mem_plot.plot(pen='r')
        grid_layout.addWidget(self.mem_plot, 1, 0)

        layout.addLayout(grid_layout)
        self.setLayout(layout)

    def update_stats(self):
        # Get current stats
        cpu_percent = psutil.cpu_percent()
        mem_percent = psutil.virtual_memory().percent

        # Update data deques
        self.time_counter += 1
        self.time_data.append(self.time_counter)
        self.cpu_data.append(cpu_percent)
        self.mem_data.append(mem_percent)

        # Update plots
        self.cpu_curve.setData(list(self.time_data), list(self.cpu_data))
        self.mem_curve.setData(list(self.time_data), list(self.mem_data))