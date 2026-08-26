"""
SILVERLINE Akıllı Fırın Arayüzü - Genel Ayarlar
=================================================
Jetson TX2 üzerinde 800x480 dokunmatik panel için hazırlanmıştır.
Geliştirme sırasında (Jetson takılı değilken) DEBUG_MODE = True yaparak
uygulamayı normal bir masaüstü penceresinde, seri haberleşme simülasyonuyla
çalıştırabilirsiniz.
"""

# --- Ekran ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

# True: pencereli (masaüstünde geliştirme), fare imleci görünür, seri port
#       bulunamazsa otomatik simülasyon moduna geçer.
# False: gerçek donanım (Jetson TX2) - tam ekran, imleç gizli, kiosk modu.
DEBUG_MODE = True

# --- Seri Haberleşme (fırın kontrol kartı ile) ---
SERIAL_PORT = "/dev/ttyTHS1"   # Jetson TX2 donanımsal UART. Gerekirse /dev/ttyUSB0 yapın.
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 1.0           # saniye
# Port açılamazsa (kart bağlı değilse) otomatik olarak simülasyon moduna düş.
SERIAL_AUTO_SIMULATE = True

# --- Sıcaklık sınırları ---
MIN_TEMP = 50
MAX_TEMP = 250
DEFAULT_TEMP = 180
TEMP_STEP = 10

# --- Açılış animasyonu ---
SPLASH_DURATION_MS = 2600
SPLASH_TEXT = "SILVERLINE"

# --- Sesli asistan alt yapısı (ileride etkinleştirilecek) ---
# Şimdilik pasif; core/assistant_bridge.py bu bayrağı okuyup
# gerçek bir konuşma tanıma motoru bağlanana kadar devre dışı kalır.
ASSISTANT_ENABLED = False
