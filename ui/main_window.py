"""
ui/main_window.py
====================
Uygulamanın ana penceresi. Sol tarafta NavRail, sağ tarafta QStackedWidget
içinde dört ekran (Ana Ekran, Tarifler, Zamanlayıcı, Ayarlar).

Kiosk davranışı:
  - ESC tuşu -> uygulamayı kapatır (config.DEBUG_MODE farketmeksizin).
  - config.DEBUG_MODE = False iken tam ekran + çerçevesiz + imleç gizli.
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PyQt5.QtCore import Qt

import config
from core.oven_controller import OvenController
from core.assistant_bridge import AssistantBridge
from ui.nav_rail import NavRail
from ui.views.home_view import HomeView
from ui.views.recipes_view import RecipesView
from ui.views.timer_view import TimerView
from ui.views.settings_view import SettingsView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SILVERLINE Akıllı Fırın")

        if config.DEBUG_MODE:
            self.setFixedSize(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setCursor(Qt.BlankCursor)

        self.controller = OvenController()
        self.assistant = AssistantBridge(self.controller)

        root = QWidget()
        root.setObjectName("root")
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setCentralWidget(root)

        self.nav = NavRail()
        self.nav.view_requested.connect(self._show_view)
        self.nav.mic_pressed.connect(self.assistant.toggle_listening)
        layout.addWidget(self.nav)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, stretch=1)

        self.views = {
            "home": HomeView(self.controller),
            "recipes": RecipesView(self.controller),
            "timer": TimerView(self.controller),
            "settings": SettingsView(self.controller),
        }
        for view in self.views.values():
            self.stack.addWidget(view)

        # Tarif seçilince otomatik ana ekrana dön
        self.views["recipes"].recipe_applied.connect(lambda: self._show_view("home"))

        self.assistant.assistant_unavailable.connect(self._on_assistant_unavailable)

        self._show_view("home")

    def _show_view(self, key):
        self.stack.setCurrentWidget(self.views[key])
        self.nav.set_active(key)

    def _on_assistant_unavailable(self, message):
        # Şimdilik konsola yazıyoruz; ileride bir toast/banner ile
        # kullanıcıya ekranda da gösterilebilir.
        print(f"[Sesli Asistan] {message}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close_app()
        else:
            super().keyPressEvent(event)

    def close_app(self):
        self.controller.shutdown()
        from PyQt5.QtWidgets import QApplication
        QApplication.instance().quit()

    def closeEvent(self, event):
        self.controller.shutdown()
        super().closeEvent(event)
