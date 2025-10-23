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

# İstanbul'daki yoğun yollar ve trafik karakteristikleri
TRAFFIC_ZONES = {
    'E5': {
        'avg_speed_peak': 25,      # Yoğun saatlerde ortalama hız (km/h)
        'avg_speed_offpeak': 60,   # Seyrek saatlerde
        'traffic_multiplier': 1.8,  # Trafik tüketim çarpanı
        'keywords': ['E5', 'TEM', 'Otoyol', 'D100']
    },
    'Anadolu': {
        'avg_speed_peak': 30,
        'avg_speed_offpeak': 50,
        'traffic_multiplier': 1.6,
        'keywords': ['Bağdat', 'Anadolu', 'Kadıköy', 'Maltepe', 'Kartal']
    },
    'Suburban': {
        'avg_speed_peak': 40,
        'avg_speed_offpeak': 70,
        'traffic_multiplier': 1.3,
        'keywords': ['Aydos', 'Orman', 'Sultanbeyli', 'Sancaktepe']
    },
    'Highway': {
        'avg_speed_peak': 80,
        'avg_speed_offpeak': 100,
        'traffic_multiplier': 1.0,
        'keywords': ['Otoyol', 'Çevre']
    }
}

# Yakıt fiyatları (TL/Litre) - Güncellenebilir
FUEL_PRICES = {
    'Benzin': 39.48,
    'Dizel': 40.28
}

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

def get_fuel_price(fuel_type):
    """
    Belirli bir yakıt tipinin fiyatını döndürür
    
    Args:
        fuel_type (str): Yakıt tipi (Benzin/Dizel)
        
    Returns:
        float: Yakıt fiyatı (TL/Litre)
    """
    return FUEL_PRICES.get(fuel_type, 0)
