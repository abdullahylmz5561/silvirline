"""
core/assistant_bridge.py
==========================
Sesli yapay zeka asistanı için hazırlanmış BAĞLANTI KATMANI.

Şu an hiçbir konuşma tanıma / NLU motoru içermiyor - amacı, o motor
eklendiğinde geri kalan hiçbir şeyin (arayüz, seri haberleşme,
fırın mantığı) değişmesine gerek kalmayacak şekilde temiz bir sınır
çizmek.

İleride yapılacaklar (bu dosyanın dışında, ayrı bir modülde):
  1. Bir mikrofon/wake-word dinleyici (ör. Porcupine, Vosk, whisper.cpp)
     `listening_started` / `listening_stopped` sinyallerini tetikler.
  2. Konuşma metne çevrilip bir niyet (intent) çözümleyiciye verilir.
  3. Çözümlenen niyet, aşağıdaki `handle_intent()` metoduna iletilir.
     Bu metot da OvenController üzerinden fırını yönetir - yani sesli
     asistan, dokunmatik ekranla AYNI kontrol yolunu kullanır.

Örnek kullanım (gelecekte, gerçek motor bağlandığında):
    bridge.handle_intent("set_mode", {"mode": "PIZZA"})
    bridge.handle_intent("set_temperature", {"value": 200})
    bridge.handle_intent("start_cooking", {})
"""

from PyQt5.QtCore import QObject, pyqtSignal

import config
from core.oven_controller import OvenController


class AssistantBridge(QObject):
    listening_started = pyqtSignal()
    listening_stopped = pyqtSignal()
    wake_word_detected = pyqtSignal()
    command_recognized = pyqtSignal(str)     # ham metin (loglama/hata ayıklama için)
    intent_handled = pyqtSignal(str, dict)   # (intent_adı, parametreler)
    assistant_unavailable = pyqtSignal(str)  # kullanıcıya gösterilecek mesaj

    def __init__(self, oven_controller: OvenController, parent=None):
        super().__init__(parent)
        self.controller = oven_controller
        self.enabled = config.ASSISTANT_ENABLED
        self._listening = False

        # Niyet adı -> işleyici fonksiyon eşlemesi.
        # Yeni bir sesli komut eklemek için buraya tek satır yeterli.
        self._intent_handlers = {
            "set_mode": self._handle_set_mode,
            "set_temperature": self._handle_set_temperature,
            "adjust_temperature": self._handle_adjust_temperature,
            "start_cooking": lambda p: self.controller.start(),
            "stop_cooking": lambda p: self.controller.stop(),
            "set_timer": self._handle_set_timer,
        }

    # ------------------------------------------------------------------
    def toggle_listening(self):
        """Nav rail'deki mikrofon düğmesine basıldığında çağrılır."""
        if not self.enabled:
            self.assistant_unavailable.emit(
                "Sesli asistan henüz etkin değil. config.ASSISTANT_ENABLED = True "
                "yapıp bir konuşma tanıma motoru bağlandığında kullanılabilir olacak."
            )
            return
        self._listening = not self._listening
        (self.listening_started if self._listening else self.listening_stopped).emit()

    # ------------------------------------------------------------------
    def handle_intent(self, intent_name: str, params: dict):
        """Konuşma tanıma / NLU katmanının çağıracağı tek giriş noktası."""
        handler = self._intent_handlers.get(intent_name)
        if handler is None:
            return
        handler(params or {})
        self.intent_handled.emit(intent_name, params or {})

    # ------------------------------------------------------------------
    def _handle_set_mode(self, params):
        mode = params.get("mode")
        if mode:
            self.controller.set_mode(mode)

    def _handle_set_temperature(self, params):
        value = params.get("value")
        if value is not None:
            self.controller.set_target_temp(int(value))

    def _handle_adjust_temperature(self, params):
        delta = params.get("delta", 0)
        self.controller.adjust_temp(int(delta))

    def _handle_set_timer(self, params):
        minutes = params.get("minutes")
        if minutes is not None:
            self.controller.set_timer(int(minutes) * 60)
