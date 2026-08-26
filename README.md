# SILVERLINE Akıllı Fırın Arayüzü

Jetson TX2 üzerinde çalışan, 800×480 dokunmatik panel için PyQt5 ile
yazılmış tam ekran fırın kontrol arayüzü.

## Kurulum

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Jetson TX2 (JetPack) üzerinde PyQt5'i pip yerine apt ile kurmak genelde
daha sorunsuzdur:

```bash
sudo apt install python3-pyqt5 python3-serial
```

## Çalıştırma

```bash
python3 main.py
```

- **Geliştirme (PC'de, donanım yokken):** `config.py` içinde
  `DEBUG_MODE = True` olarak kalsın. Uygulama 800×480 boyutunda normal bir
  pencere olarak açılır, fare ile kullanılabilir ve seri port bulunamazsa
  otomatik olarak **simülasyon moduna** geçip gerçekçi sahte sıcaklık
  telemetrisi üretir.
- **Gerçek donanım (Jetson TX2 + dokunmatik panel):** `DEBUG_MODE = False`
  yapın. Uygulama tam ekran, çerçevesiz ve imleç gizli şekilde açılır.
- **Çıkış:** Her iki modda da **ESC** tuşu uygulamayı kapatır
  (açılış animasyonu dahil).

## Klasör yapısı

```
main.py                    Giriş noktası, splash -> ana pencere geçişi
config.py                  Tüm ayarlar (ekran, seri port, sıcaklık sınırları)

core/
  oven_controller.py       Fırının tek durum kaynağı. UI ve sesli asistan
                            fırını HER ZAMAN bu sınıf üzerinden yönetir.
  serial_comm.py           Kontrol kartıyla UART haberleşmesi + simülasyon
  assistant_bridge.py      Sesli asistan için hazır bağlantı katmanı (iskelet)

ui/
  main_window.py           Ana pencere, nav rail + ekran yığını, ESC/tam ekran
  nav_rail.py               Sol menü (Ana Ekran / Tarifler / Zamanlayıcı / Ayarlar / Mikrofon)
  splash_screen.py         "SILVERLINE" açılış animasyonu
  icons.py                 QPainter ile çizilen fırın piktogramları ve menü ikonları
  widgets/temp_dial.py     Dairesel sıcaklık kadranı
  views/
    home_view.py           Ana ekran: kadran + fırın fonksiyonları ızgarası
    recipes_view.py        Tarif kütüphanesi (kategori filtreli)
    timer_view.py          Bağımsız zamanlayıcı
    settings_view.py       Cihaz ayarları + seri bağlantı durumu

styles/theme.qss           Koyu grafit + kor/amber tema
```

## Seri haberleşme protokolü

Basit, satır bazlı (`\n` ile biten) metin protokolü. Kontrol kartı
firmware'inde aynı komutları uygulamanız yeterli:

**Jetson → Kart**
| Komut | Açıklama |
|---|---|
| `MODE:<AD>` | örn. `MODE:ALT_UST_FAN` |
| `SETTEMP:<int>` | Hedef sıcaklık (°C) |
| `SETTIMER:<saniye>` | Zamanlayıcı süresi |
| `START` | Pişirmeyi başlat |
| `STOP` | Pişirmeyi durdur |

**Kart → Jetson**
| Mesaj | Açıklama |
|---|---|
| `TEMP:<int>` | Anlık iç sıcaklık |
| `DOOR:<0/1>` | Kapı durumu (1 = açık) |
| `STATUS:<IDLE\|HEATING\|READY\|ERROR>` | Fırın durumu |

Port `config.py` içinde `SERIAL_PORT` ile ayarlanır (Jetson TX2'nin
donanımsal UART'ı için varsayılan `/dev/ttyTHS1`; USB-seri çevirici
kullanıyorsanız `/dev/ttyUSB0` yapın). Kart bağlı değilse ve
`SERIAL_AUTO_SIMULATE = True` ise arayüz otomatik olarak simülasyon
moduna düşer — donanım gelmeden geliştirmeye devam edebilirsiniz.

## Sesli asistan için hazır altyapı

`core/assistant_bridge.py`, ileride eklenecek bir konuşma tanıma /
NLU motoru için temiz bir sınır tanımlar:

```python
bridge.handle_intent("set_mode", {"mode": "PIZZA"})
bridge.handle_intent("set_temperature", {"value": 200})
bridge.handle_intent("start_cooking", {})
```

Bu metodlar, dokunmatik ekranın kullandığı **aynı** `OvenController`
üzerinden fırını yönetir — yani sesli asistan geldiğinde arayüzde veya
seri haberleşmede hiçbir değişiklik yapmanız gerekmez, sadece konuşmayı
bir niyete (`intent`) çevirip `handle_intent()`'e vermeniz yeterli olur.
Sol menüdeki mikrofon simgesi zaten bu köprüye bağlı; `config.ASSISTANT_ENABLED`
`True` olana kadar "henüz etkin değil" mesajı gösterir.

## Notlar / sonraki adımlar

- Fırın fonksiyon ikonları (`ui/icons.py`) dosya kullanmadan, koddan
  QPainter ile çizilir — Jetson'a dağıtımda eksik asset dosyası riski
  yoktur ve gerçek fırın piktogramlarıyla (alt çizgi, üst-alt çizgi,
  fan, zigzag ızgara) birebir aynı mantığı kullanır.
- `ui/main_window.py`'deki ESC davranışı hem splash ekranında hem ana
  pencerede aktiftir.
- Gerçek kartla test ederken `STATUS:ERROR` gibi hata durumlarını
  arayüzde göstermek isterseniz `OvenController.status_changed`
  sinyaline bir dinleyici eklemeniz yeterli (şu an sadece loglanıyor).
