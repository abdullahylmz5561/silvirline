"""
ui/nav_rail.py
================
Ekranın solundaki sabit menü şeridi: Ana Ekran, Tarifler, Zamanlayıcı,
Ayarlar ve (ileride etkinleşecek) sesli asistan mikrofon düğmesi.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QButtonGroup
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QDateTime

from ui.icons import NavIcon


class NavRail(QWidget):
    view_requested = pyqtSignal(str)
    mic_pressed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navRail")
        self.setFixedWidth(76)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 14, 0, 14)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignHCenter)

        self.clock_label = QLabel("--:--")
        self.clock_label.setProperty("class", "dim")
        self.clock_label.setStyleSheet("font-family:'JetBrains Mono'; font-size:12px;")
        self.clock_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.clock_label)
        layout.addSpacing(8)

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)

        self._add_nav_btn(layout, "home", "home", "Ana Ekran", checked=True)
        self._add_nav_btn(layout, "recipes", "recipes", "Tarifler")
        self._add_nav_btn(layout, "timer", "timer", "Zamanlayıcı")
        self._add_nav_btn(layout, "settings", "settings", "Ayarlar")

        layout.addStretch(1)

        mic_btn = QPushButton()
        mic_btn.setObjectName("micBtn")
        mic_btn.setFixedSize(52, 52)
        mic_btn.setCursor(Qt.PointingHandCursor)
        mic_btn.setStyleSheet(
            "QPushButton{background:#2a2724; border:1px solid #3a3532; border-radius:26px;}"
            "QPushButton:pressed{background:#3a4750;}"
        )
        mic_icon = NavIcon("mic", 20)
        mic_layout = QVBoxLayout(mic_btn)
        mic_layout.setContentsMargins(0, 0, 0, 0)
        mic_layout.addWidget(mic_icon, alignment=Qt.AlignCenter)
        mic_btn.clicked.connect(self.mic_pressed.emit)
        layout.addWidget(mic_btn, alignment=Qt.AlignHCenter)
        layout.addSpacing(4)

        timer = QTimer(self)
        timer.timeout.connect(self._tick_clock)
        timer.start(15000)
        self._tick_clock()

    def _add_nav_btn(self, layout, view_key, icon_kind, tooltip, checked=False):
        btn = QPushButton()
        btn.setObjectName(f"nav_{view_key}")
        btn.setProperty("class", "navBtn")
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setFixedSize(52, 52)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        icon = NavIcon(icon_kind, 22)
        inner = QVBoxLayout(btn)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.addWidget(icon, alignment=Qt.AlignCenter)
        btn.clicked.connect(lambda: self.view_requested.emit(view_key))
        self.group.addButton(btn)
        layout.addWidget(btn, alignment=Qt.AlignHCenter)

    def _tick_clock(self):
        self.clock_label.setText(QDateTime.currentDateTime().toString("HH:mm"))

    def set_active(self, view_key: str):
        btn = self.findChild(QPushButton, f"nav_{view_key}")
        if btn:
            btn.setChecked(True)
