# admin/tabs/system_stats_tab.py

import psutil
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QGridLayout
from PyQt6.QtCore import QTimer

class SystemStatsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # Update every second

    def init_ui(self):
        layout = QVBoxLayout(self)
        grid_layout = QGridLayout()

        self.cpu_label = QLabel("CPU Usage:")
        self.cpu_bar = QProgressBar()
        grid_layout.addWidget(self.cpu_label, 0, 0)
        grid_layout.addWidget(self.cpu_bar, 0, 1)

        self.mem_label = QLabel("Memory Usage:")
        self.mem_bar = QProgressBar()
        grid_layout.addWidget(self.mem_label, 1, 0)
        grid_layout.addWidget(self.mem_bar, 1, 1)

        layout.addLayout(grid_layout)
        self.setLayout(layout)

    def update_stats(self):
        cpu_percent = psutil.cpu_percent()
        mem_percent = psutil.virtual_memory().percent

        self.cpu_bar.setValue(int(cpu_percent))
        self.cpu_label.setText(f"CPU Usage: {cpu_percent}%")

        self.mem_bar.setValue(int(mem_percent))
        self.mem_label.setText(f"Memory Usage: {mem_percent}%")