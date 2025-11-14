"""
Veritabanı Modülü - Araç ve Trafik Verileri
Bu modül tüm statik veri tanımlamalarını içerir.
"""

# Türkiye'de yaygın ekonomi sınıfı araçlar veritabanı
VEHICLE_DATABASE = {
    "Fiat Egea 1.3 Multijet": {
        "hp": 95,
        "torque_nm": 200,
        "weight_kg": 1185,
        "fuel_consumption_city": 4.9,
        "fuel_consumption_highway": 3.8,
        "fuel_type": "Dizel",
        "engine_cc": 1300
    },
    "Renault Clio 1.0 TCe": {
        "hp": 100,
        "torque_nm": 160,
        "weight_kg": 1100,
        "fuel_consumption_city": 5.7,
        "fuel_consumption_highway": 4.2,
        "fuel_type": "Benzin",
        "engine_cc": 999
    },
    "Volkswagen Polo 1.0 TSI": {
        "hp": 95,
        "torque_nm": 175,
        "weight_kg": 1150,
        "fuel_consumption_city": 5.8,
        "fuel_consumption_highway": 4.3,
        "fuel_type": "Benzin",
        "engine_cc": 999
    },
    "Hyundai i20 1.4 CRDi": {
        "hp": 90,
        "torque_nm": 220,
        "weight_kg": 1120,
        "fuel_consumption_city": 4.7,
        "fuel_consumption_highway": 3.6,
        "fuel_type": "Dizel",
        "engine_cc": 1396
    },
    "Toyota Corolla 1.6": {
        "hp": 132,
        "torque_nm": 160,
        "weight_kg": 1300,
        "fuel_consumption_city": 6.4,
        "fuel_consumption_highway": 4.7,
        "fuel_type": "Benzin",
        "engine_cc": 1598
    },
    "Peugeot 301 1.5 BlueHDi": {
        "hp": 100,
        "torque_nm": 250,
        "weight_kg": 1170,
        "fuel_consumption_city": 4.5,
        "fuel_consumption_highway": 3.4,
        "fuel_type": "Dizel",
        "engine_cc": 1499
    },
    "Dacia Duster 1.5 dCi": {
        "hp": 115,
        "torque_nm": 260,
        "weight_kg": 1320,
        "fuel_consumption_city": 5.3,
        "fuel_consumption_highway": 4.1,
        "fuel_type": "Dizel",
        "engine_cc": 1461
    },
    "Ford Focus 1.5 TDCi": {
        "hp": 120,
        "torque_nm": 270,
        "weight_kg": 1350,
        "fuel_consumption_city": 4.8,
        "fuel_consumption_highway": 3.7,
        "fuel_type": "Dizel",
        "engine_cc": 1499
    },
    "Opel Astra 1.5 D": {
        "hp": 105,
        "torque_nm": 260,
        "weight_kg": 1320,
        "fuel_consumption_city": 4.9,
        "fuel_consumption_highway": 3.8,
        "fuel_type": "Dizel",
        "engine_cc": 1499
    },
    "Nissan Qashqai 1.3 DIG-T": {
        "hp": 140,
        "torque_nm": 240,
        "weight_kg": 1425,
        "fuel_consumption_city": 6.8,
        "fuel_consumption_highway": 5.0,
        "fuel_type": "Benzin",
        "engine_cc": 1332
    },
    "Skoda Octavia 1.6 TDI": {
        "hp": 115,
        "torque_nm": 250,
        "weight_kg": 1350,
        "fuel_consumption_city": 4.6,
        "fuel_consumption_highway": 3.5,
        "fuel_type": "Dizel",
        "engine_cc": 1598
    },
    "Seat Leon 1.0 TSI": {
        "hp": 110,
        "torque_nm": 200,
        "weight_kg": 1205,
        "fuel_consumption_city": 5.9,
        "fuel_consumption_highway": 4.4,
        "fuel_type": "Benzin",
        "engine_cc": 999
    }
}

# İstanbul'daki yollar ve trafik karakteristikleri - Gerçekçi ve Detaylı
TRAFFIC_ZONES = {
    # DEVLET OTOYOLLARI
    'O-1_O-2_Otoyol': {
        'name': 'O-1_O-2_Otoyol',
        'avg_speed_peak': 50,
        'avg_speed_offpeak': 95,
        'traffic_multiplier': 1.2,
        'toll': False,
        'road_type': 'Otoyol',
        'keywords': ['TEM', 'O-1', 'O-2', 'Trans Avrupa', 'Mahmutbey', 'Habipler']
    },
    
    'D100_E5': {
        'name': 'D100_E5',
        'avg_speed_peak': 25,
        'avg_speed_offpeak': 60,
        'traffic_multiplier': 1.8,
        'toll': False,
        'road_type': 'Ana Arter',
        'keywords': ['E5', 'D100', 'Londra Asfaltı', 'Bakırköy', 'Avcılar', 'Beylikdüzü']
    },
    
    # ÖZEL OTOYOLLAR (Ücretli)
    'Avrasya_Tuneli': {
        'name': 'Avrasya_Tuneli',
        'avg_speed_peak': 60,
        'avg_speed_offpeak': 70,
        'traffic_multiplier': 1.1,
        'toll': True,
        'toll_price': 145,
        'road_type': 'Tünel',
        'keywords': ['Avrasya', 'Tünel', 'Kazlıçeşme', 'Göztepe']
    },
    
    '15_Temmuz_Kopru': {
        'name': '15_Temmuz_Kopru',
        'avg_speed_peak': 35,
        'avg_speed_offpeak': 70,
        'traffic_multiplier': 1.5,
        'toll': True,
        'toll_price': 52,
        'road_type': 'Köprü',
        'keywords': ['15 Temmuz', 'Boğaziçi', 'Birinci Köprü', 'Ortaköy', 'Beylerbeyi']
    },
    
    'FSM_Kopru': {
        'name': 'FSM_Kopru',
        'avg_speed_peak': 40,
        'avg_speed_offpeak': 75,
        'traffic_multiplier': 1.4,
        'toll': True,
        'toll_price': 52,
        'road_type': 'Köprü',
        'keywords': ['FSM', 'Fatih Sultan', 'İkinci Köprü', 'Kavacık', 'Hisarüstü']
    },
    
    'YSS_Kopru': {
        'name': 'YSS_Kopru',
        'avg_speed_peak': 70,
        'avg_speed_offpeak': 100,
        'traffic_multiplier': 1.1,
        'toll': True,
        'toll_price': 94,
        'road_type': 'Köprü',
        'keywords': ['YSS', 'Yavuz Sultan', 'Üçüncü Köprü', 'Kuzey Marmara']
    },
    
    'Kuzey_Marmara_Otoyolu': {
        'name': 'Kuzey_Marmara_Otoyolu',
        'avg_speed_peak': 80,
        'avg_speed_offpeak': 110,
        'traffic_multiplier': 1.0,
        'toll': True,
        'toll_per_km': 0.48,
        'road_type': 'Otoyol',
        'keywords': ['Kuzey Marmara', 'O-7', 'Odayeri', 'Başakşehir', 'Kurtköy']
    },
    
    # ANA ARTERLER VE CADDELER
    'Bagdat_Caddesi': {
        'name': 'Bağdat Caddesi',
        'avg_speed_peak': 20,
        'avg_speed_offpeak': 45,
        'traffic_multiplier': 2.0,
        'toll': False,
        'road_type': 'Cadde',
        'keywords': ['Bağdat', 'Kadıköy', 'Bostancı', 'Suadiye', 'Caddebostan']
    },
    
    'Barbaros_Bulvari': {
        'name': 'Barbaros Bulvarı',
        'avg_speed_peak': 25,
        'avg_speed_offpeak': 50,
        'traffic_multiplier': 1.7,
        'toll': False,
        'road_type': 'Bulvar',
        'keywords': ['Barbaros', 'Beşiktaş', 'Zincirlikuyu', 'Levent', '4.Levent']
    },
    
    'Sahil_Yolu_Avrupa': {
        'name': 'Avrupa Yakası Sahil Yolu',
        'avg_speed_peak': 30,
        'avg_speed_offpeak': 55,
        'traffic_multiplier': 1.6,
        'toll': False,
        'road_type': 'Sahil Yolu',
        'keywords': ['Sahil', 'Florya', 'Yeşilköy', 'Bakırköy', 'Ataköy']
    },
    
    'Sahil_Yolu_Anadolu': {
        'name': 'Sahil_Yolu_Anadolu',
        'avg_speed_peak': 35,
        'avg_speed_offpeak': 60,
        'traffic_multiplier': 1.5,
        'toll': False,
        'road_type': 'Sahil Yolu',
        'keywords': ['Sahil', 'Kadıköy', 'Maltepe', 'Kartal', 'Pendik', 'Tuzla']
    },
    
    # BAĞLANTI YOLLARI
    'TEM_Baglanti': {
        'name': 'TEM_Baglanti',
        'avg_speed_peak': 35,
        'avg_speed_offpeak': 65,
        'traffic_multiplier': 1.5,
        'toll': False,
        'road_type': 'Bağlantı Yolu',
        'keywords': ['TEM Bağlantı', 'Kavacık', 'Ümraniye', 'Samandıra', 'Kayışdağı']
    },
    
    'Basin_Ekspres': {
        'name': 'Basın Ekspres Yolu',
        'avg_speed_peak': 40,
        'avg_speed_offpeak': 70,
        'traffic_multiplier': 1.4,
        'toll': False,
        'road_type': 'Ekspres Yol',
        'keywords': ['Basın Ekspres', 'İkitelli', 'Güneşli', 'Yenibosna']
    },
    
    # DIŞ BÖLGELER VE BANLIYÖLER
    'Beylikduzu_Buyukcekmece': {
        'name': 'Beylikdüzü-Büyükçekmece Bölgesi',
        'avg_speed_peak': 40,
        'avg_speed_offpeak': 65,
        'traffic_multiplier': 1.3,
        'toll': False,
        'road_type': 'Banliyö',
        'keywords': ['Beylikdüzü', 'Büyükçekmece', 'Esenyurt', 'Avcılar']
    },
    
    'Tuzla_Gebze': {
        'name': 'Tuzla-Gebze Bölgesi',
        'avg_speed_peak': 45,
        'avg_speed_offpeak': 70,
        'traffic_multiplier': 1.3,
        'toll': False,
        'road_type': 'Banliyö',
        'keywords': ['Tuzla', 'Gebze', 'Çayırova', 'Darıca', 'Şekerpınar']
    },
    
    'Sancaktepe_Sultanbeyli': {
        'name': 'Sancaktepe-Sultanbeyli Bölgesi',
        'avg_speed_peak': 35,
        'avg_speed_offpeak': 55,
        'traffic_multiplier': 1.4,
        'toll': False,
        'road_type': 'Banliyö',
        'keywords': ['Sancaktepe', 'Sultanbeyli', 'Samandıra', 'Sarıgazi']
    },
    
    # ŞEHİR İÇİ YOĞUN BÖLGELER
    'Taksim_Sisli': {
        'name': 'Taksim-Şişli Merkez',
        'avg_speed_peak': 15,
        'avg_speed_offpeak': 35,
        'traffic_multiplier': 2.2,
        'toll': False,
        'road_type': 'Şehir İçi',
        'keywords': ['Taksim', 'Şişli', 'Mecidiyeköy', 'Nişantaşı', 'Osmanbey']
    },
    
    'Kadikoy_Merkez': {
        'name': 'Kadıköy Merkez',
        'avg_speed_peak': 18,
        'avg_speed_offpeak': 40,
        'traffic_multiplier': 2.1,
        'toll': False,
        'road_type': 'Şehir İçi',
        'keywords': ['Kadıköy', 'Moda', 'Bahariye', 'Altıyol', 'Söğütlüçeşme']
    },
    
    'Uskudar_Umraniye': {
        'name': 'Üsküdar-Ümraniye Aksı',
        'avg_speed_peak': 22,
        'avg_speed_offpeak': 45,
        'traffic_multiplier': 1.9,
        'toll': False,
        'road_type': 'Şehir İçi',
        'keywords': ['Üsküdar', 'Ümraniye', 'Altunizade', 'Çamlıca', 'Acıbadem']
    },
    
    # ============================================
    # BEYKOZ BÖLGESİ - ÖZEL TANIMLAMALAR
    # ============================================
    
    # Beykoz Sahil Yolu (Düz, düşük eğimli)
    'Beykoz_Sahil': {
        'name': 'Beykoz Sahil Yolu',
        'avg_speed_peak': 35,
        'avg_speed_offpeak': 55,
        'traffic_multiplier': 1.4,
        'toll': False,
        'road_type': 'Sahil Yolu',
        'typical_slope': 2,  # %2 ortalama eğim (düşük)
        'elevation_range': (0, 20),  # Deniz seviyesi - 20m arası
        'keywords': ['Beykoz', 'Sahil', 'Paşabahçe', 'Çubuklu', 'Kanlıca', 'Anadolu Hisarı']
    },
    
    # Barbaros Caddesi (Beykoz) - Orta eğimli
    'Beykoz_Barbaros_Cad': {
        'name': 'Barbaros Caddesi (Beykoz)',
        'avg_speed_peak': 30,
        'avg_speed_offpeak': 50,
        'traffic_multiplier': 1.5,
        'toll': False,
        'road_type': 'Cadde',
        'typical_slope': 5,  # %5 ortalama eğim
        'elevation_range': (10, 80),  # 10m - 80m arası
        'keywords': ['Barbaros', 'Beykoz', 'Çubuklu', 'Sosyal Tesisler']
    },
    
    # Sümbül Sokak - Düşük eğimli
    'Beykoz_Sumbul_Sok': {
        'name': 'Sümbül Sokak',
        'avg_speed_peak': 25,
        'avg_speed_offpeak': 40,
        'traffic_multiplier': 1.3,
        'toll': False,
        'road_type': 'Sokak',
        'typical_slope': 4,  # %4 ortalama eğim
        'elevation_range': (60, 90),
        'keywords': ['Sümbül', 'Beykoz', 'Paşabahçe Mahallesi']
    },
    
    # Karanfil Sokak - Düşük eğimli
    'Beykoz_Karanfil_Sok': {
        'name': 'Karanfil Sokak',
        'avg_speed_peak': 25,
        'avg_speed_offpeak': 40,
        'traffic_multiplier': 1.3,
        'toll': False,
        'road_type': 'Sokak',
        'typical_slope': 3,  # %3 ortalama eğim
        'elevation_range': (70, 85),
        'keywords': ['Karanfil', 'Beykoz', 'Paşabahçe']
    },
    
    # Karagöz Sırtı Caddesi - Orta eğimli
    'Beykoz_Karagoz_Sirti': {
        'name': 'Karagöz Sırtı Caddesi',
        'avg_speed_peak': 30,
        'avg_speed_offpeak': 45,
        'traffic_multiplier': 1.4,
        'toll': False,
        'road_type': 'Cadde',
        'typical_slope': 6,  # %6 ortalama eğim
        'elevation_range': (70, 110),
        'keywords': ['Karagöz Sırtı', 'Beykoz', 'Çubuklu']
    },
    
    # Beykoz İç Yollar (Dik, kaçınılmalı)
    'Beykoz_Ic_Yollar_Dik': {
        'name': 'Beykoz İç Yolları (Dik Bölge)',
        'avg_speed_peak': 20,
        'avg_speed_offpeak': 35,
        'traffic_multiplier': 1.8,
        'toll': False,
        'road_type': 'Mahalle İçi',
        'typical_slope': 18,  # %18 ortalama eğim (KRİTİK!)
        'elevation_range': (20, 150),  # Büyük yükselti farkı
        'keywords': ['Beykoz', 'İç Yollar', 'Tepeüstü', 'Polonezköy Yolu']
    },
    
    # Beykoz Merkez - Orta yoğunluk
    'Beykoz_Merkez': {
        'name': 'Beykoz Merkez',
        'avg_speed_peak': 25,
        'avg_speed_offpeak': 45,
        'traffic_multiplier': 1.6,
        'toll': False,
        'road_type': 'Şehir İçi',
        'typical_slope': 7,
        'elevation_range': (30, 100),
        'keywords': ['Beykoz', 'Merkez', 'İskele', 'Çarşı']
    }
}

# Yakıt fiyatları (TL/Litre) - 2024 Ekim ortalama fiyatları
FUEL_PRICES = {
    'Benzin': 42.15,
    'Dizel': 43.25,
    'LPG': 24.85
}

# Trafik yoğunluğu saatleri
PEAK_HOURS = {
    'sabah': {'start': 7, 'end': 10},
    'aksam': {'start': 17, 'end': 20}
}

# ============================================
# YENİ: YOL AĞI CACHE YAPISI
# ============================================
ROAD_NETWORK_CACHE = {
    'nodes': {},      # {node_id: {gps, elevation, metadata}}
    'edges': [],      # [{from, to, distance, slope, direction, ...}]
    'last_update': None,
    'bbox': None      # Hangi bölge indirilmiş
}

# ============================================
# YENİ: GRAF YAPILANDIRMA
# ============================================
GRAPH_CONFIG = {
    'default_bbox': (41.10, 29.05, 41.15, 29.15),  # Beykoz
    'cache_duration': 7 * 24 * 3600,  # 7 gün (saniye)
    'elevation_batch_size': 512,
    'critical_slope_threshold': 15,  # %15 üzeri kritik
    'max_acceptable_slope': 12,  # %12 üzeri tercih edilmez
}

# ============================================
# YENİ: OPTİMİZASYON PROFİLLERİ
# ============================================
OPTIMIZATION_PROFILES = {
    'fuel_saver': {
        'name': 'Yakıt Tasarrufu',
        'weights': {
            'slope': 0.4,      # Eğim önemli (yakıt tüketimi için)
            'fuel': 0.5,       # Yakıt en önemli
            'time': 0.05,      # Zaman önemsiz
            'road': 0.05       # Yol tipi önemsiz
        },
        'description': 'En az yakıt tüketen rota'
    },
    'time_saver': {
        'name': 'Zaman Tasarrufu',
        'weights': {
            'slope': 0.2,      # Eğim daha az önemli
            'fuel': 0.1,       # Yakıt önemsiz
            'time': 0.6,       # Zaman en önemli
            'road': 0.1        # Yol tipi biraz önemli (hızlı yollar)
        },
        'description': 'En hızlı ulaşım sağlayan rota'
    },
    'safety_first': {
        'name': 'Güvenlik/Konfor Öncelikli',
        'weights': {
            'slope': 0.7,      # Eğim çok önemli (güvenlik için)
            'fuel': 0.1,       # Yakıt önemsiz
            'time': 0.1,       # Zaman önemsiz
            'road': 0.1        # Yol tipi biraz önemli
        },
        'description': 'En düşük eğimli, güvenli rota'
    },
    'balanced': {
        'name': 'Dengeli',
        'weights': {
            'slope': 0.4,      # Eğim önemli
            'fuel': 0.3,       # Yakıt önemli
            'time': 0.2,       # Zaman biraz önemli
            'road': 0.1        # Yol tipi az önemli
        },
        'description': 'Tüm kriterlerin dengeli kombinasyonu'
    }
}

# ============================================
# YENİ: BEYKOZ BÖLGE BİLGİLERİ
# ============================================
BEYKOZ_REGION = {
    'bbox': (41.10, 29.05, 41.15, 29.15),  # (min_lat, min_lon, max_lat, max_lon)
    'center': (41.1125, 29.10),
    'known_locations': {
        'Beykoz_Sosyal_Tesisleri': {
            'gps': (41.1133, 29.0877),
            'elevation': 5,  # metre (sahil seviyesi)
            'description': 'İBB Beykoz Sahil Sosyal Tesisleri',
            'address': 'Paşabahçe Mahallesi, Barbaros Caddesi, Burunbahçe Mevki'
        },
        'Karagoz_Sirti_Camii': {
            'gps': (41.1117, 29.0925),
            'elevation': 77,  # metre
            'description': 'Karagöz Sırtı Camii',
            'address': 'Karagöz Sırtı Caddesi'
        },
        'Pasabahce_Iskelesi': {
            'gps': (41.1145, 29.0885),
            'elevation': 0,  # deniz seviyesi
            'description': 'Paşabahçe İskelesi'
        },
        'Beykoz_Merkez': {
            'gps': (41.1155, 29.0965),
            'elevation': 35,
            'description': 'Beykoz Merkez/İskele'
        }
    },
    'safe_routes': {
        'coastal_path': {
            'description': 'Sahil yolu üzerinden (en düşük eğim)',
            'waypoints': ['Beykoz_Sosyal_Tesisleri', 'Barbaros_Cad', 'Karanfil_Sok', 'Karagoz_Sirti_Camii'],
            'avg_slope': 4,  # %4 ortalama
            'max_slope': 7   # %7 maksimum
        },
        'direct_steep': {
            'description': 'Direkt iç yollar (dik, önerilmez)',
            'waypoints': ['Beykoz_Sosyal_Tesisleri', 'Ic_Yollar', 'Karagoz_Sirti_Camii'],
            'avg_slope': 14,  # %14 ortalama
            'max_slope': 22   # %22 maksimum (KRİTİK!)
        }
    }
}


# ============================================
# FONKSİYONLAR
# ============================================

def get_vehicle_specs(vehicle_name):
    """
    Belirli bir aracın özelliklerini döndürür
    
    Args:
        vehicle_name (str): Araç adı
        
    Returns:
        dict: Araç özellikleri veya None
    """
    return VEHICLE_DATABASE.get(vehicle_name, None)


def get_all_vehicles():
    """
    Tüm araçların listesini döndürür
    
    Returns:
        list: Araç isimleri listesi
    """
    return list(VEHICLE_DATABASE.keys())


def get_traffic_zone(zone_name):
    """
    Belirli bir trafik bölgesinin verilerini döndürür
    
    Args:
        zone_name (str): Bölge adı
        
    Returns:
        dict: Bölge verileri veya None
    """
    return TRAFFIC_ZONES.get(zone_name, None)


def get_all_traffic_zones():
    """
    Tüm trafik bölgelerinin listesini döndürür
    
    Returns:
        list: Bölge isimleri listesi
    """
    return list(TRAFFIC_ZONES.keys())


def get_fuel_price(fuel_type):
    """
    Belirli bir yakıt tipinin fiyatını döndürür
    
    Args:
        fuel_type (str): Yakıt tipi (Benzin/Dizel/LPG)
        
    Returns:
        float: Yakıt fiyatı (TL/Litre)
    """
    return FUEL_PRICES.get(fuel_type, 0)


def find_zone_by_keyword(keyword):
    """
    Anahtar kelimeye göre trafik bölgesi bulur
    
    Args:
        keyword (str): Aranacak anahtar kelime
        
    Returns:
        tuple: (zone_key, zone_data) veya (None, None)
    """
    keyword_lower = keyword.lower()
    for zone_key, zone_data in TRAFFIC_ZONES.items():
        for kw in zone_data['keywords']:
            if keyword_lower in kw.lower():
                return zone_key, zone_data
    return None, None


def is_peak_hour(hour):
    """
    Verilen saatin yoğun trafik saati olup olmadığını kontrol eder
    
    Args:
        hour (int): Saat (0-23)
        
    Returns:
        bool: Yoğun saat ise True
    """
    for period in PEAK_HOURS.values():
        if period['start'] <= hour < period['end']:
            return True
    return False


def calculate_toll_cost(zones_used):
    """
    Kullanılan bölgelere göre toplam geçiş ücreti hesaplar
    
    Args:
        zones_used (list): Kullanılan bölgelerin listesi
        
    Returns:
        float: Toplam geçiş ücreti (TL)
    """
    total_toll = 0
    for zone_name in zones_used:
        zone = TRAFFIC_ZONES.get(zone_name, {})
        if zone.get('toll', False):
            if 'toll_price' in zone:
                total_toll += zone['toll_price']
            # toll_per_km varsa, mesafe bilgisi gerekir
            elif 'toll_per_km' in zone:
                total_toll += zone['toll_per_km'] * 20
    return total_toll


def find_zone_by_gps(lat, lon, max_distance_km=0.5):
    """
    GPS koordinatına göre en yakın trafik bölgesini bulur
    
    Args:
        lat (float): Enlem
        lon (float): Boylam
        max_distance_km (float): Maksimum arama mesafesi (km)
        
    Returns:
        tuple: (zone_key, zone_data, distance) veya (None, None, None)
    """
    from math import radians, cos, sin, asin, sqrt
    
    def haversine(lon1, lat1, lon2, lat2):
        """İki GPS noktası arası mesafe (km)"""
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return km
    
    # Beykoz bilinen lokasyonlarını kontrol et
    min_distance = float('inf')
    closest_zone = None
    
    for zone_key, zone_data in TRAFFIC_ZONES.items():
        # Beykoz bölge zonları için yaklaşık merkez noktaları
        if zone_key.startswith('Beykoz_'):
            # Elevation range'den ortalama bir merkez tahmin et
            # Bu basit bir yaklaşım, gerçek uygulamada OSM verisi kullanılmalı
            zone_center = None
            
            if zone_key == 'Beykoz_Sahil':
                zone_center = (41.1140, 29.0890)  # Sahil orta noktası
            elif zone_key == 'Beykoz_Barbaros_Cad':
                zone_center = (41.1130, 29.0885)
            elif zone_key == 'Beykoz_Sumbul_Sok':
                zone_center = (41.1122, 29.0900)
            elif zone_key == 'Beykoz_Karanfil_Sok':
                zone_center = (41.1120, 29.0910)
            elif zone_key == 'Beykoz_Karagoz_Sirti':
                zone_center = (41.1117, 29.0920)
            
            if zone_center:
                distance = haversine(lon, lat, zone_center[1], zone_center[0])
                if distance < min_distance and distance <= max_distance_km:
                    min_distance = distance
                    closest_zone = (zone_key, zone_data, distance)
    
    if closest_zone:
        return closest_zone
    
    return None, None, None


def get_optimization_profile(profile_name='balanced'):
    """
    Optimizasyon profilini döndürür
    
    Args:
        profile_name (str): Profil adı
        
    Returns:
        dict: Profil bilgileri
    """
    return OPTIMIZATION_PROFILES.get(profile_name, OPTIMIZATION_PROFILES['balanced'])
