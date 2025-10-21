import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from datetime import datetime

class RouteElevationAnalyzer:
    def __init__(self, google_api_key=None):
        """
        Rota yükseklik analizi için sınıf
        
        Args:
            google_api_key: Google Maps API anahtarı (opsiyonel, Open-Elevation kullanılabilir)
        """
        self.google_api_key = google_api_key
        self.use_open_elevation = google_api_key is None
        
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
    
    def visualize_route(self, results, save_path='rota_analizi.png'):
        """
        Rota analizini harita ile birlikte görselleştir
        """
        fig = plt.figure(figsize=(16, 12))
        
        # Grid layout oluştur
        gs = fig.add_gridspec(3, 2, height_ratios=[2, 1, 1], hspace=0.3, wspace=0.3)
        
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
        
        # 1. HAİTA - Rota görünümü (üstte, geniş)
        ax_map = fig.add_subplot(gs[0, :])
        
        # Yüksekliğe göre renklendirme
        scatter = ax_map.scatter(lngs, lats, c=elevations, cmap='terrain', 
                                s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
        
        # Rota çizgisini çiz
        ax_map.plot(lngs, lats, 'b-', linewidth=2, alpha=0.7, label='Rota')
        
        # %20'yi aşan dik eğim bölgelerini vurgula
        if steep_indices:
            steep_lats = [lats[i] for i in steep_indices]
            steep_lngs = [lngs[i] for i in steep_indices]
            steep_grads = [gradients_map[i] for i in steep_indices]
            
            ax_map.scatter(steep_lngs, steep_lats, c='red', s=200, 
                          marker='X', edgecolors='darkred', linewidth=2,
                          label='Dik Eğim (>%20)', zorder=5)
            
            # Her dik eğim noktasını etiketle
            for i, idx in enumerate(steep_indices):
                ax_map.annotate(f'{abs(gradients_map[idx]):.1f}%', 
                              (steep_lngs[i], steep_lats[i]),
                              xytext=(10, 10), textcoords='offset points',
                              bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8),
                              fontsize=9, fontweight='bold',
                              arrowprops=dict(arrowstyle='->', color='red', lw=2))
        
        # Başlangıç ve bitiş noktaları
        ax_map.plot(lngs[0], lats[0], 'go', markersize=15, label='Başlangıç: Maltepe', 
                   markeredgecolor='black', markeredgewidth=2)
        ax_map.plot(lngs[-1], lats[-1], 'ro', markersize=15, label='Varış: Aydos Ormanı',
                   markeredgecolor='black', markeredgewidth=2)
        
        # Yükseklik renk çubuğu
        cbar = plt.colorbar(scatter, ax=ax_map, orientation='vertical', pad=0.02)
        cbar.set_label('Yükseklik (m)', fontsize=12, fontweight='bold')
        
        ax_map.set_xlabel('Boylam (°)', fontsize=12, fontweight='bold')
        ax_map.set_ylabel('Enlem (°)', fontsize=12, fontweight='bold')
        ax_map.set_title('Maltepe Tınaztepe Sokak → Aydos Ormanı Rota Haritası', 
                        fontsize=14, fontweight='bold')
        ax_map.grid(True, alpha=0.3, linestyle='--')
        ax_map.legend(loc='upper left', fontsize=10)
        ax_map.set_aspect('equal', adjustable='box')
        
        # 2. YÜKSEKLİK PROFİLİ (sol alt)
        ax_elev = fig.add_subplot(gs[1, :])
        
        ax_elev.plot(results['distances'], results['elevations'], 'b-', linewidth=2.5)
        ax_elev.fill_between(results['distances'], results['elevations'], 
                            alpha=0.3, color='skyblue')
        
        # Min/Max noktalarını işaretle
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
        
        # 3. EĞİM ANALİZİ (sağ alt)
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
        ax_grad.legend(fontsize=10)
        
        # İstatistik kutusu ekle
        stats_text = f"""
        📊 ROTA İSTATİSTİKLERİ
        {'='*30}
        Toplam Mesafe: {results['total_distance_km']:.2f} km
        Yükseklik Farkı: {results['max_elevation_m'] - results['min_elevation_m']:.1f} m
        Toplam Tırmanış: {results['total_ascent_m']:.1f} m
        Toplam İniş: {results['total_descent_m']:.1f} m
        Ortalama Eğim: {results['avg_gradient']:.2f}%
        """
        
        fig.text(0.98, 0.02, stats_text, fontsize=9, family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                verticalalignment='bottom', horizontalalignment='right')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nGrafik kaydedildi: {save_path}")
        plt.show()
    
    def print_report(self, results):
        """
        Analiz raporunu yazdır
        """
        print("\n" + "="*60)
        print("ROTA ANALİZ RAPORU")
        print("="*60)
        print(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        print(f"\nToplam Mesafe: {results['total_distance_km']:.2f} km")
        print(f"En Düşük Yükseklik: {results['min_elevation_m']:.1f} m")
        print(f"En Yüksek Yükseklik: {results['max_elevation_m']:.1f} m")
        print(f"Yükseklik Farkı: {results['max_elevation_m'] - results['min_elevation_m']:.1f} m")
        print(f"\nToplam Tırmanış: {results['total_ascent_m']:.1f} m")
        print(f"Toplam İniş: {results['total_descent_m']:.1f} m")
        print(f"Ortalama Eğim: {results['avg_gradient']:.2f}%")
        print("="*60)


# KULLANIM ÖRNEĞİ
if __name__ == "__main__":
    # API key olmadan kullanım (Open-Elevation API ile)
    key = "AIzaSyDFkQuhvtavuFNPvnrlEFZcbh30BarQ-l4"
    analyzer = RouteElevationAnalyzer(key)
    
    # Google API key ile kullanım (varsa)
    # analyzer = RouteElevationAnalyzer(google_api_key='YOUR_API_KEY_HERE')
    
    # Rota analizi
    origin = "Tınaztepe Sokak, Maltepe, İstanbul"
    destination = "Aydos Ormanı Rekreasyon Alanı, İstanbul"
    
    results = analyzer.analyze_route(origin, destination)
    
    # Rapor yazdır
    analyzer.print_report(results)
    
    # Harita ile görselleştir
    analyzer.visualize_route(results)
    
    # Araç için öneriler
    print("\n🚗 ARAÇ İÇİN ÖNERİLER:")
    if results['total_ascent_m'] > 100:
        print("⚠️  Önemli tırmanış bölümleri var - düşük vites kullanımı önerilir")
    if results['total_descent_m'] > 100:
        print("⚠️  Uzun iniş bölümleri var - fren performansına dikkat")
    if results['avg_gradient'] > 5:
        print("⚠️  Ortalama eğim yüksek - yakıt tüketimi artabilir")
    
    print("\n✓ Analiz tamamlandı!")