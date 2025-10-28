"""
Görselleştirme Modülü - Rota Analizi ve Grafik Oluşturma (Geliştirilmiş)
Bu modül API çağrıları, alternatif rota analizi ve görselleştirme işlemlerini yönetir.
"""

import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib import gridspec
from datetime import datetime
import json

# Yerel modüller
from database import (VEHICLE_DATABASE, TRAFFIC_ZONES, 
                     get_vehicle_specs, get_all_vehicles, get_fuel_price)
from calculations import (RouteSegmentAnalyzer, FuelConsumptionCalculator, 
                                   AlternativeRouteOptimizer)

# Emoji desteği için
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'Segoe UI Emoji']
plt.rcParams['axes.unicode_minus'] = False


class RouteElevationAnalyzer:
    """Google Maps API kullanarak rota yükseklik profili ve yakıt tüketimi analizi"""
    # GERÇEKÇI SİSTEM SABITLERI
    ACCEPTABLE_EXTRA_PERCENT = 0.20  # %20 ekstra mesafe limiti
    CRITICAL_SLOPE_THRESHOLD = 15    # %15 kritik eğim eşiği
    def __init__(self, api_key):
        """
        Args:
            api_key (str): Google Maps API anahtarı
        """
        self.api_key = api_key
        self.fuel_calculator = FuelConsumptionCalculator()
        self.segment_analyzer = RouteSegmentAnalyzer()
        self.alternative_optimizer = AlternativeRouteOptimizer(api_key)
    
    def get_route(self, origin, destination, alternatives=False):
        """
        Google Directions API ile rota bilgisini al
        
        Args:
            origin (str): Başlangıç noktası
            destination (str): Bitiş noktası
            alternatives (bool): Alternatif rotalar iste
            
        Returns:
            dict: Rota bilgileri
        """
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            'origin': origin,
            'destination': destination,
            'mode': 'driving',
            'language': 'tr',
            'alternatives': 'true' if alternatives else 'false',
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
    
        
    def generate_google_maps_link(self, origin, destination, waypoints=None):
        """Google Maps linki oluştur"""
        import urllib.parse
        
        base_url = "https://www.google.com/maps/dir/"
        encoded_origin = urllib.parse.quote(origin)
        encoded_destination = urllib.parse.quote(destination)
        
        if waypoints:
            # Waypoint'li link
            encoded_waypoints = [urllib.parse.quote(wp) for wp in waypoints]
            all_points = [encoded_origin] + encoded_waypoints + [encoded_destination]
            url = base_url + "/".join(all_points)
        else:
            # Basit link
            url = f"{base_url}{encoded_origin}/{encoded_destination}"
        
        return url
    
    def analyze_route(self, origin, destination, num_samples=50, include_alternatives=True):
        """
        Rota analizi yap (orijinal ve alternatif rotalar)
        
        Args:
            origin (str): Başlangıç noktası
            destination (str): Bitiş noktası
            num_samples (int): Yükseklik örnek sayısı
            include_alternatives (bool): Alternatif rotaları analiz et
            
        Returns:
            dict: Analiz sonuçları (orijinal ve alternatif rotalar)
        """
        print(f"[ROTA] {origin} -> {destination}")
        print("[API] Google Directions API çağrısı yapılıyor...")
        
        # Rota bilgisini al (alternatifler dahil)
        route_data = self.get_route(origin, destination, alternatives=include_alternatives)
        
        if not route_data or route_data.get('status') != 'OK':
            print(f"❌ Hata: {route_data.get('status', 'Bilinmeyen hata')}")
            return None
        
        all_route_analyses = []
        
        # Tüm rotaları analiz et
        routes = route_data.get('routes', [])
        print(f"[BİLGİ] {len(routes)} rota bulundu")
        
        for idx, route in enumerate(routes):
            route_name = "ORİJİNAL ROTA" if idx == 0 else f"ALTERNATİF ROTA {idx}"
            print(f"\n[ANALİZ] {route_name} analiz ediliyor...")
            
            # Polyline'ı decode et
            polyline = route['overview_polyline']['points']
            all_coordinates = self.decode_polyline(polyline)
            
            # Koordinatları örnekle
            sampled_coordinates = self.sample_points(all_coordinates, num_samples)
            print(f"[SAMPLE] {len(all_coordinates)} noktadan {len(sampled_coordinates)} örnek alındı")
            
            # Yükseklik bilgilerini al
            print("[API] Google Elevation API çağrısı yapılıyor...")
            elevations = self.get_elevations(sampled_coordinates)
            
            if not elevations:
                print("❌ Yükseklik bilgileri alınamadı!")
                continue
            
            # Mesafeleri hesapla
            distances = self.calculate_distances(sampled_coordinates)
            
            # İstatistikler
            total_ascent = sum([max(0, elevations[i] - elevations[i-1]) 
                              for i in range(1, len(elevations))])
            total_descent = sum([max(0, elevations[i-1] - elevations[i]) 
                               for i in range(1, len(elevations))])
            
            # Eğim hesapla
            gradients = [0]
            for i in range(1, len(elevations)):
                if distances[i] != distances[i-1]:
                    gradient = (elevations[i] - elevations[i-1]) / \
                              ((distances[i] - distances[i-1]) * 1000) * 100
                    gradients.append(gradient)
                else:
                    gradients.append(0)
            
            # Rota özet bilgileri
            leg = route['legs'][0]
            
            # Segmentleri analiz et ve kritik bölgeleri tespit et
            segments = self.segment_analyzer.classify_route_segments(
                sampled_coordinates, elevations, distances, route
            )
            critical_sections = self.segment_analyzer.identify_critical_sections(segments)
            
            route_analysis = {
                'route_name': route_name,
                'route_index': idx,
                'is_original': idx == 0,
                'summary': route.get('summary', route_name),
                'coordinates': sampled_coordinates,
                'elevations': elevations,
                'distances': distances,
                'gradients': gradients,
                'total_distance_km': distances[-1],
                'total_duration_min': leg['duration']['value'] / 60,
                'min_elevation_m': min(elevations),
                'max_elevation_m': max(elevations),
                'total_ascent_m': total_ascent,
                'total_descent_m': total_descent,
                'avg_gradient': np.mean([abs(g) for g in gradients]),
                'max_gradient': max([abs(g) for g in gradients]),
                'segments': segments,
                'critical_sections': critical_sections,
                'has_critical_sections': len(critical_sections) > 0,
                'route_data': route
            }
            
            all_route_analyses.append(route_analysis)
            
            print(f"✓ {route_name} analizi tamamlandı")
            print(f"  Mesafe: {route_analysis['total_distance_km']:.2f} km")
            print(f"  Süre: {route_analysis['total_duration_min']:.0f} dakika")
            print(f"  Kritik bölge sayısı: {len(critical_sections)}")
        
        if not all_route_analyses:
            return None
        
        # Sonuçları döndür
        result = {
            'origin': origin,
            'destination': destination,
            'timestamp': datetime.now(),
            'routes': all_route_analyses,
            'original_route': all_route_analyses[0] if all_route_analyses else None,
            'alternative_routes': all_route_analyses[1:] if len(all_route_analyses) > 1 else []
        }
        
        print("\n✓ Tüm rotalar analiz edildi!")
        return result
    
    def compare_routes(self, route_analyses, vehicle_name, time_of_day='peak'):
        """
        Tüm rotaları karşılaştır (yakıt tüketimi, maliyet, kritik bölgeler)
        
        Args:
            route_analyses (dict): Rota analizleri
            vehicle_name (str): Araç adı
            time_of_day (str): 'peak' veya 'offpeak'
            
        Returns:
            dict: Karşılaştırma sonuçları
        """
        if not route_analyses or 'routes' not in route_analyses:
            return None
        
        vehicle_specs = get_vehicle_specs(vehicle_name)
        if not vehicle_specs:
            return None
        
        comparisons = []
        
        for route in route_analyses['routes']:
            # Yakıt tüketimi hesapla
            fuel_data = self.fuel_calculator.calculate_fuel_consumption(
                vehicle_specs, route, time_of_day, route['route_data']
            )
            
            # Performans değerlendirmesi
            capability = self.fuel_calculator.assess_vehicle_capability(vehicle_specs, route)
            
            comparisons.append({
                'route_name': route['route_name'],
                'summary': route['summary'],
                'distance_km': route['total_distance_km'],
                'duration_min': route['total_duration_min'],
                'fuel_consumption': fuel_data,
                'capability': capability,
                'critical_sections_count': len(route['critical_sections']),
                'max_gradient': route['max_gradient'],
                'is_recommended': False  # Sonra belirlenecek
            })
        
        # En iyi rotayı belirle (çok kriterli analiz)
        if comparisons:
            # Skorlama: düşük yakıt + düşük maliyet + az kritik bölge + kolay zorluk
            difficulty_score = {'KOLAY': 0, 'ORTA': 1, 'ZOR': 2, 'ÇOK ZOR': 3}
            
            for comp in comparisons:
                score = 0
                # Yakıt tüketimi (normalize edilmiş)
                score += comp['fuel_consumption']['fuel_per_100km'] * 10
                # Toplam maliyet
                score += comp['fuel_consumption']['total_cost_tl'] / 10
                # Kritik bölge sayısı
                score += comp['critical_sections_count'] * 50
                # Zorluk
                score += difficulty_score.get(comp['capability']['difficulty'], 2) * 20
                
                comp['score'] = score
            
            # GERÇEKÇI SİSTEM KONTROLÜ
            # 1. Güvenli rotaları bul (kritik eğim yok)
            safe_routes = [c for c in comparisons if c['critical_sections_count'] == 0]
            
            if safe_routes:
                # Güvenli rotalar var - en iyisini seç
                best_route = min(safe_routes, key=lambda x: x['score'])
                best_route['is_recommended'] = True
                unavoidable_critical = False
            else:
                # Hiçbir güvenli rota yok - gerçekçi limit kontrolü
                shortest_route = min(comparisons, key=lambda x: x['distance_km'])
                max_acceptable_distance = shortest_route['distance_km'] * (1 + self.ACCEPTABLE_EXTRA_PERCENT)
                
                # Kabul edilebilir mesafedeki rotalar   
                acceptable_routes = [
                    c for c in comparisons 
                    if c['distance_km'] <= max_acceptable_distance
                ]
                
                if not acceptable_routes:
                    # Hiçbiri kabul edilebilir değil - sadece en kısayı al
                    acceptable_routes = [shortest_route]
                
                # Kabul edilebilir rotalar içinden en az kötüsünü seç
                best_route = min(acceptable_routes, key=lambda x: x['score'])
                best_route['is_recommended'] = True
                unavoidable_critical = True  # Kritik eğim kaçınılmaz
            
                # Google Maps linki oluştur
                origin = route_analyses.get('origin', '')
                destination = route_analyses.get('destination', '')
                google_maps_link = self.generate_google_maps_link(origin, destination) if origin and destination else None
                
            # GERÇEKÇI SİSTEM ÇIKTILARINI EKLE
            result = {
                'vehicle': vehicle_name,
                'time_of_day': time_of_day,
                'comparisons': comparisons,
                'recommended_route': best_route if comparisons else None,
                'google_maps_link': google_maps_link,      # EKLENDI
                'origin': origin,                            # EKLENDI
                'destination': destination                   # EKLENDI
            }
            
            # Kritik eğim durumu analizi
            if comparisons:
                result['unavoidable_critical'] = unavoidable_critical
                
                if unavoidable_critical:
                    # Kritik eğim kaçınılmaz - ek bilgiler ekle
                    result['warning'] = {
                        'message': 'Bu güzergahta kritik eğim kaçınılmaz',
                        'reason': self._explain_why_unavoidable(route_analyses),
                        'driving_tips': self._get_driving_tips(vehicle_specs, best_route),
                        'alternatives': self._suggest_alternatives(best_route)
                    }
            
            return result

    def _explain_why_unavoidable(self, route_analyses):
        """
        Kritik eğimin neden kaçınılmaz olduğunu açıkla
        """
        if not route_analyses or 'routes' not in route_analyses:
            return "Rota bilgisi yok"
        
        routes = route_analyses['routes']
        if not routes:
            return "Rota bulunamadı"
        
        # İlk rotanın yükseklik bilgilerini al
        first_route = routes[0]
        elevation_gain = first_route.get('total_ascent_m', 0)
        distance_km = first_route.get('total_distance_km', 0)
        
        if elevation_gain > 0 and distance_km > 0:
            avg_slope = (elevation_gain / (distance_km * 1000)) * 100
            
            return (
                f"Bu güzergahta {elevation_gain:.0f}m yükseklik farkı var. "
                f"{distance_km:.1f}km mesafede bu kadar yükselmek "
                f"fiziksel olarak kritik eğim gerektiriyor "
                f"(ortalama %{avg_slope:.1f} eğim)."
            )
        
        return "Yükseklik farkı nedeniyle kritik eğim kaçınılmaz"
    
    def _get_driving_tips(self, vehicle_specs, route_comparison):
        """
        Kritik eğimde sürüş ipuçları
        """
        tips = []
        
        # Temel ipuçları
        tips.append("1. veya 2. vites kullanın")
        tips.append("Motor devrini 2000+ rpm tutun")
        tips.append("Rampalarda 3-4 araç mesafe bırakın")
        tips.append("Ani gaz vermekten kaçının")
        
        # Araç özelliğine göre
        if vehicle_specs.get('hp', 0) < 100:
            tips.append("Motorunuz düşük güçlü - özellikle dikkatli olun")
        
        # Zorluk seviyesine göre
        difficulty = route_comparison.get('capability', {}).get('difficulty', 'ORTA')
        if difficulty == 'ÇOK ZOR':
            tips.append("Bu rota çok zorlu - alternatif düşünün (taksi, yürüyüş)")
        
        # Trafik durumuna göre
        tips.append("Mümkünse trafiksiz saatlerde gidin (14:00-16:00)")
        
        return tips
    
    def _suggest_alternatives(self, route_comparison):
        """
        Alternatif çözüm önerileri
        """
        distance_km = route_comparison.get('distance_km', 0)
        
        alternatives = []
        
        # Taksi önerisi
        taxi_cost = distance_km * 25  # Ortalama 25 TL/km
        alternatives.append({
            'type': 'taxi',
            'description': 'Taksi kullanın',
            'cost': f"~{taxi_cost:.0f} TL",
            'benefit': 'Motor zorlanmaz, güvenli varış',
            'duration': 'Aynı süre'
        })
        
        # Yürüyüş önerisi
        walk_time = distance_km * 12  # Ortalama 12 dk/km
        alternatives.append({
            'type': 'walking',
            'description': 'Yürüyerek gidin',
            'cost': '0 TL',
            'benefit': 'En güvenli yöntem + egzersiz',
            'duration': f"~{walk_time:.0f} dakika"
        })
        
        # Farklı araç önerisi
        alternatives.append({
            'type': 'different_vehicle',
            'description': 'Daha güçlü araç kullanın',
            'suggestions': ['SUV', 'Turbo motor', '4x4', 'Elektrikli (yüksek tork)'],
            'benefit': 'Daha güçlü motor, kolay tırmanış'
        })
        
        # Farklı zaman önerisi
        alternatives.append({
            'type': 'different_time',
            'description': 'Trafiksiz saatte gidin',
            'suggestions': ['14:00-16:00 (Öğlen arası)', 'Erken sabah (06:00-08:00)'],
            'benefit': 'Rampa kalkış riski azalır, trafik stres yok'
        })
        
        # Yolcu indirme önerisi (kısa mesafelerde)
        if distance_km < 10:
            alternatives.append({
                'type': 'reduce_weight',
                'description': 'Yolcuları indirin',
                'benefit': 'Daha hafif araç = daha kolay tırmanış',
                'note': 'Yolcular yürüyerek veya taksiyle gelebilir'
            })
        
        return alternatives
    
    def visualize_route_comparison(self, route_analyses, vehicle_name, time_of_day='peak',
                                   save_path='route_comparison.png'):
        """
        Orijinal ve alternatif rotaları görselleştir ve karşılaştır
        
        Args:
            route_analyses (dict): Rota analizleri
            vehicle_name (str): Araç adı
            time_of_day (str): 'peak' veya 'offpeak'
            save_path (str): Kayıt yolu
        """
        if not route_analyses or 'routes' not in route_analyses:
            print("Görselleştirilecek rota bulunamadı!")
            return
        
        comparison = self.compare_routes(route_analyses, vehicle_name, time_of_day)
        if not comparison:
            print("Karşılaştırma yapılamadı!")
            return
        
        routes = route_analyses['routes']
        comparisons = comparison['comparisons']
        
        # Grafik oluştur
        fig = plt.figure(figsize=(20, 12))
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # Başlık
        fig.suptitle(f'ROTA KARŞILAŞTIRMASI - {vehicle_name}\n'
                    f'{route_analyses["origin"]} → {route_analyses["destination"]}',
                    fontsize=16, fontweight='bold')
        
        # Renk paleti
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
        
        # 1. Yükseklik profilleri
        ax1 = fig.add_subplot(gs[0, :])
        for idx, (route, comp) in enumerate(zip(routes, comparisons)):
            color = colors[idx % len(colors)]
            label = f"{route['route_name']}"
            if comp['is_recommended']:
                label += " ⭐ ÖNERİLEN"
            
            ax1.plot(route['distances'], route['elevations'], 
                    label=label, linewidth=2.5, color=color, alpha=0.8)
            
            # Kritik bölgeleri işaretle
            for section in route['critical_sections']:
                seg_idx = section['segment_index']
                if seg_idx < len(route['distances']):
                    ax1.scatter(route['distances'][seg_idx], route['elevations'][seg_idx],
                              s=150, c='red', marker='X', edgecolors='black', 
                              linewidths=1.5, zorder=5)
        
        ax1.set_xlabel('Mesafe (km)', fontweight='bold', fontsize=11)
        ax1.set_ylabel('Yükseklik (m)', fontweight='bold', fontsize=11)
        ax1.set_title('Yükseklik Profilleri ve Kritik Bölgeler', fontweight='bold', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='best', fontsize=9)
        ax1.fill_between(routes[0]['distances'], 
                        min([min(r['elevations']) for r in routes]) - 10,
                        routes[0]['elevations'], alpha=0.1, color='gray')
        
        # 2. Yakıt tüketimi karşılaştırması
        ax2 = fig.add_subplot(gs[1, 0])
        route_names = [c['route_name'].replace('ROTA', 'R.') for c in comparisons]
        fuel_consumption = [c['fuel_consumption']['total_fuel_liters'] for c in comparisons]
        bar_colors = [colors[i % len(colors)] for i in range(len(comparisons))]
        
        bars = ax2.bar(range(len(route_names)), fuel_consumption, color=bar_colors, 
                      alpha=0.7, edgecolor='black', linewidth=1.5)
        
        # Önerilen rotayı vurgula
        for i, comp in enumerate(comparisons):
            if comp['is_recommended']:
                bars[i].set_edgecolor('gold')
                bars[i].set_linewidth(3)
        
        ax2.set_xticks(range(len(route_names)))
        ax2.set_xticklabels(route_names, rotation=45, ha='right', fontsize=9)
        ax2.set_ylabel('Yakıt (Litre)', fontweight='bold')
        ax2.set_title('Toplam Yakıt Tüketimi', fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(fuel_consumption):
            ax2.text(i, v + 0.05, f'{v:.2f}L', ha='center', fontweight='bold', fontsize=9)
        
        # 3. Maliyet karşılaştırması
        ax3 = fig.add_subplot(gs[1, 1])
        total_costs = [c['fuel_consumption']['total_cost_tl'] for c in comparisons]
        
        bars = ax3.bar(range(len(route_names)), total_costs, color=bar_colors,
                      alpha=0.7, edgecolor='black', linewidth=1.5)
        
        for i, comp in enumerate(comparisons):
            if comp['is_recommended']:
                bars[i].set_edgecolor('gold')
                bars[i].set_linewidth(3)
        
        ax3.set_xticks(range(len(route_names)))
        ax3.set_xticklabels(route_names, rotation=45, ha='right', fontsize=9)
        ax3.set_ylabel('Maliyet (TL)', fontweight='bold')
        ax3.set_title('Toplam Maliyet (Yakıt + Geçiş)', fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(total_costs):
            ax3.text(i, v + 1, f'{v:.1f}₺', ha='center', fontweight='bold', fontsize=9)
        
        # 4. Kritik bölge sayısı
        ax4 = fig.add_subplot(gs[1, 2])
        critical_counts = [c['critical_sections_count'] for c in comparisons]
        
        bars = ax4.bar(range(len(route_names)), critical_counts, color=bar_colors,
                      alpha=0.7, edgecolor='black', linewidth=1.5)
        
        for i, comp in enumerate(comparisons):
            if comp['is_recommended']:
                bars[i].set_edgecolor('gold')
                bars[i].set_linewidth(3)
        
        ax4.set_xticks(range(len(route_names)))
        ax4.set_xticklabels(route_names, rotation=45, ha='right', fontsize=9)
        ax4.set_ylabel('Kritik Bölge Sayısı', fontweight='bold')
        ax4.set_title('Kritik Eğim Bölgeleri (>%15)', fontweight='bold')
        ax4.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(critical_counts):
            if v > 0:
                ax4.text(i, v + 0.1, str(v), ha='center', fontweight='bold', fontsize=10)
        
        # 5. Detaylı karşılaştırma tablosu
        ax5 = fig.add_subplot(gs[2, :])
        ax5.axis('off')
        
        # Tablo verileri
        table_data = []
        headers = ['Rota', 'Mesafe\n(km)', 'Süre\n(dk)', 'Yakıt\n(L)', 
                  'Maliyet\n(TL)', 'Kritik\nBölge', 'Maks.\nEğim (%)', 'Zorluk']
        
        for comp in comparisons:
            row = [
                comp['route_name'].replace(' ROTA', ''),
                f"{comp['distance_km']:.1f}",
                f"{comp['duration_min']:.0f}",
                f"{comp['fuel_consumption']['total_fuel_liters']:.2f}",
                f"{comp['fuel_consumption']['total_cost_tl']:.1f}",
                str(comp['critical_sections_count']),
                f"{comp['max_gradient']:.1f}",
                comp['capability']['difficulty']
            ]
            
            # Önerilen rotayı işaretle
            if comp['is_recommended']:
                row[0] += " ⭐"
            
            table_data.append(row)
        
        table = ax5.table(cellText=table_data, colLabels=headers,
                         cellLoc='center', loc='center',
                         colWidths=[0.15, 0.1, 0.1, 0.1, 0.1, 0.1, 0.12, 0.13])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2.5)
        
        # Başlık satırını vurgula
        for i in range(len(headers)):
            table[(0, i)].set_facecolor('#2E86AB')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Önerilen rotayı vurgula
        for i, comp in enumerate(comparisons):
            if comp['is_recommended']:
                for j in range(len(headers)):
                    table[(i+1, j)].set_facecolor('#FFD700')
                    table[(i+1, j)].set_alpha(0.3)
        
        # Bilgi kutusu
        info_text = f"Araç: {vehicle_name}\n"
        info_text += f"Trafik: {'YOĞUN' if time_of_day == 'peak' else 'SEYREK'} SAAT\n"
        info_text += f"Analiz: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        info_text += f"\n⭐ = ÖNERİLEN ROTA (En düşük maliyet + En az kritik bölge)"
        
        ax5.text(0.02, 0.98, info_text, transform=ax5.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n✓ Karşılaştırma grafiği kaydedildi: {save_path}")
        plt.show()
    
    def print_route_comparison_report(self, route_analyses, vehicle_name, time_of_day='peak'):
        """
        Detaylı rota karşılaştırma raporu yazdır
        
        Args:
            route_analyses (dict): Rota analizleri
            vehicle_name (str): Araç adı
            time_of_day (str): 'peak' veya 'offpeak'
        """
        comparison = self.compare_routes(route_analyses, vehicle_name, time_of_day)
        if not comparison:
            print("Karşılaştırma yapılamadı!")
            return
        
        print("\n" + "="*80)
        print("DETAYLI ROTA KARŞILAŞTIRMA RAPORU")
        print("="*80)
        print(f"Araç: {vehicle_name}")
        print(f"Trafik Durumu: {'YOĞUN SAAT' if time_of_day == 'peak' else 'SEYREK SAAT'}")
        print(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        
        for i, comp in enumerate(comparison['comparisons'], 1):
            print(f"\n{'-'*80}")
            print(f"ROTA {i}: {comp['route_name']}")
            if comp['is_recommended']:
                print("⭐ ÖNERİLEN ROTA")
            print(f"Özet: {comp['summary']}")
            print(f"{'-'*80}")
            
            print(f"\n📍 Rota Bilgileri:")
            print(f"  Mesafe: {comp['distance_km']:.2f} km")
            print(f"  Süre: {comp['duration_min']:.0f} dakika")
            print(f"  Maksimum Eğim: {comp['max_gradient']:.1f}%")
            
            print(f"\n⛽ Yakıt Tüketimi:")
            print(f"  Toplam: {comp['fuel_consumption']['total_fuel_liters']:.3f} Litre")
            print(f"  100km Başına: {comp['fuel_consumption']['fuel_per_100km']:.2f} L/100km")
            print(f"  Yakıt Maliyeti: {comp['fuel_consumption']['fuel_cost_tl']:.2f} TL")
            print(f"  Geçiş Ücreti: {comp['fuel_consumption']['toll_cost_tl']:.2f} TL")
            print(f"  Toplam Maliyet: {comp['fuel_consumption']['total_cost_tl']:.2f} TL")
            
            print(f"\n🎯 Performans:")
            print(f"  Zorluk: {comp['capability']['difficulty']}")
            print(f"  Kritik Bölge Sayısı: {comp['critical_sections_count']}")
            
            if comp['capability']['warnings']:
                print(f"\n⚠️  Uyarılar:")
                for warning in comp['capability']['warnings']:
                    print(f"  {warning}")
        
        # Öneri
        if comparison['recommended_route']:
            rec = comparison['recommended_route']
            print(f"\n{'='*80}")
            print("📊 ÖNERİ:")
            print(f"{'='*80}")
            print(f"En iyi seçim: {rec['route_name']}")
            print(f"Neden: Toplam {rec['critical_sections_count']} kritik bölge, ")
            print(f"       {rec['fuel_consumption']['total_cost_tl']:.2f} TL maliyet,")
            print(f"       {rec['capability']['difficulty']} zorluk seviyesi")
        
        print(f"\n{'='*80}\n")

    # Mevcut metodlar buraya eklenmeye devam edebilir...
    # (Orijinal dosyadaki diğer metodlar aynı kalabilir)
