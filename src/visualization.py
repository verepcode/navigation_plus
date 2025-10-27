"""
Görselleştirme Modülü - Rota Analizi ve Grafik Oluşturma
Bu modül API çağrıları ve görselleştirme işlemlerini yönetir.
"""

import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib import gridspec
from datetime import datetime
import json

# Yerel modüller
from database import (VEHICLE_DATABASE, TRAFFIC_ZONES, 
                     get_vehicle_specs, get_all_vehicles, get_fuel_price)
from calculations import (RouteSegmentAnalyzer, FuelConsumptionCalculator)

# Emoji desteği için
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'Segoe UI Emoji']
plt.rcParams['axes.unicode_minus'] = False


class RouteElevationAnalyzer:
    """Google Maps API kullanarak rota yükseklik profili ve yakıt tüketimi analizi"""
    
    def __init__(self, api_key):
        """
        Args:
            api_key (str): Google Maps API anahtarı
        """
        self.api_key = api_key
        self.fuel_calculator = FuelConsumptionCalculator()
        self.segment_analyzer = RouteSegmentAnalyzer()
    
    def get_route(self, origin, destination):
        """
        Google Directions API ile rota bilgisini al
        
        Args:
            origin (str): Başlangıç noktası
            destination (str): Bitiş noktası
            
        Returns:
            dict: Rota bilgileri
        """
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            'origin': origin,
            'destination': destination,
            'mode': 'driving',
            'language': 'tr',
            'key': self.api_key
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Rota alınamadı: {response.status_code}")
            return None
    
    def decode_polyline(self, polyline_string):
        """
        Google'ın encode edilmiş polyline formatını decode et
        
        Args:
            polyline_string (str): Encode edilmiş polyline
            
        Returns:
            list: Koordinat listesi [(lat, lng), ...]
        """
        coordinates = []
        index = 0
        lat = 0
        lng = 0
        
        while index < len(polyline_string):
            shift = 0
            result = 0
            
            while True:
                byte = ord(polyline_string[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if byte < 0x20:
                    break
            
            dlat = ~(result >> 1) if result & 1 else result >> 1
            lat += dlat
            
            shift = 0
            result = 0
            
            while True:
                byte = ord(polyline_string[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if byte < 0x20:
                    break
            
            dlng = ~(result >> 1) if result & 1 else result >> 1
            lng += dlng
            
            coordinates.append((lat * 1e-5, lng * 1e-5))
        
        return coordinates
    
    def sample_points(self, coordinates, num_samples=50):
        """
        Koordinat listesinden uniform örnekler al
        
        Args:
            coordinates (list): Tüm koordinatlar
            num_samples (int): Örnek sayısı
            
        Returns:
            list: Örneklenmiş koordinatlar
        """
        if len(coordinates) <= num_samples:
            return coordinates
        
        indices = np.linspace(0, len(coordinates) - 1, num_samples, dtype=int)
        return [coordinates[i] for i in indices]
    
    def get_elevations(self, coordinates):
        """
        Google Elevation API ile yükseklik bilgilerini al
        
        Args:
            coordinates (list): Koordinat listesi
            
        Returns:
            list: Yükseklik listesi (metre)
        """
        url = "https://maps.googleapis.com/maps/api/elevation/json"
        
        # Koordinatları string formatına çevir
        locations = "|".join([f"{lat},{lng}" for lat, lng in coordinates])
        
        params = {
            'locations': locations,
            'key': self.api_key
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK':
                return [result['elevation'] for result in data['results']]
        
        return None
    
    def calculate_distances(self, coordinates):
        """
        Haversine formülü ile koordinatlar arası mesafeleri hesapla
        
        Args:
            coordinates (list): Koordinat listesi
            
        Returns:
            list: Kümülatif mesafe listesi (km)
        """
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371  # Dünya yarıçapı (km)
            dlat = np.radians(lat2 - lat1)
            dlon = np.radians(lon2 - lon1)
            a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * \
                np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
            c = 2 * np.arcsin(np.sqrt(a))
            return R * c
        
        distances = [0]
        for i in range(1, len(coordinates)):
            lat1, lon1 = coordinates[i-1]
            lat2, lon2 = coordinates[i]
            dist = haversine(lat1, lon1, lat2, lon2)
            distances.append(distances[-1] + dist)
        
        return distances
    
    def analyze_route(self, origin, destination, num_samples=50):
        """
        Rota analizi yap
        
        Args:
            origin (str): Başlangıç noktası
            destination (str): Bitiş noktası
            num_samples (int): Yükseklik örnek sayısı
            
        Returns:
            dict: Analiz sonuçları
        """
        print(f"[ROTA] {origin} -> {destination}")
        print("[API] Google Directions API çağrısı yapılıyor...")
        
        # Rota bilgisini al
        route_data = self.get_route(origin, destination)
        if not route_data or route_data['status'] != 'OK':
            print("[HATA] Rota bulunamadı!")
            return None
        
        # İlk rota
        route = route_data['routes'][0]
        leg = route['legs'][0]
        
        # Polyline'ı decode et
        polyline = route['overview_polyline']['points']
        all_coordinates = self.decode_polyline(polyline)
        
        print(f"[ROTA] Toplam {len(all_coordinates)} nokta bulundu")
        
        # Örnekle
        sampled_coordinates = self.sample_points(all_coordinates, num_samples)
        print(f"[SAMPLE] {len(sampled_coordinates)} nokta örneklendi")
        
        # Yükseklik bilgilerini al
        print("[API] Google Elevation API çağrısı yapılıyor...")
        elevations = self.get_elevations(sampled_coordinates)
        
        if not elevations:
            print("[HATA] Yükseklik bilgisi alınamadı!")
            return None
        
        # Mesafeleri hesapla
        distances = self.calculate_distances(sampled_coordinates)
        
        # İstatistikleri hesapla
        total_distance_km = leg['distance']['value'] / 1000
        total_ascent_m = sum(max(0, elevations[i] - elevations[i-1]) 
                           for i in range(1, len(elevations)))
        total_descent_m = sum(max(0, elevations[i-1] - elevations[i]) 
                            for i in range(1, len(elevations)))
        
        # Ortalama eğim hesapla
        gradients = []
        for i in range(1, len(elevations)):
            if distances[i] != distances[i-1]:
                gradient = (elevations[i] - elevations[i-1]) / \
                          ((distances[i] - distances[i-1]) * 1000) * 100
                gradients.append(gradient)
        
        avg_gradient = np.mean(np.abs(gradients)) if gradients else 0
        
        results = {
            'coordinates': sampled_coordinates,
            'elevations': elevations,
            'distances': distances,
            'total_distance_km': total_distance_km,
            'total_duration_min': leg['duration']['value'] / 60,
            'total_ascent_m': total_ascent_m,
            'total_descent_m': total_descent_m,
            'max_elevation_m': max(elevations),
            'min_elevation_m': min(elevations),
            'avg_gradient': avg_gradient,
            'start_address': leg['start_address'],
            'end_address': leg['end_address']
        }
        
        print(f"[OK] Analiz tamamlandı: {total_distance_km:.2f} km")
        return results
    
    def visualize_route_with_fuel(self, results, vehicle_name, time_of_day='peak', 
                                 save_path='rota_analizi.png', origin_name='', destination_name='', route_info=None):
        """
        Rota, yükseklik profili ve yakıt tüketimi grafiklerini oluştur
        
        Args:
            results (dict): Rota analizi sonuçları
            vehicle_name (str): Araç adı
            time_of_day (str): 'peak' veya 'offpeak'
            save_path (str): Grafik kayıt yolu
            origin_name (str): Başlangıç noktası adı
            destination_name (str): Bitiş noktası adı
            route_info (dict): Google Maps rota bilgisi
        """
        vehicle_specs = get_vehicle_specs(vehicle_name)
        if not vehicle_specs:
            print(f"Araç bulunamadı: {vehicle_name}")
            return
        
        # Yakıt hesaplamaları
        fuel_data = self.fuel_calculator.calculate_fuel_consumption(vehicle_specs, results, time_of_day, route_info)
        capability = self.fuel_calculator.assess_vehicle_capability(vehicle_specs, results)
        
        # Grafik oluştur - Enhanced layout
        fig = plt.figure(figsize=(18, 20))
        gs = gridspec.GridSpec(5, 2, height_ratios=[1.5, 1, 1, 0.8, 0.3], 
                             hspace=0.3, wspace=0.2)
        
        # 1. ROTA HARİTASI (üst panel, tüm genişlik)
        ax_map = fig.add_subplot(gs[0, :])
        
        lats = [coord[0] for coord in results['coordinates']]
        lngs = [coord[1] for coord in results['coordinates']]
        
        # Eğim hesaplama (harita için)
        gradients_map = []
        for i in range(len(results['elevations'])):
            if i == 0:
                gradients_map.append(0)
            else:
                if results['distances'][i] != results['distances'][i-1]:
                    gradient = (results['elevations'][i] - results['elevations'][i-1]) / \
                              ((results['distances'][i] - results['distances'][i-1]) * 1000) * 100
                    gradients_map.append(gradient)
                else:
                    gradients_map.append(0)
        
        # Kritik eğim bölgelerini tespit et
        steep_indices = [i for i, g in enumerate(gradients_map) if abs(g) > 20]
        moderate_steep_indices = [i for i, g in enumerate(gradients_map) if 10 <= abs(g) <= 20]
        
        # Yükseklik renklendirmesi ile rota çizimi
        scatter = ax_map.scatter(lngs, lats, c=results['elevations'], cmap='terrain',
                                s=30, alpha=0.8, edgecolors='black', linewidth=0.5)
        ax_map.plot(lngs, lats, 'b-', linewidth=2, alpha=0.7, label='Rota')
        
        # Orta eğim bölgelerini vurgula
        if moderate_steep_indices:
            mod_lats = [lats[i] for i in moderate_steep_indices]
            mod_lngs = [lngs[i] for i in moderate_steep_indices]
            
            ax_map.scatter(mod_lngs, mod_lats, c='yellow', s=150, 
                        marker='o', edgecolors='orange', linewidth=2,
                        label='Orta Eğim (%10-20)', zorder=4)
        
        # Dik eğim bölgelerini vurgula
        if steep_indices:
            steep_lats = [lats[i] for i in steep_indices]
            steep_lngs = [lngs[i] for i in steep_indices]
            
            ax_map.scatter(steep_lngs, steep_lats, c='red', s=200, 
                          marker='X', edgecolors='darkred', linewidth=2,
                          label='Dik Eğim (>%20)', zorder=5)
        
        # Başlangıç ve bitiş noktaları
        ax_map.plot(lngs[0], lats[0], 'go', markersize=15, label=f'Başlangıç: {origin_name}', 
                   markeredgecolor='black', markeredgewidth=2)
        ax_map.plot(lngs[-1], lats[-1], 'ro', markersize=15, label=f'Varış: {destination_name}',
                   markeredgecolor='black', markeredgewidth=2)
        
        cbar = plt.colorbar(scatter, ax=ax_map, orientation='vertical', pad=0.02)
        cbar.set_label('Yükseklik (m)', fontsize=12, fontweight='bold')
        
        ax_map.set_xlabel('Boylam (°)', fontsize=12, fontweight='bold')
        ax_map.set_ylabel('Enlem (°)', fontsize=12, fontweight='bold')
        ax_map.set_title(f'{origin_name} → {destination_name}\n{vehicle_name} | Zorluk: {capability["difficulty"]}', 
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
        
        ax_grad.set_xlabel('Mesafe (km)', fontsize=12, fontweight='bold')
        ax_grad.set_ylabel('Eğim (%)', fontsize=12, fontweight='bold')
        ax_grad.set_title('Eğim Analizi', fontsize=13, fontweight='bold')
        ax_grad.grid(True, alpha=0.3)
        ax_grad.legend(fontsize=9, loc='best')
        
        # 4. SEGMENT ANALİZİ PANELİ
        ax_segment = fig.add_subplot(gs[3, :])
        
        seg_stats = fuel_data['segment_stats']
        zones = list(seg_stats.keys())
        distances_seg = [seg_stats[z]['distance'] for z in zones]
        fuels = [seg_stats[z]['fuel'] for z in zones]
        
        x = np.arange(len(zones))
        width = 0.35
        
        ax_segment2 = ax_segment.twinx()
        
        bars1 = ax_segment.bar(x - width/2, distances_seg, width, label='Mesafe (km)', 
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
        
        ax_segment.legend(loc='upper left')
        ax_segment2.legend(loc='upper right')
        ax_segment.grid(True, alpha=0.3, axis='y')
        
        # 5. YAKIT TÜKETİMİ BİLGİ PANELİ
        ax_fuel = fig.add_subplot(gs[4, :])
        ax_fuel.axis('off')
        
        fuel_info = f"""
        {vehicle_name} | {vehicle_specs['hp']}HP {vehicle_specs['torque_nm']}Nm | {vehicle_specs['fuel_type']}
        {fuel_data['total_fuel_liters']:.3f}L | {fuel_data['fuel_per_100km']:.2f}L/100km | Yakıt: {fuel_data['fuel_cost_tl']:.2f}TL
        """
        
        # Geçiş ücretleri varsa göster
        if fuel_data.get('toll_cost_tl', 0) > 0:
            fuel_info += f"\n Geçiş Ücreti: {fuel_data['toll_cost_tl']:.2f}TL | Toplam Maliyet: {fuel_data['total_cost_tl']:.2f}TL"
        
        if capability['warnings']:
            fuel_info += f"\n {' | '.join(capability['warnings'][:2])}"
        else:
            fuel_info += "\n Araç bu rota için uygun"
        
        ax_fuel.text(0.5, 0.5, fuel_info, fontsize=10, family='monospace',
                    bbox=dict(boxstyle='round', facecolor='lightyellow', 
                            edgecolor='orange', linewidth=2, alpha=0.9),
                    verticalalignment='center', horizontalalignment='center')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nGrafik kaydedildi: {save_path}")
        plt.show()
    
    def compare_vehicles(self, results, time_of_day='peak', save_path='arac_karsilastirma.png', route_info=None):
        """
        Tüm araçlar için yakıt tüketimi karşılaştırması
        
        Args:
            results (dict): Rota analizi sonuçları
            time_of_day (str): 'peak' veya 'offpeak'
            save_path (str): Grafik kayıt yolu
            route_info (dict): Google Maps rota bilgisi
            
        Returns:
            dict: Araç karşılaştırma sonuçları
        """
        vehicle_results = {}
        
        for vehicle_name, specs in VEHICLE_DATABASE.items():
            fuel_data = self.fuel_calculator.calculate_fuel_consumption(specs, results, time_of_day, route_info)            
            capability = self.fuel_calculator.assess_vehicle_capability(specs, results)
            
            vehicle_results[vehicle_name] = {
                'fuel': fuel_data,
                'capability': capability,
                'specs': specs
            }
        
        # Karşılaştırma grafiği oluştur
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Araç Karşılaştırması - {results["total_distance_km"]:.2f} km Rota\n'
                    f'{time_of_day.upper()} Saatleri', fontsize=16, fontweight='bold')
        
        vehicles = list(vehicle_results.keys())
        
        # 1. Toplam yakıt tüketimi
        fuel_consumption = [vehicle_results[v]['fuel']['total_fuel_liters'] for v in vehicles]
        colors1 = ['green' if f < 3 else 'orange' if f < 5 else 'red' for f in fuel_consumption]
        
        ax1.barh(vehicles, fuel_consumption, color=colors1, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax1.set_xlabel('Toplam Yakıt Tüketimi (Litre)', fontweight='bold')
        ax1.set_title('Toplam Yakıt Tüketimi', fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        for i, v in enumerate(fuel_consumption):
            ax1.text(v + 0.05, i, f'{v:.3f}L', va='center', fontweight='bold')
        
        # 2. 100km başına tüketim
        fuel_per_100 = [vehicle_results[v]['fuel']['fuel_per_100km'] for v in vehicles]
        colors2 = ['green' if f < 5 else 'orange' if f < 7 else 'red' for f in fuel_per_100]
        
        ax2.barh(vehicles, fuel_per_100, color=colors2, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax2.set_xlabel('100km Başına Tüketim (L/100km)', fontweight='bold')
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
        difficulty_map = {'KOLAY': 1, 'ORTA': 2, 'ZOR': 3}
        difficulties = [difficulty_map.get(vehicle_results[v]['capability']['difficulty'], 3) for v in vehicles]
        difficulty_labels = [vehicle_results[v]['capability']['difficulty'] for v in vehicles]
        colors4 = ['green' if d == 1 else 'yellow' if d == 2 else 'red' for d in difficulties]
        
        ax4.barh(vehicles, difficulties, color=colors4, alpha=0.7, edgecolor='black', linewidth=1.5)
        ax4.set_xlabel('Zorluk Seviyesi', fontweight='bold')
        ax4.set_title('Rota Zorluk Değerlendirmesi', fontweight='bold')
        ax4.set_xticks([1, 2, 3])
        ax4.set_xticklabels(['KOLAY', 'ORTA', 'ZOR'])
        ax4.grid(axis='x', alpha=0.3)
        
        for i, label in enumerate(difficulty_labels):
            ax4.text(difficulties[i] + 0.1, i, label, va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nKarşılaştırma grafiği kaydedildi: {save_path}")
        plt.show()
        
        return vehicle_results
    
    def print_detailed_report(self, results, vehicle_name=None, time_of_day='peak'):
        """
        Detaylı analiz raporu yazdır
        
        Args:
            results (dict): Rota analizi sonuçları
            vehicle_name (str): Araç adı (opsiyonel)
            time_of_day (str): 'peak' veya 'offpeak'
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
        print(f"Trafik Durumu: {'YOĞUN SAAT' if time_of_day == 'peak' else 'SEYREK SAAT'}")
        print(f"\n📍 ROTA BİLGİLERİ:")
        print(f"Toplam Mesafe: {results['total_distance_km']:.2f} km")
        print(f"Tahmini Süre: {results['total_duration_min']:.0f} dakika")
        print(f"En Düşük Yükseklik: {results['min_elevation_m']:.1f} m")
        print(f"En Yüksek Yükseklik: {results['max_elevation_m']:.1f} m")
        print(f"Yükseklik Farkı: {results['max_elevation_m'] - results['min_elevation_m']:.1f} m")
        print(f"Toplam Tırmanış: {results['total_ascent_m']:.1f} m")
        print(f"Toplam İniş: {results['total_descent_m']:.1f} m")
        print(f"Ortalama Eğim: {results['avg_gradient']:.2f}%")
        
        # Kritik eğim bölgeleri
        if steep_sections:
            print("\n KRİTİK EĞİM BÖLGELERİ (%20'nin Üzeri)")
            print("="*80)
            
            for idx, section in enumerate(steep_sections, 1):
                eğim_tipi = "TIRMANIŞ" if section['gradient'] > 0 else "İNİŞ"
                print(f"\n{idx}. Bölge - {eğim_tipi}")
                print(f"   Mesafe: {section['distance_km']:.3f} km")
                print(f"   Eğim: {abs(section['gradient']):.1f}%")
                print(f"   Yükseklik: {section['elevation']:.1f} m")
                print(f"   Koordinat: {section['lat']:.6f}°, {section['lng']:.6f}°")
                print(f"   Google Maps: https://www.google.com/maps?q={section['lat']},{section['lng']}")
        
        # Araç özel rapor
        if vehicle_name:
            print("\n" + "="*80)
            print(f"🚗 ARAÇ ÖZEL ANALİZ: {vehicle_name}")
            print("="*80)
            
            specs = get_vehicle_specs(vehicle_name)
            if specs:
                fuel_data = self.fuel_calculator.calculate_fuel_consumption(specs, results, time_of_day)
                capability = self.fuel_calculator.assess_vehicle_capability(specs, results)
                
                print(f"\n Araç Özellikleri:")
                print(f"Motor Gücü: {specs['hp']} HP")
                print(f"Tork: {specs['torque_nm']} Nm")
                print(f"Ağırlık: {specs['weight_kg']} kg")
                print(f"Motor Hacmi: {specs['engine_cc']} cc")
                print(f"Yakıt Tipi: {specs['fuel_type']}")
                
                print(f"\n Yakıt Tahmini ({time_of_day.upper()} saatleri):")
                print(f"Toplam Tüketim: {fuel_data['total_fuel_liters']:.3f} Litre")
                print(f"100km Başına: {fuel_data['fuel_per_100km']:.2f} L/100km")
                print(f"Tahmini Maliyet: {fuel_data['fuel_cost_tl']:.2f} TL")
                
                print(f"\n Segment Bazlı Analiz:")
                for zone, data in fuel_data['segment_stats'].items():
                    if data['distance'] > 0:
                        zone_info = TRAFFIC_ZONES[zone]
                        avg_speed = zone_info['avg_speed_peak'] if time_of_day == 'peak' else zone_info['avg_speed_offpeak']
                        print(f"  {zone}: {data['distance']:.2f}km | Ort. Hız: {avg_speed}km/h | Yakıt: {data['fuel']:.3f}L")
                
                print(f"\n Performans Analizi:")
                print(f"Güç/Ağırlık: {capability['power_to_weight']:.3f} HP/kg")
                print(f"Tork/Ağırlık: {capability['torque_to_weight']:.3f} Nm/kg")
                print(f"Rota Zorluğu: {capability['difficulty']}")
                
                if capability['warnings']:
                    print(f"\n Uyarılar:")
                    for warning in capability['warnings']:
                        print(f"  {warning}")
                else:
                    print("\n Bu rota için araç performansı yeterli.")
        
        print("\n" + "="*80)