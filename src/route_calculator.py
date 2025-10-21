import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from datetime import datetime
import json

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

class RouteSegmentAnalyzer:
    """Rota segmentlerini analiz eder ve trafik özelliklerini belirler"""
    
    @staticmethod
    def classify_route_segments(coordinates, elevations, distances):
        """
        Rotayı segmentlere ayırır ve her segmentin özelliklerini belirler
        """
        segments = []
        
        for i in range(len(coordinates) - 1):
            lat1, lng1 = coordinates[i]
            lat2, lng2 = coordinates[i + 1]
            
            segment_distance = distances[i + 1] - distances[i]
            if segment_distance == 0:
                continue
            
            # Eğim hesapla
            elevation_change = elevations[i + 1] - elevations[i]
            gradient = (elevation_change / (segment_distance * 1000)) * 100 if segment_distance > 0 else 0
            
            # Segment tipini belirle (basit konum bazlı)
            segment_type = RouteSegmentAnalyzer.determine_segment_type(lat1, lng1, lat2, lng2)
            
            segments.append({
                'start_idx': i,
                'end_idx': i + 1,
                'distance_km': segment_distance,
                'gradient': gradient,
                'elevation_change': elevation_change,
                'type': segment_type,
                'traffic_zone': segment_type
            })
        
        return segments
    
    @staticmethod
    def determine_segment_type(lat1, lng1, lat2, lng2):
        """
        Koordinatlara göre segment tipini belirle
        """
        # Maltepe-Kartal arasında (E5 bölgesi)
        if 40.92 < lat1 < 40.94 and 29.14 < lng1 < 29.18:
            return 'Anadolu'
        # Aydos Ormanı civarı
        elif lat1 > 40.95 or lng1 > 29.19:
            return 'Suburban'
        # E5 yakını
        elif 40.93 < lat1 < 40.95:
            return 'E5'
        else:
            return 'Suburban'


class FuelConsumptionCalculator:
    """Yakıt tüketimi hesaplama motoru"""
    @staticmethod
    def calculate_fuel_consumption(vehicle_specs, route_data, time_of_day='peak'):
        """
        Segment bazlı gerçekçi yakıt tüketimi hesaplama
        
        Parametreler:
        - vehicle_specs: Araç özellikleri
        - route_data: Rota verileri
        - time_of_day: 'peak' (06-10, 17-21) veya 'offpeak'
        """
        # Route segmentlerini analiz et
        segments = RouteSegmentAnalyzer.classify_route_segments(
            route_data['coordinates'],
            route_data['elevations'],
            route_data['distances']
        )
        
        total_fuel = 0
        segment_details = []
        
        # Her segment için ayrı hesaplama
        for segment in segments:
            traffic_zone = TRAFFIC_ZONES[segment['traffic_zone']]
            
            # Ortalama hız belirleme
            avg_speed = traffic_zone['avg_speed_peak'] if time_of_day == 'peak' else traffic_zone['avg_speed_offpeak']
            
            # Hız bazlı tüketim faktörü
            if avg_speed < 40:
                # Düşük hız = şehir içi tüketimi
                base_consumption = vehicle_specs['fuel_consumption_city']
                speed_factor = 1.0 + (40 - avg_speed) / 100  # Daha yavaş = daha fazla tüketim
            elif avg_speed > 80:
                # Yüksek hız
                base_consumption = vehicle_specs['fuel_consumption_highway']
                speed_factor = 1.0 + (avg_speed - 80) / 200  # Çok hızlı da fazla tüketim
            else:
                # Orta hız - interpolasyon
                city = vehicle_specs['fuel_consumption_city']
                highway = vehicle_specs['fuel_consumption_highway']
                ratio = (avg_speed - 40) / 40
                base_consumption = city + (highway - city) * ratio
                speed_factor = 1.0
            
            # Trafik yoğunluğu faktörü
            traffic_factor = traffic_zone['traffic_multiplier'] if time_of_day == 'peak' else 1.0
            
            # Eğim faktörü
            gradient_factor = 1.0
            if segment['gradient'] > 0:  # Tırmanış
                gradient_factor += segment['gradient'] * 0.015  # Her %1 için %1.5 artış
            elif segment['gradient'] < 0:  # İniş
                gradient_factor += segment['gradient'] * 0.005  # Hafif bonus
            
            # Dur-kalk faktörü (düşük hızda)
            stop_go_factor = 1.0
            if avg_speed < 30:
                stop_go_factor = 1.3  # %30 ekstra tüketim
            elif avg_speed < 50:
                stop_go_factor = 1.1  # %10 ekstra
            
            # Güç/ağırlık etkisi
            power_to_weight = vehicle_specs['hp'] / vehicle_specs['weight_kg']
            if power_to_weight < 0.08 and segment['gradient'] > 5:
                gradient_factor *= 1.2  # Zayıf motor tırmanışta zorlanır
            
            # Segment yakıt tüketimi
            segment_fuel = (base_consumption / 100) * segment['distance_km'] * \
                        gradient_factor * traffic_factor * speed_factor * stop_go_factor
            
            total_fuel += segment_fuel
            
            segment_details.append({
                'distance': segment['distance_km'],
                'type': segment['traffic_zone'],
                'avg_speed': avg_speed,
                'gradient': segment['gradient'],
                'fuel_used': segment_fuel,
                'base_consumption': base_consumption,
                'traffic_factor': traffic_factor,
                'gradient_factor': gradient_factor
            })
        
        # Toplam mesafe
        total_distance = route_data['total_distance_km']
        
        # 100km başına ortalama tüketim
        fuel_per_100km = (total_fuel / total_distance * 100) if total_distance > 0 else 0
        
        # Maliyet hesaplama (güncel yakıt fiyatları - TL)
        fuel_prices = {'Benzin': 45.50, 'Dizel': 47.20}
        fuel_cost = total_fuel * fuel_prices[vehicle_specs['fuel_type']]
        
        # Segment istatistikleri
        segment_stats = {
            'E5': {'distance': 0, 'fuel': 0},
            'Anadolu': {'distance': 0, 'fuel': 0},
            'Suburban': {'distance': 0, 'fuel': 0},
            'Highway': {'distance': 0, 'fuel': 0}
        }
        
        for detail in segment_details:
            zone = detail['type']
            segment_stats[zone]['distance'] += detail['distance']
            segment_stats[zone]['fuel'] += detail['fuel_used']
        
        return {
            'total_fuel_liters': total_fuel,
            'fuel_per_100km': fuel_per_100km,
            'fuel_cost_tl': fuel_cost,
            'segment_details': segment_details,
            'segment_stats': segment_stats,
            'time_of_day': time_of_day
        }
    
    @staticmethod
    def assess_vehicle_capability(vehicle_specs, route_data):
        """Aracın rotayı ne kadar zorluk yaşayacağını değerlendir"""
        
        power_to_weight = vehicle_specs['hp'] / vehicle_specs['weight_kg']
        torque_to_weight = vehicle_specs['torque_nm'] / vehicle_specs['weight_kg']
        
        # Zorluk skorları
        warnings = []
        difficulty = "KOLAY"
        
        # Güç analizi
        if power_to_weight < 0.07:
            warnings.append("⚠️ Motor gücü düşük - tırmanışlarda zorlanabilir")
            difficulty = "ZOR"
        elif power_to_weight < 0.08:
            warnings.append("⚡ Motor gücü orta - dikkatli sürüş önerilir")
            difficulty = "ORTA"
        
        # Tork analizi
        if torque_to_weight < 0.18:
            warnings.append("⚠️ Tork düşük - yokuş kalkışlarda güçlük çekilebilir")
        
        # Eğim analizi
        if route_data['avg_gradient'] > 8:
            warnings.append("🚨 Ortalama eğim çok yüksek - 1. vites kullanımı gerekebilir")
            difficulty = "ÇOK ZOR"
        elif route_data['avg_gradient'] > 5:
            warnings.append("⚠️ Eğim yüksek - 2. vites kullanımı önerilir")
            if difficulty == "KOLAY":
                difficulty = "ORTA"
        
        # Toplam tırmanış
        if route_data['total_ascent_m'] > 300:
            warnings.append("📈 Uzun tırmanış - motor ısınmasına dikkat")
        
        return {
            'difficulty': difficulty,
            'warnings': warnings,
            'power_to_weight': power_to_weight,
            'torque_to_weight': torque_to_weight
        }


class RouteElevationAnalyzer:
    def __init__(self, google_api_key=None):
        """
        Rota yükseklik analizi için sınıf
        
        Args:
            google_api_key: Google Maps API anahtarı (opsiyonel, Open-Elevation kullanılabilir)
        """
        self.google_api_key = google_api_key
        self.use_open_elevation = google_api_key is None
        self.fuel_calculator = FuelConsumptionCalculator()
        
    def get_route_coordinates(self, origin, destination):
        """
        Google Directions API ile rota koordinatlarını al
        Eğer API key yoksa, basit doğrusal interpolasyon kullan
        """
        if self.google_api_key:
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': origin,
                'destination': destination,
                'key': self.google_api_key,
                'mode': 'driving'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                # Polyline'ı decode et
                polyline = data['routes'][0]['overview_polyline']['points']
                coordinates = self.decode_polyline(polyline)
                return coordinates
        
        # API key yoksa veya hata varsa, doğrusal interpolasyon kullan
        print("Google Directions API kullanılamıyor, doğrusal rota oluşturuluyor...")
        return self.create_linear_route(origin, destination)
    
    def create_linear_route(self, origin, destination, num_points=50):
        """
        İki nokta arasında doğrusal rota oluştur
        """
        # Maltepe Tınaztepe Sokak koordinatları (yaklaşık)
        origin_coords = (40.9280, 29.1450)
        # Aydos Ormanı Rekreasyon Alanı koordinatları (yaklaşık)
        dest_coords = (40.9650, 29.2100)
        
        lats = np.linspace(origin_coords[0], dest_coords[0], num_points)
        lngs = np.linspace(origin_coords[1], dest_coords[1], num_points)
        
        return list(zip(lats, lngs))
    
    def decode_polyline(self, polyline_str):
        """Google Polyline formatını decode et"""
        coordinates = []
        index = 0
        lat = 0
        lng = 0
        
        while index < len(polyline_str):
            shift = 0
            result = 0
            
            while True:
                b = ord(polyline_str[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            
            dlat = ~(result >> 1) if result & 1 else result >> 1
            lat += dlat
            
            shift = 0
            result = 0
            
            while True:
                b = ord(polyline_str[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            
            dlng = ~(result >> 1) if result & 1 else result >> 1
            lng += dlng
            
            coordinates.append((lat / 1e5, lng / 1e5))
        
        return coordinates
    
    def get_elevations(self, coordinates):
        """
        Koordinatlar için yükseklik verilerini al
        """
        elevations = []
        
        if self.use_open_elevation:
            # Open-Elevation API kullan (ücretsiz)
            print("Open-Elevation API kullanılıyor...")
            url = "https://api.open-elevation.com/api/v1/lookup"
            
            # API limitleri için küçük gruplar halinde gönder
            batch_size = 100
            for i in range(0, len(coordinates), batch_size):
                batch = coordinates[i:i + batch_size]
                locations = [{"latitude": lat, "longitude": lng} for lat, lng in batch]
                
                try:
                    response = requests.post(url, json={"locations": locations}, timeout=30)
                    data = response.json()
                    
                    for result in data['results']:
                        elevations.append(result['elevation'])
                except Exception as e:
                    print(f"Hata: {e}")
                    elevations.extend([0] * len(batch))
        else:
            # Google Elevation API kullan
            print("Google Elevation API kullanılıyor...")
            url = "https://maps.googleapis.com/maps/api/elevation/json"
            
            locations = "|".join([f"{lat},{lng}" for lat, lng in coordinates])
            params = {
                'locations': locations,
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                elevations = [result['elevation'] for result in data['results']]
        
        return elevations
    
    def analyze_route(self, origin, destination):
        """
        Rotayı analiz et ve sonuçları döndür
        """
        print(f"\nRota analizi başlatılıyor...")
        print(f"Başlangıç: {origin}")
        print(f"Varış: {destination}\n")
        
        # Rota koordinatlarını al
        coordinates = self.get_route_coordinates(origin, destination)
        print(f"Rota noktası sayısı: {len(coordinates)}")
        
        # Yükseklik verilerini al
        elevations = self.get_elevations(coordinates)
        
        # Mesafe hesapla (yaklaşık)
        distances = [0]
        for i in range(1, len(coordinates)):
            lat1, lng1 = coordinates[i-1]
            lat2, lng2 = coordinates[i]
            
            # Haversine formülü (yaklaşık mesafe km cinsinden)
            R = 6371
            dlat = np.radians(lat2 - lat1)
            dlng = np.radians(lng2 - lng1)
            a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlng/2)**2
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
            distance = R * c
            
            distances.append(distances[-1] + distance)
        
        # İstatistikler
        total_distance = distances[-1]
        min_elevation = min(elevations)
        max_elevation = max(elevations)
        total_ascent = sum([elevations[i] - elevations[i-1] for i in range(1, len(elevations)) 
                           if elevations[i] > elevations[i-1]])
        total_descent = sum([elevations[i-1] - elevations[i] for i in range(1, len(elevations)) 
                            if elevations[i] < elevations[i-1]])
        
        results = {
            'coordinates': coordinates,
            'elevations': elevations,
            'distances': distances,
            'total_distance_km': total_distance,
            'min_elevation_m': min_elevation,
            'max_elevation_m': max_elevation,
            'total_ascent_m': total_ascent,
            'total_descent_m': total_descent,
            'avg_gradient': (max_elevation - min_elevation) / (total_distance * 1000) * 100 if total_distance > 0 else 0
        }
        
        return results
    
    def visualize_route_with_fuel(self, results, vehicle_name, time_of_day='peak', save_path='rota_analizi_yakit.png'):
        """
        Rota analizini yakıt tüketimi ile birlikte görselleştir
        """
        vehicle_specs = VEHICLE_DATABASE[vehicle_name]
        fuel_data = self.fuel_calculator.calculate_fuel_consumption(vehicle_specs, results, time_of_day)
        capability = self.fuel_calculator.assess_vehicle_capability(vehicle_specs, results)
        
        fig = plt.figure(figsize=(20, 16))
        
        # Grid layout oluştur - 5 panel
        gs = fig.add_gridspec(5, 2, height_ratios=[2.5, 1, 1, 1, 0.6], hspace=0.4, wspace=0.3)
        # Eğim hesaplama (harita için)
        lats = [coord[0] for coord in results['coordinates']]
        lngs = [coord[1] for coord in results['coordinates']]
        elevations = results['elevations']
        
        gradients_map = [0]  # İlk nokta için eğim 0
        for i in range(1, len(results['elevations'])):
            if results['distances'][i] != results['distances'][i-1]:
                gradient = (results['elevations'][i] - results['elevations'][i-1]) / \
                          ((results['distances'][i] - results['distances'][i-1]) * 1000) * 100
                gradients_map.append(gradient)
            else:
                gradients_map.append(0)
        
        # %20'yi aşan eğim noktalarını tespit et
        steep_indices = [i for i, g in enumerate(gradients_map) if abs(g) > 20]
        
        # 1. HARİTA - Rota görünümü
        ax_map = fig.add_subplot(gs[0, :])
        
        scatter = ax_map.scatter(lngs, lats, c=elevations, cmap='terrain', 
                                s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
        
        ax_map.plot(lngs, lats, 'b-', linewidth=2, alpha=0.7, label='Rota')
        
        # %20'yi aşan dik eğim bölgelerini vurgula
        if steep_indices:
            steep_lats = [lats[i] for i in steep_indices]
            steep_lngs = [lngs[i] for i in steep_indices]
            
            ax_map.scatter(steep_lngs, steep_lats, c='red', s=200, 
                          marker='X', edgecolors='darkred', linewidth=2,
                          label='Dik Eğim (>%20)', zorder=5)
            
            for i, idx in enumerate(steep_indices):
                ax_map.annotate(f'{abs(gradients_map[idx]):.1f}%', 
                              (steep_lngs[i], steep_lats[i]),
                              xytext=(10, 10), textcoords='offset points',
                              bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8),
                              fontsize=9, fontweight='bold',
                              arrowprops=dict(arrowstyle='->', color='red', lw=2))
        
        ax_map.plot(lngs[0], lats[0], 'go', markersize=15, label='Başlangıç: Maltepe', 
                   markeredgecolor='black', markeredgewidth=2)
        ax_map.plot(lngs[-1], lats[-1], 'ro', markersize=15, label='Varış: Aydos Ormanı',
                   markeredgecolor='black', markeredgewidth=2)
        
        cbar = plt.colorbar(scatter, ax=ax_map, orientation='vertical', pad=0.02)
        cbar.set_label('Yükseklik (m)', fontsize=12, fontweight='bold')
        
        ax_map.set_xlabel('Boylam (°)', fontsize=12, fontweight='bold')
        ax_map.set_ylabel('Enlem (°)', fontsize=12, fontweight='bold')
        ax_map.set_title(f'Rota Haritası - {vehicle_name}\nZorluk: {capability["difficulty"]}', 
                        fontsize=14, fontweight='bold')
        ax_map.grid(True, alpha=0.3, linestyle='--')
        ax_map.legend(loc='upper left', fontsize=10)
        ax_map.set_aspect('equal', adjustable='box')
        
        # 2. YÜKSEKLİK PROFİLİ
        ax_elev = fig.add_subplot(gs[1, :])
        
        ax_elev.plot(results['distances'], results['elevations'], 'b-', linewidth=2.5)
        ax_elev.fill_between(results['distances'], results['elevations'], 
                            alpha=0.3, color='skyblue')
        
        min_idx = results['elevations'].index(results['min_elevation_m'])
        max_idx = results['elevations'].index(results['max_elevation_m'])
        
        ax_elev.plot(results['distances'][min_idx], results['min_elevation_m'], 'go', 
                    markersize=12, label=f"En düşük: {results['min_elevation_m']:.1f}m",
                    markeredgecolor='black', markeredgewidth=1.5)
        ax_elev.plot(results['distances'][max_idx], results['max_elevation_m'], 'ro', 
                    markersize=12, label=f"En yüksek: {results['max_elevation_m']:.1f}m",
                    markeredgecolor='black', markeredgewidth=1.5)
        
        ax_elev.set_xlabel('Mesafe (km)', fontsize=12, fontweight='bold')
        ax_elev.set_ylabel('Yükseklik (m)', fontsize=12, fontweight='bold')
        ax_elev.set_title('Yükseklik Profili', fontsize=13, fontweight='bold')
        ax_elev.grid(True, alpha=0.3)
        ax_elev.legend(fontsize=10)
        
        # 3. EĞİM ANALİZİ
        ax_grad = fig.add_subplot(gs[2, :])
        
        gradients = []
        gradient_distances = []
        
        for i in range(1, len(results['elevations'])):
            if results['distances'][i] != results['distances'][i-1]:
                gradient = (results['elevations'][i] - results['elevations'][i-1]) / \
                          ((results['distances'][i] - results['distances'][i-1]) * 1000) * 100
                gradients.append(gradient)
                gradient_distances.append(results['distances'][i])
        
        ax_grad.plot(gradient_distances, gradients, 'g-', linewidth=2.5)
        ax_grad.axhline(y=0, color='k', linestyle='--', alpha=0.5, linewidth=1.5)
        
        ax_grad.fill_between(gradient_distances, gradients, 0, alpha=0.4, 
                            where=np.array(gradients) > 0, color='red', 
                            label='Tırmanış', interpolate=True)
        ax_grad.fill_between(gradient_distances, gradients, 0, alpha=0.4, 
                            where=np.array(gradients) < 0, color='blue', 
                            label='İniş', interpolate=True)
        
        steep_gradient_indices = [i for i, g in enumerate(gradients) if abs(g) > 20]
        
        if steep_gradient_indices:
            steep_distances = [gradient_distances[i] for i in steep_gradient_indices]
            steep_values = [gradients[i] for i in steep_gradient_indices]
            
            ax_grad.scatter(steep_distances, steep_values, c='darkred', 
                          s=150, marker='D', edgecolors='black', linewidth=2,
                          label='Kritik Eğim (>%20)', zorder=5)
            
            ax_grad.axhline(y=20, color='orange', linestyle=':', linewidth=2, 
                          alpha=0.7, label='%20 Eğim Sınırı')
            ax_grad.axhline(y=-20, color='orange', linestyle=':', linewidth=2, alpha=0.7)
            
            for i, idx in enumerate(steep_gradient_indices):
                if i == 0 or (steep_distances[i] - steep_distances[i-1]) > 0.2:
                    ax_grad.annotate(f'{abs(steep_values[i]):.1f}%\n{steep_distances[i]:.2f}km', 
                                  (steep_distances[i], steep_values[i]),
                                  xytext=(0, 20 if steep_values[i] > 0 else -30), 
                                  textcoords='offset points',
                                  bbox=dict(boxstyle='round,pad=0.5', 
                                          facecolor='yellow', 
                                          edgecolor='darkred',
                                          linewidth=2,
                                          alpha=0.9),
                                  fontsize=9, fontweight='bold',
                                  ha='center',
                                  arrowprops=dict(arrowstyle='->', 
                                                color='darkred', 
                                                lw=2))
        
        ax_grad.set_xlabel('Mesafe (km)', fontsize=12, fontweight='bold')
        ax_grad.set_ylabel('Eğim (%)', fontsize=12, fontweight='bold')
        ax_grad.set_title('Eğim Analizi - Kritik Bölgeler Vurgulanmış', fontsize=13, fontweight='bold')
        ax_grad.grid(True, alpha=0.3)
        ax_grad.legend(fontsize=9, loc='best')
        
        # 4. SEGMENT ANALİZİ PANELİ
        ax_segment = fig.add_subplot(gs[3, :])

        seg_stats = fuel_data['segment_stats']
        zones = list(seg_stats.keys())
        distances = [seg_stats[z]['distance'] for z in zones]
        fuels = [seg_stats[z]['fuel'] for z in zones]

        x = np.arange(len(zones))
        width = 0.35

        ax_segment2 = ax_segment.twinx()

        bars1 = ax_segment.bar(x - width/2, distances, width, label='Mesafe (km)', 
                            color='skyblue', edgecolor='black', linewidth=1.5)
        bars2 = ax_segment2.bar(x + width/2, fuels, width, label='Yakıt (L)', 
                            color='orange', edgecolor='black', linewidth=1.5)

        ax_segment.set_xlabel('Yol Tipi', fontsize=12, fontweight='bold')
        ax_segment.set_ylabel('Mesafe (km)', fontsize=12, fontweight='bold', color='skyblue')
        ax_segment2.set_ylabel('Yakıt Tüketimi (L)', fontsize=12, fontweight='bold', color='orange')
        ax_segment.set_title(f'Segment Analizi - {time_of_day.upper()} Saatleri', 
                        fontsize=13, fontweight='bold')
        ax_segment.set_xticks(x)
        ax_segment.set_xticklabels(zones)
        ax_segment.tick_params(axis='y', labelcolor='skyblue')
        ax_segment2.tick_params(axis='y', labelcolor='orange')

        # Değerleri etiketle
        for bar in bars1:
            height = bar.get_height()
            if height > 0:
                ax_segment.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.2f}km', ha='center', va='bottom', fontsize=9)

        for bar in bars2:
            height = bar.get_height()
            if height > 0:
                ax_segment2.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.3f}L', ha='center', va='bottom', fontsize=9)

        ax_segment.legend(loc='upper left')
        ax_segment2.legend(loc='upper right')
        ax_segment.grid(True, alpha=0.3, axis='y')

        # 5. YAKIT TÜKETİMİ BİLGİSİ PANELİ (kompakt versiyon)
        ax_fuel = fig.add_subplot(gs[4, :])
        ax_fuel.axis('off')

        # Segment detayları
        seg_detail_text = ""
        for zone, data in seg_stats.items():
            if data['distance'] > 0:
                zone_info = TRAFFIC_ZONES[zone]
                avg_speed = zone_info['avg_speed_peak'] if time_of_day == 'peak' else zone_info['avg_speed_offpeak']
                seg_detail_text += f"{zone}: {data['distance']:.2f}km @ {avg_speed}km/h → {data['fuel']:.3f}L  |  "

        # Yakıt tüketim bilgisi metni (tek satırda)
        fuel_info = f"""🚗 {vehicle_name} | {vehicle_specs['hp']}HP {vehicle_specs['torque_nm']}Nm | {vehicle_specs['weight_kg']}kg | {vehicle_specs['fuel_type']}
        ⛽ YAKIT: {fuel_data['total_fuel_liters']:.3f}L toplam | {fuel_data['fuel_per_100km']:.2f}L/100km | {fuel_data['fuel_cost_tl']:.2f}TL | Zorluk: {capability['difficulty']}
        📊 SEGMENTLER: {seg_detail_text}
        ⚠️ {' | '.join(capability['warnings'][:3]) if capability['warnings'] else '✅ Araç uygun'}"""

        ax_fuel.text(0.5, 0.5, fuel_info, fontsize=9, family='monospace',
                    bbox=dict(boxstyle='round', facecolor='lightyellow', 
                            edgecolor='orange', linewidth=2, alpha=0.9),
                    verticalalignment='center', horizontalalignment='center',
                    wrap=True)

        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nGrafik kaydedildi: {save_path}")
        plt.show()
    
    def compare_vehicles(self, results, time_of_day='peak', save_path='arac_karsilastirma.png'):
        """
        Tüm araçlar için yakıt tüketimi karşılaştırması
        """
        vehicle_results = {}
        
        for vehicle_name, specs in VEHICLE_DATABASE.items():
            fuel_data = self.fuel_calculator.calculate_fuel_consumption(specs, results, time_of_day)            
            capability = self.fuel_calculator.assess_vehicle_capability(specs, results)
            
            vehicle_results[vehicle_name] = {
                'fuel': fuel_data,
                'capability': capability,
                'specs': specs
            }
        
        # Grafik oluştur
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Araç Karşılaştırma Analizi - {time_of_day.upper()} Saatleri', 
            fontsize=16, fontweight='bold')
        
        vehicles = list(vehicle_results.keys())
        
        # 1. Toplam yakıt tüketimi
        fuel_totals = [vehicle_results[v]['fuel']['total_fuel_liters'] for v in vehicles]
        costs = [vehicle_results[v]['fuel']['fuel_cost_tl'] for v in vehicles]
        colors1 = ['green' if f < 0.5 else 'orange' if f < 0.7 else 'red' for f in fuel_totals]
        colors3 = ['green' if c < 25 else 'orange' if c < 35 else 'red' for c in costs]
        ax1.barh(vehicles, fuel_totals, color=colors1, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax1.set_xlabel('Toplam Yakıt Tüketimi (Litre)', fontweight='bold')
        ax1.set_title('Toplam Yakıt Tüketimi', fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        for i, v in enumerate(fuel_totals):
            ax1.text(v + 0.05, i, f'{v:.2f}L', va='center', fontweight='bold')
        
        # 2. 100km başına tüketim
        fuel_per_100 = [vehicle_results[v]['fuel']['fuel_per_100km'] for v in vehicles]
        colors2 = ['green' if f < 6 else 'orange' if f < 8 else 'red' for f in fuel_per_100]
        
        ax2.barh(vehicles, fuel_per_100, color=colors2, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax2.set_xlabel('Yakıt Tüketimi (L/100km)', fontweight='bold')
        ax2.set_title('100km Başına Tüketim', fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        for i, v in enumerate(fuel_per_100):
            ax2.text(v + 0.1, i, f'{v:.2f}', va='center', fontweight='bold')
        
        # 3. Maliyet karşılaştırma
        costs = [vehicle_results[v]['fuel']['fuel_cost_tl'] for v in vehicles]
        colors3 = ['green' if c < 100 else 'orange' if c < 150 else 'red' for c in costs]
        
        ax3.barh(vehicles, costs, color=colors3, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax3.set_xlabel('Yakıt Maliyeti (TL)', fontweight='bold')
        ax3.set_title('Tahmini Yakıt Maliyeti', fontweight='bold')
        ax3.grid(axis='x', alpha=0.3)
        
        for i, v in enumerate(costs):
            ax3.text(v + 2, i, f'{v:.2f}₺', va='center', fontweight='bold')
        
        # 4. Zorluk skorları
        difficulty_map = {'KOLAY': 1, 'ORTA': 2, 'ZOR': 3, 'ÇOK ZOR': 4}
        difficulties = [difficulty_map[vehicle_results[v]['capability']['difficulty']] for v in vehicles]
        difficulty_labels = [vehicle_results[v]['capability']['difficulty'] for v in vehicles]
        colors4 = ['green' if d == 1 else 'yellow' if d == 2 else 'orange' if d == 3 else 'red' 
                  for d in difficulties]
        
        ax4.barh(vehicles, difficulties, color=colors4, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax4.set_xlabel('Zorluk Seviyesi', fontweight='bold')
        ax4.set_title('Rota Zorluk Değerlendirmesi', fontweight='bold')
        ax4.set_xticks([1, 2, 3, 4])
        ax4.set_xticklabels(['KOLAY', 'ORTA', 'ZOR', 'ÇOK ZOR'])
        ax4.grid(axis='x', alpha=0.3)
        
        for i, (d, label) in enumerate(zip(difficulties, difficulty_labels)):
            ax4.text(d + 0.1, i, label, va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nKarşılaştırma grafiği kaydedildi: {save_path}")
        plt.show()
        
        return vehicle_results
    
    def print_detailed_report(self, results, vehicle_name=None, time_of_day='peak'):
        """
        Detaylı analiz raporu
        """
        # Kritik eğim bölgelerini tespit et
        gradients_full = [0]
        for i in range(1, len(results['elevations'])):
            if results['distances'][i] != results['distances'][i-1]:
                gradient = (results['elevations'][i] - results['elevations'][i-1]) / \
                          ((results['distances'][i] - results['distances'][i-1]) * 1000) * 100
                gradients_full.append(gradient)
            else:
                gradients_full.append(0)
        
        steep_sections = []
        for i, g in enumerate(gradients_full):
            if abs(g) > 20:
                steep_sections.append({
                    'index': i,
                    'distance_km': results['distances'][i],
                    'gradient': g,
                    'lat': results['coordinates'][i][0],
                    'lng': results['coordinates'][i][1],
                    'elevation': results['elevations'][i]
                })
        
        print("\n" + "="*80)
        print("DETAYLI ROTA ANALİZ RAPORU")
        print("="*80)
        print(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        print(f"\n📍 ROTA BİLGİLERİ:")
        print(f"Toplam Mesafe: {results['total_distance_km']:.2f} km")
        print(f"En Düşük Yükseklik: {results['min_elevation_m']:.1f} m")
        print(f"En Yüksek Yükseklik: {results['max_elevation_m']:.1f} m")
        print(f"Yükseklik Farkı: {results['max_elevation_m'] - results['min_elevation_m']:.1f} m")
        print(f"Toplam Tırmanış: {results['total_ascent_m']:.1f} m")
        print(f"Toplam İniş: {results['total_descent_m']:.1f} m")
        print(f"Ortalama Eğim: {results['avg_gradient']:.2f}%")
        print(f"Trafik Durumu: {'YOĞUN SAAT' if time_of_day == 'peak' else 'SEYREK SAAT'}")
        # Kritik eğim bölgeleri
        if steep_sections:
            print("\n" + "⚠️ "*30)
            print("KRİTİK EĞİM BÖLGELERİ (%20'nin Üzeri)")
            print("="*80)
            print(f"Toplam {len(steep_sections)} kritik bölge tespit edildi:\n")
            
            for idx, section in enumerate(steep_sections, 1):
                eğim_tipi = "TIRMAN" if section['gradient'] > 0 else "İNİŞ"
                print(f"{idx}. Bölge - {eğim_tipi}")
                print(f"   Mesafe: {section['distance_km']:.3f} km")
                print(f"   Eğim: {abs(section['gradient']):.1f}%")
                print(f"   Yükseklik: {section['elevation']:.1f} m")
                print(f"   Koordinat: {section['lat']:.6f}°, {section['lng']:.6f}°")
                print(f"   Google Maps: https://www.google.com/maps?q={section['lat']},{section['lng']}")
                print()
        
        # Araç özel rapor
        if vehicle_name:
            print("\n" + "🚗 "*30)
            print(f"ARAÇ ÖZEL ANALİZ: {vehicle_name}")
            print("="*80)
            
            specs = VEHICLE_DATABASE[vehicle_name]
            fuel_data = self.fuel_calculator.calculate_fuel_consumption(specs, results, time_of_day)
            capability = self.fuel_calculator.assess_vehicle_capability(specs, results)
            
            print(f"\n📊 Araç Özellikleri:")
            print(f"Motor Gücü: {specs['hp']} HP")
            print(f"Tork: {specs['torque_nm']} Nm")
            print(f"Ağırlık: {specs['weight_kg']} kg")
            print(f"Motor Hacmi: {specs['engine_cc']} cc")
            print(f"Yakıt Tipi: {specs['fuel_type']}")
            print(f"Şehir İçi Tüketim: {specs['fuel_consumption_city']} L/100km")
            print(f"Şehir Dışı Tüketim: {specs['fuel_consumption_highway']} L/100km")
            
            print(f"\n⛽ Bu Rota İçin Yakıt Tahmini:")
            print(f"\n⛽ {time_of_day.upper()} Saatleri İçin Yakıt Tahmini:")
            print(f"Toplam Tüketim: {fuel_data['total_fuel_liters']:.3f} Litre")
            print(f"100km Başına: {fuel_data['fuel_per_100km']:.2f} L/100km")
            print(f"Tahmini Maliyet: {fuel_data['fuel_cost_tl']:.2f} TL")
            # print(f"Zorluk Faktörü: {fuel_data['gradient_factor']:.2f}x")
            
            print(f"\n📍 Segment Bazlı Analiz:")
            for zone, data in fuel_data['segment_stats'].items():
                if data['distance'] > 0:
                    zone_info = TRAFFIC_ZONES[zone]
                    avg_speed = zone_info['avg_speed_peak'] if time_of_day == 'peak' else zone_info['avg_speed_offpeak']
                    print(f"  {zone}: {data['distance']:.2f}km | Ortalama Hız: {avg_speed}km/h | Yakıt: {data['fuel']:.3f}L")
            print(f"\n🎯 Performans Analizi:")
            print(f"Güç/Ağırlık: {capability['power_to_weight']:.3f} HP/kg")
            print(f"Tork/Ağırlık: {capability['torque_to_weight']:.3f} Nm/kg")
            print(f"Rota Zorluğu: {capability['difficulty']}")
            
            if capability['warnings']:
                print(f"\n⚠️ Uyarılar:")
                for warning in capability['warnings']:
                    print(f"  {warning}")
            else:
                print("\n✅ Bu rota için araç performansı yeterli.")
        
        print("\n" + "="*80)


# KULLANIM ÖRNEĞİ
if __name__ == "__main__":
    print("="*80)
    print("NAVİGASYON ASISTANI - YAKIT TÜKETİMİ VE ROTA ANALİZİ")
    print("="*80)
    
    key = "AIzaSyDFkQuhvtavuFNPvnrlEFZcbh30BarQ-l4"
    # Analyzer oluştur
    analyzer = RouteElevationAnalyzer(key)
    
    # Rota bilgileri
    origin = "Tınaztepe Sokak, Maltepe, İstanbul"
    destination = "Aydos Ormanı Rekreasyon Alanı, İstanbul"
    
    # Rota analizi yap
    results = analyzer.analyze_route(origin, destination)
    
    # Mevcut araçları listele
    print("\n📋 Veritabanındaki Araçlar:")
    for i, vehicle in enumerate(VEHICLE_DATABASE.keys(), 1):
        print(f"{i}. {vehicle}")
    
    # Örnek araç seç
    example_vehicle = "Fiat Egea 1.3 Multijet"
    time_of_day = 'peak'  # 'peak' veya 'offpeak'

    print(f"\n🚗 Seçilen Araç: {example_vehicle}")
    print(f"⏰ Zaman Dilimi: {'Yoğun Saat (06-10, 17-21)' if time_of_day == 'peak' else 'Seyrek Saat'}")

    # Detaylı rapor
    analyzer.print_detailed_report(results, example_vehicle, time_of_day)

    # Görselleştirme
    analyzer.visualize_route_with_fuel(results, example_vehicle, time_of_day)

    # Tüm araçları karşılaştır
    print("\n📊 Tüm araçlar karşılaştırılıyor...")
    vehicle_comparison = analyzer.compare_vehicles(results, time_of_day)    
    # En iyi araçları öner
    print("\n" + "🏆 "*30)
    print("EN İYİ ARAÇ ÖNERİLERİ")
    print("="*80)
    
    # En düşük yakıt tüketen
    best_fuel = min(vehicle_comparison.items(), 
                   key=lambda x: x[1]['fuel']['total_fuel_liters'])
    print(f"\n⛽ En Az Yakıt Tüketen: {best_fuel[0]}")
    print(f"   Tüketim: {best_fuel[1]['fuel']['total_fuel_liters']:.2f} L")
    print(f"   Maliyet: {best_fuel[1]['fuel']['fuel_cost_tl']:.2f} TL")
    
    # En düşük maliyetli
    best_cost = min(vehicle_comparison.items(), 
                   key=lambda x: x[1]['fuel']['fuel_cost_tl'])
    print(f"\n💰 En Düşük Maliyetli: {best_cost[0]}")
    print(f"   Maliyet: {best_cost[1]['fuel']['fuel_cost_tl']:.2f} TL")
    
    # En kolay sürüş
    difficulty_order = {'KOLAY': 0, 'ORTA': 1, 'ZOR': 2, 'ÇOK ZOR': 3}
    easiest = min(vehicle_comparison.items(), 
                 key=lambda x: difficulty_order[x[1]['capability']['difficulty']])
    print(f"\n🎯 En Kolay Sürüş: {easiest[0]}")
    print(f"   Zorluk: {easiest[1]['capability']['difficulty']}")
    print(f"   Güç/Ağırlık: {easiest[1]['capability']['power_to_weight']:.3f} HP/kg")
    
    print("\n" + "="*80)
    print("✓ Analiz tamamlandı! Tüm grafikler kaydedildi.")
    print("="*80)