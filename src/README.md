# Rota Analizi ve Yakıt Tüketimi Hesaplama Sistemi v2.0

## 🆕 Yeni Özellikler (v2.0)

### Detaylı İstanbul Trafik Veritabanı
- **19 Farklı Trafik Bölgesi:** Gerçek İstanbul yolları, köprüleri, tünelleri
- **Geçiş Ücretleri:** Köprü ve tünel ücretleri otomatik hesaplanır
- **Dinamik Trafik:** Saat bazlı otomatik peak/offpeak tespiti
- **Gerçekçi Hız Profilleri:** Her bölge için ayrı hız değerleri

### Akıllı Rota Analizi
- Koordinat bazlı otomatik bölge tespiti
- Boğaz geçişlerini tanıma (köprü/tünel seçimi)
- Segment bazlı detaylı yakıt hesaplama
- CO2 emisyon hesaplama (LPG dahil)

## 📁 Modüler Yapı

### 1. `database.py` - Gelişmiş Veritabanı Modülü
- **İçerik:** 
  - 12 araç modeli
  - 19 detaylı trafik bölgesi
  - Güncel yakıt fiyatları (Benzin, Dizel, LPG)
  - Yoğun saat tanımlamaları
- **Yeni Fonksiyonlar:**
  - `find_zone_by_keyword()`: Anahtar kelime ile bölge bulma
  - `is_peak_hour()`: Otomatik yoğun saat tespiti
  - `calculate_toll_cost()`: Geçiş ücreti hesaplama
  - `get_all_traffic_zones()`: Tüm bölgeleri listele

### 2. `calculations.py` - Geliştirilmiş Hesaplama Modülü
- **Sınıflar:**
  - `RouteSegmentAnalyzer`: Akıllı segment analizi
  - `FuelConsumptionCalculator`: Detaylı yakıt hesaplama
- **Yeni Özellikler:**
  - Koordinat bazlı bölge tespiti
  - Yol tipi bazlı yakıt hesaplama
  - Şehir içi dur-kalk faktörü
  - LPG emisyon hesaplama

### 3. `visualization.py` - Görselleştirme Modülü
- **Özellikler:**
  - Geçiş ücretlerini gösterme
  - Detaylı bölge istatistikleri
  - Toplam maliyet hesaplama
  - Zenginleştirilmiş grafikler

### 4. `main.py` - Ana Program
- Otomatik saat bazlı trafik durumu
- Yakıt fiyatları gösterimi
- Gelişmiş raporlama

## 🚀 Kurulum

### Gereksinimler
```bash
pip install requests numpy matplotlib
```

### API Anahtarı
Google Maps API anahtarı gereklidir:
- Directions API
- Elevation API

## 💻 Kullanım

### Basit Kullanım
```python
from visualization import RouteElevationAnalyzer
from datetime import datetime
from database import is_peak_hour

# API anahtarı ile analyzer oluştur
analyzer = RouteElevationAnalyzer("YOUR_API_KEY")

# Otomatik peak/offpeak tespiti
current_hour = datetime.now().hour
time_of_day = 'peak' if is_peak_hour(current_hour) else 'offpeak'

# Rota analizi
results = analyzer.analyze_route("Taksim", "Kadıköy")

# Görselleştirme
analyzer.visualize_route_with_fuel(
    results, 
    "Fiat Egea 1.3 Multijet",
    time_of_day,
    route_info=results
)
```

### Ana Programı Çalıştırma
```bash
python main.py
```

## 📊 Özellikler

### İstanbul Trafik Bölgeleri

#### Köprü ve Tüneller (Ücretli)
- **Avrasya Tüneli:** 145 TL
- **15 Temmuz Köprüsü:** 52 TL
- **FSM Köprüsü:** 52 TL
- **YSS Köprüsü:** 94 TL
- **Kuzey Marmara Otoyolu:** 0.48 TL/km

#### Ana Arterler
- TEM Otoyolu (O-1/O-2)
- D-100/E-5 Karayolu
- Bağdat Caddesi
- Barbaros Bulvarı
- Sahil Yolları

#### Şehir İçi Bölgeler
- Taksim-Şişli
- Kadıköy Merkez
- Üsküdar-Ümraniye

### Hesaplamalar
- **Akıllı Segment Analizi:** Koordinat bazlı bölge tespiti
- **Dinamik Yakıt Hesaplama:** Hız, eğim, trafik ve yol tipi faktörleri
- **Maliyet Analizi:** Yakıt + geçiş ücretleri
- **Emisyon Hesaplama:** Benzin, Dizel, LPG için CO2 tahmini

### Görselleştirmeler
1. **Rota Haritası:** Bölgeler ve eğimler vurgulanmış
2. **Yükseklik Profili:** Min/max noktaları
3. **Eğim Analizi:** Kritik bölgeler
4. **Segment Analizi:** Bölge bazlı yakıt tüketimi
5. **Maliyet Özeti:** Yakıt + geçiş ücretleri

## 🔧 Özelleştirme

### Yeni Trafik Bölgesi Ekleme
```python
TRAFFIC_ZONES['Yeni_Bolge'] = {
    'name': 'Bölge Adı',
    'avg_speed_peak': 30,
    'avg_speed_offpeak': 60,
    'traffic_multiplier': 1.5,
    'toll': False,
    'road_type': 'Cadde',
    'keywords': ['anahtar', 'kelimeler']
}
```

### Geçiş Ücreti Güncelleme
```python
TRAFFIC_ZONES['Avrasya_Tuneli']['toll_price'] = 150  # Yeni ücret
```

## 📈 Çıktılar

- `rota_analizi.png` - Detaylı rota analiz grafiği
- `arac_karsilastirma.png` - Araç karşılaştırması

## ⚠️ Önemli Notlar

- API anahtarını güvenli saklayın
- Google Maps API limitlerini kontrol edin
- Yakıt fiyatlarını düzenli güncelleyin
- Geçiş ücretleri 2024 Ekim tarifelerine göredir
- Gerçek yakıt tüketimi sürüş stiline bağlı değişir

## 📊 Performans İpuçları

- Yoğun saatlerde (07-10, 17-20) %30-50 daha fazla yakıt tüketimi
- Köprü geçişlerinde alternatif rotaları değerlendirin
- Şehir içi kısa mesafelerde dur-kalk faktörü yüksektir

## 📝 Lisans

Eğitim amaçlı geliştirilmiştir.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Yeni özellik ekleyin (`feature/YeniOzellik`)
3. Test edin
4. Pull request gönderin

## 📧 İletişim

Sorularınız için issue açabilirsiniz.