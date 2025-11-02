"""
Enhanced Routing Engine - Geliştirilmiş Rota Hesaplama Motoru
Düzeltilmiş eğim limitleri ve geliştirilmiş hata kontrolü ile
"""

import heapq
import json
import numpy as np
from math import radians, cos, sin, asin, sqrt, atan2, degrees
from datetime import datetime
import requests
import urllib.parse


class EnhancedRoutingEngine:
    """
    Düzeltilmiş A* algoritması - Gerçekçi eğim limitleri
    """
    
    def __init__(self, road_network, vehicle_db, traffic_zones):
        self.nodes = road_network.get('nodes', {})
        self.edges = road_network.get('edges', [])
        self.vehicle_db = vehicle_db
        self.traffic_zones = traffic_zones
        
        # Kenarları indeksle
        self._build_edge_index()
        
        # Eğim renkleri
        self.slope_colors = {
            'easy': '#00ff00',      # Yeşil: %0-5
            'moderate': '#ffff00',   # Sarı: %5-10
            'hard': '#ff8800',       # Turuncu: %10-15
            'extreme': '#ff0000',    # Kırmızı: %15+
            'descent': '#0088ff'     # Mavi: İniş
        }
        
        print(f"✓ Enhanced Routing Engine başlatıldı")
        print(f"  • {len(self.nodes)} düğüm")
        print(f"  • {len(self.edges)} kenar")
    
    
    def _build_edge_index(self):
        """Kenarları düğümlere göre indeksle"""
        self.outgoing_edges = {}
        self.incoming_edges = {}
        
        for edge in self.edges:
            from_node = str(edge['from'])  # String'e çevir
            to_node = str(edge['to'])      # String'e çevir
            
            if from_node not in self.outgoing_edges:
                self.outgoing_edges[from_node] = []
            self.outgoing_edges[from_node].append(edge)
            
            if to_node not in self.incoming_edges:
                self.incoming_edges[to_node] = []
            self.incoming_edges[to_node].append(edge)
    
    
    def calculate_vehicle_capability(self, vehicle_name):
        """
        DÜZELTME: Gerçekçi araç eğim kapasitesi hesapla
        """
        vehicle = self.vehicle_db.get(vehicle_name, {})
        
        if not vehicle:
            return None
        
        hp = vehicle.get('hp', 100)
        torque = vehicle.get('torque_nm', 200)
        weight = vehicle.get('weight_kg', 1300)
        
        # Güç/ağırlık oranı (HP/ton)
        power_weight_ratio = (hp / weight) * 1000
        
        # Tork/ağırlık oranı
        torque_weight_ratio = torque / weight
        
        # GERÇEKÇİ EĞİM LİMİTLERİ
        # Düşük güçlü araçlar: %8-12-15
        # Orta güçlü araçlar: %10-15-18
        # Yüksek güçlü araçlar: %12-18-22
        
        if power_weight_ratio < 70:  # Düşük güç (Egea vb.)
            comfortable_slope = 8.0
            manageable_slope = 12.0
            maximum_slope = 15.0
        elif power_weight_ratio < 100:  # Orta güç (Corolla vb.)
            comfortable_slope = 10.0
            manageable_slope = 15.0
            maximum_slope = 18.0
        else:  # Yüksek güç (Qashqai vb.)
            comfortable_slope = 12.0
            manageable_slope = 18.0
            maximum_slope = 22.0
        
        # Tork etkisi (dizel araçlar için avantaj)
        if vehicle.get('fuel_type') == 'Dizel':
            comfortable_slope += 1.0
            manageable_slope += 1.5
            maximum_slope += 2.0
        
        # Yakıt tüketim çarpanları
        fuel_multipliers = {
            'flat': 1.0,           # %0-2
            'gentle': 1.15,        # %2-5
            'moderate': 1.35,      # %5-10
            'steep': 1.65,         # %10-15
            'extreme': 2.2,        # %15+
            'descent': 0.7         # İniş
        }
        
        return {
            'vehicle_name': vehicle_name,
            'hp': hp,
            'torque': torque,
            'weight': weight,
            'power_weight_ratio': round(power_weight_ratio, 2),
            'torque_weight_ratio': round(torque_weight_ratio, 2),
            'comfortable_slope': round(comfortable_slope, 1),
            'manageable_slope': round(manageable_slope, 1),
            'maximum_slope': round(maximum_slope, 1),
            'fuel_multipliers': fuel_multipliers
        }
    
    
    def find_optimal_route(self, start_gps, end_gps, vehicle_name, 
                          time_of_day='offpeak', mode='power_optimized'):
        """
        Optimal rotayı bul - geliştirilmiş hata kontrolü ile
        """
        print(f"\n{'='*70}")
        print("ROTA HESAPLAMA")
        print(f"{'='*70}")
        
        # Araç kapasitelerini hesapla
        vehicle_capability = self.calculate_vehicle_capability(vehicle_name)
        if not vehicle_capability:
            print(f"❌ Araç bulunamadı: {vehicle_name}")
            return None
        
        print(f"\n📊 Araç: {vehicle_name}")
        print(f"  • Güç/Ağırlık: {vehicle_capability['power_weight_ratio']} HP/ton")
        print(f"  • Rahat eğim: %{vehicle_capability['comfortable_slope']}")
        print(f"  • Zorlu eğim: %{vehicle_capability['manageable_slope']}")
        print(f"  • Maksimum: %{vehicle_capability['maximum_slope']}")
        
        # En yakın düğümleri bul
        print(f"başlangıç: {start_gps}")
        start_node = self.find_closest_node(*start_gps)
        print(f"bitiş: {end_gps}")
        end_node = self.find_closest_node(*end_gps)
        
        if not start_node:
            print(f"❌ Başlangıç noktası bulunamadı: {start_gps}")
            return None
            
        if not end_node:
            print(f"❌ Varış noktası bulunamadı: {end_gps}")
            return None
        
        if start_node == end_node:
            print("❌ Başlangıç ve varış aynı nokta!")
            return None
        
        print(f"\n🔍 Rota aranıyor...")
        print(f"  Başlangıç düğümü: {start_node}")
        print(f"  Varış düğümü: {end_node}")
        
        # A* algoritması ile rota bul
        route_path = self.a_star_search(
            start_node, end_node, 
            vehicle_capability, 
            time_of_day, 
            mode
        )
        
        if not route_path or len(route_path) < 2:
            print("\n❌ Rota bulunamadı!")
            print("  Olası sebepler:")
            print("  • Araç için çok dik yollar")
            print("  • Bağlantısız yol ağı")
            print("  • Çok uzak noktalar")
            
            # Boş rota döndür (hata durumu için)
            return {
                'path': [start_node] if start_node else [],
                'segments': [],
                'total_distance': 0,
                'total_fuel': 0,
                'fuel_cost': 0,
                'total_time': 0,
                'max_slope': 0,
                'critical_sections': 0,
                'vehicle_capability': vehicle_capability,
                'google_maps_url': self.generate_google_maps_url([]),
                'error': 'Rota bulunamadı'
            }
        
        # Rota detaylarını hesapla
        route_details = self.analyze_route(route_path, vehicle_capability, time_of_day)
        
        # Google Maps URL'si oluştur
        google_maps_url = self.generate_google_maps_url(route_path)
        route_details['google_maps_url'] = google_maps_url
        
        print(f"\n✅ ROTA BULUNDU!")
        print(f"  • Mesafe: {route_details['total_distance']:.2f} km")
        print(f"  • Süre: {route_details['total_time']:.1f} dk")
        print(f"  • Yakıt: {route_details['total_fuel']:.2f} L")
        print(f"  • Maks Eğim: %{route_details['max_slope']:.1f}")
        
        return route_details
    
    
    def find_closest_node(self, lat, lon):
        """En yakın yol düğümünü bul - geliştirilmiş"""
        if not lat or not lon:
            print(f"⚠️ Geçersiz koordinat: {lat}, {lon}")
            return None
        
        print(f"lat and lon: {lat}, {lon}")
        min_distance = float('inf')
        closest_node = None
        print(f"Burada")
        for node_id, node_data in self.nodes.items():
            gps = node_data.get('gps', [0, 0])
            node_lat = gps[0] if len(gps) > 0 else 0
            node_lon = gps[1] if len(gps) > 1 else 0
            
            if not node_lat or not node_lon:
                continue
            
            distance = self.haversine_distance(lat, lon, node_lat, node_lon)
            # print(f"distance {distance:.0f}m ")
            if distance < min_distance:
                min_distance = distance
                closest_node = str(node_id)  # String olarak kaydet
        
        if min_distance > 500:  # 500 metreden uzaksa
            print(f"⚠️ En yakın düğüm {min_distance:.0f}m uzakta!")
        
        return closest_node
    
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Haversine mesafe hesabı"""
        R = 6371000  # Dünya yarıçapı (metre)
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        return R * c
    
    
    def calculate_slope(self, from_node_id, to_node_id):
        """İki düğüm arasındaki eğimi hesapla"""
        from_node = self.nodes.get(str(from_node_id), {})
        to_node = self.nodes.get(str(to_node_id), {})
        
        # Yükseklikler (yoksa varsayılan değer kullan)
        from_elevation = from_node.get('elevation', 50)
        to_elevation = to_node.get('elevation', 50)
        elevation_change = to_elevation - from_elevation
        
        # Mesafe
        distance = self.haversine_distance(
            from_node.get('lat', 0), from_node.get('lon', 0),
            to_node.get('lat', 0), to_node.get('lon', 0)
        )
        
        # Eğim yüzdesi
        if distance > 0:
            slope_percent = (elevation_change / distance) * 100
        else:
            slope_percent = 0
        
        # Kategori
        abs_slope = abs(slope_percent)
        if slope_percent < -2:
            category = 'descent'
            difficulty = 'descent'
        elif abs_slope < 2:
            category = 'flat'
            difficulty = 'easy'
        elif abs_slope < 5:
            category = 'gentle'
            difficulty = 'easy'
        elif abs_slope < 10:
            category = 'moderate'
            difficulty = 'moderate'
        elif abs_slope < 15:
            category = 'steep'
            difficulty = 'hard'
        else:
            category = 'extreme'
            difficulty = 'extreme'
        
        return {
            'slope_percent': round(slope_percent, 2),
            'category': category,
            'difficulty': difficulty,
            'elevation_change': round(elevation_change, 1),
            'distance_m': round(distance, 1),
            'from_elevation': round(from_elevation, 1),
            'to_elevation': round(to_elevation, 1)
        }
    
    
    def calculate_edge_cost(self, edge, vehicle_capability, time_of_day='offpeak', mode='balanced'):
        """Kenar maliyeti hesapla"""
        # Temel özellikler
        distance = edge.get('distance', 100)
        base_speed = edge.get('speed_limit', 50)
        
        # Eğim hesapla
        slope_info = self.calculate_slope(edge['from'], edge['to'])
        slope_percent = slope_info['slope_percent']
        slope_category = slope_info['category']
        
        # Araç limitleri
        comfortable_slope = vehicle_capability['comfortable_slope']
        manageable_slope = vehicle_capability['manageable_slope']
        maximum_slope = vehicle_capability['maximum_slope']
        
        # Eğim penaltısı
        abs_slope = abs(slope_percent)
        if abs_slope <= comfortable_slope:
            slope_penalty = 1.0
            passable = True
            difficulty_level = 'comfortable'
        elif abs_slope <= manageable_slope:
            slope_penalty = 1.5 + (abs_slope - comfortable_slope) * 0.1
            passable = True
            difficulty_level = 'manageable'
        elif abs_slope <= maximum_slope:
            slope_penalty = 2.5 + (abs_slope - manageable_slope) * 0.2
            passable = True
            difficulty_level = 'difficult'
        else:
            slope_penalty = float('inf')
            passable = False
            difficulty_level = 'impassable'
        
        # Yakıt tüketimi
        fuel_multiplier = vehicle_capability['fuel_multipliers'].get(slope_category, 1.0)
        base_consumption = vehicle_capability.get('fuel_consumption_city', 6.0) / 100
        fuel_consumption = base_consumption * (distance / 1000) * fuel_multiplier
        
        # Toplam maliyet
        if not passable:
            total_cost = float('inf')
        else:
            time_cost = (distance / (base_speed * 1000 / 3600))
            fuel_cost = fuel_consumption * 35
            slope_cost = slope_penalty * 10
            
            # Mod ağırlıkları
            if mode == 'power_optimized':
                weights = {'fuel': 1.5, 'time': 0.8, 'slope': 2.5}
            else:
                weights = {'fuel': 1.0, 'time': 1.0, 'slope': 1.0}
            
            total_cost = (
                weights['fuel'] * fuel_cost +
                weights['time'] * time_cost * 60 +
                weights['slope'] * slope_cost
            )
        
        return {
            'total_cost': total_cost,
            'distance': distance,
            'fuel_consumption': round(fuel_consumption, 3),
            'fuel_cost': round(fuel_consumption * 35, 2),
            'time_minutes': round((distance / (base_speed * 1000 / 3600)) * 60, 1),
            'slope_info': slope_info,
            'passable': passable,
            'difficulty_level': difficulty_level,
            'slope_penalty': round(slope_penalty, 2)
        }
    
    
    def a_star_search(self, start_node, end_node, vehicle_capability, time_of_day, mode):
        """A* algoritması - geliştirilmiş hata kontrolü"""
        # String'e çevir
        start_node = str(start_node)
        end_node = str(end_node)
        
        # Priority queue
        open_set = [(0, start_node, [start_node])]
        closed_set = set()
        g_costs = {start_node: 0}
        
        iteration = 0
        max_iterations = 50000  # Artırıldı
        
        print(f"  İterasyon başlıyor... (maks {max_iterations})")
        
        while open_set and iteration < max_iterations:
            iteration += 1
            
            if iteration % 1000 == 0:
                print(f"  İterasyon {iteration}...")
            
            # En düşük maliyetli düğümü al
            current_f, current_node, current_path = heapq.heappop(open_set)
            
            if current_node == end_node:
                print(f"  ✓ Hedef bulundu! ({iteration} iterasyon)")
                return current_path
            
            if current_node in closed_set:
                continue
            
            closed_set.add(current_node)
            
            # Komşuları kontrol et
            for edge in self.outgoing_edges.get(current_node, []):
                neighbor = str(edge['to'])
                
                if neighbor in closed_set:
                    continue
                
                # Kenar maliyeti
                edge_cost_info = self.calculate_edge_cost(
                    edge, vehicle_capability, time_of_day, mode
                )
                
                # Geçilemez mi?
                if not edge_cost_info['passable']:
                    continue
                
                # Yeni maliyet
                tentative_g = g_costs[current_node] + edge_cost_info['total_cost']
                
                if neighbor not in g_costs or tentative_g < g_costs[neighbor]:
                    g_costs[neighbor] = tentative_g
                    
                    # Heuristik
                    h_cost = self.calculate_heuristic(neighbor, end_node)
                    f_cost = tentative_g + h_cost
                    
                    new_path = current_path + [neighbor]
                    heapq.heappush(open_set, (f_cost, neighbor, new_path))
        
        print(f"  ❌ Rota bulunamadı ({iteration} iterasyon)")
        return None
    
    
    def calculate_heuristic(self, from_node_id, to_node_id):
        """A* için heuristik"""
        from_node = self.nodes.get(str(from_node_id), {})
        to_node = self.nodes.get(str(to_node_id), {})
        
        if not from_node or not to_node:
            return float('inf')
        
        distance = self.haversine_distance(
            from_node.get('lat', 0), from_node.get('lon', 0),
            to_node.get('lat', 0), to_node.get('lon', 0)
        )
        
        return distance / 100
    
    
    def analyze_route(self, route_path, vehicle_capability, time_of_day):
        """Rota analizi"""
        total_distance = 0
        total_fuel = 0
        total_time = 0
        max_slope = 0
        critical_sections = 0
        slope_segments = []
        
        for i in range(len(route_path) - 1):
            from_node = str(route_path[i])
            to_node = str(route_path[i + 1])
            
            # Kenarı bul
            edge = None
            for e in self.outgoing_edges.get(from_node, []):
                if str(e['to']) == to_node:
                    edge = e
                    break
            
            if not edge:
                continue
            
            # Maliyet hesapla
            cost_info = self.calculate_edge_cost(
                edge, vehicle_capability, time_of_day, 'balanced'
            )
            
            total_distance += cost_info['distance'] / 1000
            total_fuel += cost_info['fuel_consumption']
            total_time += cost_info['time_minutes']
            
            # Eğim bilgisi
            slope_info = cost_info['slope_info']
            abs_slope = abs(slope_info['slope_percent'])
            
            if abs_slope > max_slope:
                max_slope = abs_slope
            
            if cost_info['difficulty_level'] in ['difficult', 'manageable']:
                critical_sections += 1
            
            # Segment kaydet
            slope_segments.append({
                'from': from_node,
                'to': to_node,
                'distance': cost_info['distance'],
                'slope': slope_info['slope_percent'],
                'category': slope_info['category'],
                'difficulty': slope_info['difficulty'],
                'elevation_change': slope_info['elevation_change'],
                'from_elevation': slope_info['from_elevation'],
                'to_elevation': slope_info['to_elevation'],
                'color': self.get_slope_color(slope_info),
                'fuel_consumption': cost_info['fuel_consumption'],
                'time_minutes': cost_info['time_minutes'],
                'passable': cost_info['passable'],
                'difficulty_level': cost_info['difficulty_level']
            })
        
        return {
            'path': route_path,
            'segments': slope_segments,
            'total_distance': round(total_distance, 2),
            'total_fuel': round(total_fuel, 2),
            'fuel_cost': round(total_fuel * 35, 2),
            'total_time': round(total_time, 1),
            'max_slope': round(max_slope, 1),
            'critical_sections': critical_sections,
            'vehicle_capability': vehicle_capability
        }
    
    
    def get_slope_color(self, slope_info):
        """Eğim rengi"""
        difficulty = slope_info['difficulty']
        return self.slope_colors.get(difficulty, '#888888')
    
    
    def generate_google_maps_url(self, route_path):
        """Google Maps URL oluştur"""
        if not route_path or len(route_path) < 2:
            # Boş URL
            return "https://www.google.com/maps/dir/?api=1&origin=0,0&destination=0,0&travelmode=driving"
        
        # Waypoint'ler
        waypoints = []
        step = max(1, len(route_path) // 23)
        
        for i in range(0, len(route_path), step):
            node_id = str(route_path[i])
            node_data = self.nodes.get(node_id, {})
            lat = node_data.get('lat', 0)
            lon = node_data.get('lon', 0)
            if lat and lon:
                waypoints.append(f"{lat},{lon}")
        
        if len(waypoints) < 2:
            return "https://www.google.com/maps/dir/?api=1&origin=0,0&destination=0,0&travelmode=driving"
        
        # URL oluştur
        origin = waypoints[0]
        destination = waypoints[-1]
        
        params = {
            'api': '1',
            'origin': origin,
            'destination': destination,
            'travelmode': 'driving'
        }
        
        if len(waypoints) > 2:
            params['waypoints'] = "|".join(waypoints[1:-1])
        
        query_string = urllib.parse.urlencode(params)
        return f"https://www.google.com/maps/dir/?{query_string}"


def get_elevation_from_api(lat, lon):
    """
    Yükseklik verisi almak için API kullan
    (Open-Elevation API veya benzeri)
    """
    try:
        # Open-Elevation API
        url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                return data['results'][0].get('elevation', 0)
    except:
        pass
    
    # Varsayılan yükseklik (İstanbul ortalama)
    return 50
