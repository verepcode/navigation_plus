# Rota Analizi ve Yakıt Tüketimi Hesaplama Sistemi

## 📁 Modüler Yapı

Proje 3 ana modülden oluşmaktadır:

### 1. `database.py` - Veritabanı Modülü
- **İçerik:** Araç veritabanı, trafik bölge verileri, yakıt fiyatları
- **Fonksiyonlar:**
  - `get_vehicle_specs()`: Belirli bir aracın özelliklerini getirir
  - `get_all_vehicles()`: Tüm araçların listesini döndürür
  - `get_traffic_zone()`: Trafik bölgesi verilerini getirir
  - `get_fuel_price()`: Yakıt fiyatlarını döndürür

### 2. `calculations.py` - Hesaplama Modülü
- **Sınıflar:**
  - `RouteSegmentAnalyzer`: Rota segmentlerini analiz eder
  - `FuelConsumptionCalculator`: Yakıt tüketimi hesaplamaları yapar
- **Özellikler:**
  - Segment bazlı rota analizi
  - Eğim faktörlü yakıt hesaplama
  - Araç yetenek değerlendirmesi
  - CO2 emisyon hesaplama

### 3. `visualization.py` - Görselleştirme Modülü
- **Sınıf:** `RouteElevationAnalyzer`
- **Özellikler:**
  - Google Maps API entegrasyonu
  - Rota ve yükseklik profili analizi
  - Detaylı grafik oluşturma
  - Araç karşılaştırma raporları

### 4. `main.py` - Ana Program
- Modülleri bir araya getiren ana uygulama
- Örnek kullanım senaryosu
- Kullanıcı arayüzü

## 🚀 Kurulum

### Gereksinimler
```bash
pip install requests numpy matplotlib
```

### API Anahtarı
Google Maps API anahtarı gereklidir. Aşağıdaki API'ler aktif olmalıdır:
- Directions API
- Elevation API

## 💻 Kullanım

### Basit Kullanım
```python
from visualization import RouteElevationAnalyzer

# API anahtarı ile analyzer oluştur
analyzer = RouteElevationAnalyzer("YOUR_API_KEY")

# Rota analizi
results = analyzer.analyze_route("Başlangıç", "Bitiş")

# Görselleştirme
analyzer.visualize_route_with_fuel(results, "Fiat Egea 1.3 Multijet")
```

### Ana Programı Çalıştırma
```bash
python main.py
```

## 📊 Özellikler

### Veritabanı
- 12 farklı araç modeli
- 4 trafik bölgesi profili
- Güncel yakıt fiyatları

### Hesaplamalar
- **Segment Bazlı Analiz:** Rota farklı bölgelere ayrılır
- **Dinamik Yakıt Hesaplama:** Hız, eğim ve trafik faktörleri
- **Performans Değerlendirme:** Araç yeteneği analizi
- **Emisyon Hesaplama:** CO2 salınımı tahmini

### Görselleştirmeler
1. **Rota Haritası:** Kritik eğim bölgeleri vurgulanmış
2. **Yükseklik Profili:** Min/max noktaları işaretli
3. **Eğim Analizi:** Tırmanış ve iniş bölgeleri
4. **Segment Analizi:** Bölge bazlı yakıt tüketimi
5. **Araç Karşılaştırması:** Tüm araçların performans analizi

## 🔧 Modülleri Özelleştirme

### Yeni Araç Ekleme
`database.py` dosyasında `VEHICLE_DATABASE` sözlüğüne yeni araç ekleyin:
```python
"Araç Adı": {
    "hp": 100,
    "torque_nm": 200,
    "weight_kg": 1200,
    "fuel_consumption_city": 5.0,
    "fuel_consumption_highway": 4.0,
    "fuel_type": "Benzin",
    "engine_cc": 1400
}
```

### Trafik Bölgesi Ekleme
`database.py` dosyasında `TRAFFIC_ZONES` sözlüğüne yeni bölge ekleyin:
```python
'YeniBolge': {
    'avg_speed_peak': 35,
    'avg_speed_offpeak': 65,
    'traffic_multiplier': 1.5,
    'keywords': ['anahtar', 'kelimeler']
}
```

### Hesaplama Algoritması Özelleştirme
`calculations.py` dosyasında `FuelConsumptionCalculator` sınıfının metodlarını düzenleyin.

## 📈 Çıktılar

Program aşağıdaki dosyaları oluşturur:
- `rota_analizi.png` - Detaylı rota analiz grafiği
- `arac_karsilastirma.png` - Tüm araçların karşılaştırması

## ⚠️ Önemli Notlar

- API anahtarını güvenli şekilde saklayın (environment variable kullanın)
- Google Maps API kullanım limitlerine dikkat edin
- Yakıt fiyatlarını düzenli güncelleyin
- Gerçek yakıt tüketimi birçok faktöre bağlı olarak değişebilir

## 📝 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Yeni özellik ekleyin
3. Test edin
4. Pull request gönderin

## 📧 İletişim

Sorularınız için issue açabilirsiniz.