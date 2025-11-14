"""
Enhanced Visualization - Geliştirilmiş Görselleştirme Modülü
Eğim seviyelerine göre renkli rotalar ve detaylı analiz grafikleri
"""

import folium
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
from datetime import datetime
import json
import base64
from io import BytesIO
import warnings

# tight_layout uyarısını sustur
warnings.filterwarnings('ignore', message='This figure includes Axes that are not compatible with tight_layout')


class EnhancedVisualization:
    """
    Geliştirilmiş rota görselleştirme sınıfı
    """
    
    def __init__(self, output_dir='./output'):
        """
        Args:
            output_dir (str): Çıktı dosyaları dizini
        """
        self.output_dir = output_dir
        
        # Eğim renk şeması
        self.slope_colors = {
            'easy': '#00ff00',       # Yeşil: Kolay (%0-5)
            'moderate': '#ffff00',    # Sarı: Orta (%5-10)
            'hard': '#ff8800',        # Turuncu: Zor (%10-15)
            'extreme': '#ff0000',     # Kırmızı: Aşırı (%15+)
            'descent': '#0088ff'      # Mavi: İniş
        }
        
        # Eğim desenleri (pattern)
        self.slope_patterns = {
            'easy': {'weight': 4, 'opacity': 0.8, 'dash': None},
            'moderate': {'weight': 5, 'opacity': 0.9, 'dash': '10,5'},
            'hard': {'weight': 6, 'opacity': 1.0, 'dash': '5,5'},
            'extreme': {'weight': 7, 'opacity': 1.0, 'dash': '3,3'},
            'descent': {'weight': 5, 'opacity': 0.8, 'dash': '15,5'}
        }
    
    
    def create_slope_map(self, route_data):
        """
        Eğim seviyelerine göre renklendirilmiş harita oluştur
        
        Args:
            route_data (dict): Rota verisi
            
        Returns:
            folium.Map: Harita objesi
        """
        # Merkez noktayı bul
        path = route_data.get('path', [])
        if not path:
            return None
        
        # Düğüm konumlarını al
        nodes = route_data.get('nodes', {})
        coordinates = []
        
        for node_id in path:
            node = nodes.get(node_id, {})
            gps = node.get('gps', [])
            if len(gps) >= 2:
                coordinates.append([gps[0], gps[1]])
        
        if not coordinates:
            return None
        
        # Harita merkezi
        center_lat = sum(c[0] for c in coordinates) / len(coordinates)
        center_lon = sum(c[1] for c in coordinates) / len(coordinates)
        
        # Folium haritası oluştur
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=13,
            tiles='OpenStreetMap',
            control_scale=True
        )
        
        # Segment'leri çiz
        segments = route_data.get('segments', [])
        
        for i, segment in enumerate(segments):
            # Segment koordinatları
            from_node = nodes.get(segment['from'], {})
            to_node = nodes.get(segment['to'], {})
            
            from_gps = from_node.get('gps', [])
            to_gps = to_node.get('gps', [])
            
            if len(from_gps) < 2 or len(to_gps) < 2:
                continue
            
            seg_coords = [
                [from_gps[0], from_gps[1]],
                [to_gps[0], to_gps[1]]
            ]
            
            # Renk ve stil
            difficulty = segment.get('difficulty', 'easy')
            color = self.slope_colors.get(difficulty, '#888888')
            pattern = self.slope_patterns.get(difficulty, {})
            
            # Segment bilgisi için popup
            popup_html = f"""
            <div style="font-family: Arial, sans-serif; width: 200px;">
                <h4 style="margin: 5px 0;">Segment {i+1}</h4>
                <table style="width: 100%;">
                    <tr><td><b>Eğim:</b></td><td>%{segment['slope']:.1f}</td></tr>
                    <tr><td><b>Kategori:</b></td><td>{segment['category']}</td></tr>
                    <tr><td><b>Mesafe:</b></td><td>{segment['distance']:.0f}m</td></tr>
                    <tr><td><b>Yükselti Farkı:</b></td><td>{segment['elevation_change']:.1f}m</td></tr>
                    <tr><td><b>Zorluk:</b></td><td>{difficulty}</td></tr>
                </table>
            </div>
            """
            
            # Çizgi ekle
            folium.PolyLine(
                seg_coords,
                color=color,
                weight=pattern.get('weight', 5),
                opacity=pattern.get('opacity', 0.9),
                dash_array=pattern.get('dash'),
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(m)
        
        # Başlangıç ve bitiş işaretleyicileri
        if coordinates:
            # Başlangıç - Yeşil işaret
            folium.Marker(
                coordinates[0],
                popup="<b>BAŞLANGIÇ</b>",
                tooltip="Başlangıç Noktası",
                icon=folium.Icon(color='green', icon='play', prefix='fa')
            ).add_to(m)
            
            # Bitiş - Kırmızı işaret
            folium.Marker(
                coordinates[-1],
                popup="<b>VARIŞ</b>",
                tooltip="Varış Noktası",
                icon=folium.Icon(color='red', icon='flag-checkered', prefix='fa')
            ).add_to(m)
        
        # Kritik noktaları işaretle
        critical_points = self.find_critical_points(route_data)
        for point in critical_points:
            folium.CircleMarker(
                location=[point['lat'], point['lon']],
                radius=8,
                popup=f"<b>Kritik Nokta</b><br>Eğim: %{point['slope']:.1f}",
                color='red',
                fill=True,
                fillColor='yellow'
            ).add_to(m)
        
        # Harita lejantı ekle
        self.add_legend(m)
        
        # Rota özeti ekle
        self.add_route_summary(m, route_data)
        
        return m
    
    
    def add_legend(self, folium_map):
        """
        Haritaya eğim lejantı ekle
        """
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: auto; 
                    background-color: white; z-index: 1000; font-size: 14px;
                    border: 2px solid grey; border-radius: 5px; padding: 10px">
            
            <p style="margin: 0 0 5px 0; font-weight: bold; text-align: center;">
                Eğim Seviyeleri
            </p>
            
            <div style="margin-bottom: 5px;">
                <span style="background-color: #00ff00; width: 20px; height: 3px; 
                           display: inline-block; margin-right: 5px;"></span>
                %0-5 Kolay (Yeşil)
            </div>
            
            <div style="margin-bottom: 5px;">
                <span style="background-color: #ffff00; width: 20px; height: 3px; 
                           display: inline-block; margin-right: 5px;"></span>
                %5-10 Orta (Sarı)
            </div>
            
            <div style="margin-bottom: 5px;">
                <span style="background-color: #ff8800; width: 20px; height: 3px; 
                           display: inline-block; margin-right: 5px;"></span>
                %10-15 Zor (Turuncu)
            </div>
            
            <div style="margin-bottom: 5px;">
                <span style="background-color: #ff0000; width: 20px; height: 3px; 
                           display: inline-block; margin-right: 5px;"></span>
                %15+ Aşırı (Kırmızı)
            </div>
            
            <div style="margin-bottom: 0;">
                <span style="background-color: #0088ff; width: 20px; height: 3px; 
                           display: inline-block; margin-right: 5px;"></span>
                İniş (Mavi)
            </div>
        </div>
        '''
        folium_map.get_root().html.add_child(folium.Element(legend_html))
    
    
    def add_route_summary(self, folium_map, route_data):
        """
        Haritaya rota özeti ekle
        """
        vehicle_cap = route_data.get('vehicle_capability', {})
        
        summary_html = f'''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 280px; height: auto; 
                    background-color: rgba(255, 255, 255, 0.95); z-index: 1000; font-size: 13px;
                    border: 2px solid #333; border-radius: 8px; padding: 10px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
            
            <h3 style="margin: 0 0 10px 0; text-align: center; color: #333;">
                📊 Rota Analizi
            </h3>
            
            <div style="background-color: #f0f0f0; padding: 5px; border-radius: 5px; margin-bottom: 8px;">
                <b>Araç:</b> {vehicle_cap.get('vehicle_name', 'Bilinmiyor')}<br>
                <b>Güç:</b> {vehicle_cap.get('hp', 0)} HP | 
                <b>Tork:</b> {vehicle_cap.get('torque', 0)} Nm
            </div>
            
            <table style="width: 100%; font-size: 12px;">
                <tr>
                    <td><b>Toplam Mesafe:</b></td>
                    <td style="text-align: right;">{route_data.get('total_distance', 0):.2f} km</td>
                </tr>
                <tr>
                    <td><b>Tahmini Süre:</b></td>
                    <td style="text-align: right;">{route_data.get('total_time', 0):.0f} dakika</td>
                </tr>
                <tr>
                    <td><b>Yakıt Tüketimi:</b></td>
                    <td style="text-align: right;">{route_data.get('total_fuel', 0):.2f} L</td>
                </tr>
                <tr>
                    <td><b>Yakıt Maliyeti:</b></td>
                    <td style="text-align: right;">{route_data.get('fuel_cost', 0):.2f} TL</td>
                </tr>
                <tr style="border-top: 1px solid #ccc;">
                    <td><b>Maks. Eğim:</b></td>
                    <td style="text-align: right; color: #ff0000;">
                        %{route_data.get('max_slope', 0):.1f}
                    </td>
                </tr>
                <tr>
                    <td><b>Araç Limiti:</b></td>
                    <td style="text-align: right; color: #00aa00;">
                        %{vehicle_cap.get('maximum_slope', 0):.1f}
                    </td>
                </tr>
                <tr>
                    <td><b>Kritik Bölge:</b></td>
                    <td style="text-align: right;">
                        {route_data.get('critical_sections', 0)} adet
                    </td>
                </tr>
            </table>
            
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #ccc;">
                <a href="{route_data.get('google_maps_url', '#')}" target="_blank" 
                   style="display: block; text-align: center; background-color: #4285F4; 
                          color: white; padding: 8px; border-radius: 5px; 
                          text-decoration: none; font-weight: bold;">
                    🗺️ Google Maps'te Aç
                </a>
            </div>
        </div>
        '''
        folium_map.get_root().html.add_child(folium.Element(summary_html))
    
    
    def find_critical_points(self, route_data):
        """
        Kritik noktaları bul (yüksek eğimli yerler)
        """
        critical_points = []
        segments = route_data.get('segments', [])
        nodes = route_data.get('nodes', {})
        vehicle_cap = route_data.get('vehicle_capability', {})
        
        manageable_slope = vehicle_cap.get('manageable_slope', 15)
        
        for segment in segments:
            slope = abs(segment.get('slope', 0))
            if slope >= manageable_slope:
                from_node = nodes.get(segment['from'], {})
                from_gps = from_node.get('gps', [])
                if len(from_gps) >= 2:
                    critical_points.append({
                        'lat': from_gps[0],
                        'lon': from_gps[1],
                        'slope': segment['slope']
                    })
        
        return critical_points
    
    
    def create_elevation_profile(self, route_data):
        """
        Rota yükseklik profili grafiği oluştur
        """
        segments = route_data.get('segments', [])
        if not segments:
            return None
        
        # Veri hazırlama
        distances = [0]
        elevations = []
        slopes = []
        colors = []
        
        current_distance = 0
        
        for segment in segments:
            # İlk nokta yüksekliği
            if len(elevations) == 0:
                elevations.append(segment.get('from_elevation', 0))
            
            # Mesafe ekle
            current_distance += segment.get('distance', 0) / 1000  # km
            distances.append(current_distance)
            
            # Yükseklik ekle
            elevations.append(segment.get('to_elevation', 0))
            
            # Eğim ve renk
            slopes.append(segment.get('slope', 0))
            colors.append(self.slope_colors.get(segment.get('difficulty', 'easy')))
        
        # Grafik oluştur - DÜZELTME: constrained_layout kullan
        fig = plt.figure(figsize=(14, 8), constrained_layout=True)
        gs = GridSpec(3, 1, height_ratios=[2, 1, 1], hspace=0.3, figure=fig)
        
        # 1. Yükseklik Profili
        ax1 = fig.add_subplot(gs[0])
        
        # Gradient dolgu için
        for i in range(len(distances) - 1):
            ax1.fill_between(
                [distances[i], distances[i+1]], 
                0, 
                [elevations[i], elevations[i+1]],
                color=colors[i] if i < len(colors) else '#888888',
                alpha=0.3
            )
        
        ax1.plot(distances, elevations, 'b-', linewidth=2, label='Yükseklik')
        ax1.fill_between(distances, 0, elevations, alpha=0.1, color='blue')
        ax1.set_ylabel('Yükseklik (m)', fontsize=10)
        ax1.set_title('Rota Yükseklik Profili ve Eğim Analizi', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper right')
        
        # 2. Eğim Grafiği
        ax2 = fig.add_subplot(gs[1])
        
        # Eğim çubukları
        bar_width = 0.8 * (distances[1] - distances[0]) if len(distances) > 1 else 0.1
        for i in range(len(slopes)):
            color = colors[i] if i < len(colors) else '#888888'
            ax2.bar(distances[i], slopes[i], width=bar_width, color=color, alpha=0.7)
        
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.set_ylabel('Eğim (%)', fontsize=10)
        ax2.set_xlabel('Mesafe (km)', fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # Araç limitleri
        vehicle_cap = route_data.get('vehicle_capability', {})
        comfortable = vehicle_cap.get('comfortable_slope', 8)
        manageable = vehicle_cap.get('manageable_slope', 12)
        maximum = vehicle_cap.get('maximum_slope', 18)
        
        ax2.axhline(y=comfortable, color='green', linestyle='--', linewidth=1, 
                   label=f'Rahat: %{comfortable}')
        ax2.axhline(y=-comfortable, color='green', linestyle='--', linewidth=1)
        ax2.axhline(y=manageable, color='orange', linestyle='--', linewidth=1, 
                   label=f'Zorlu: %{manageable}')
        ax2.axhline(y=-manageable, color='orange', linestyle='--', linewidth=1)
        ax2.axhline(y=maximum, color='red', linestyle='--', linewidth=1, 
                   label=f'Maksimum: %{maximum}')
        ax2.axhline(y=-maximum, color='red', linestyle='--', linewidth=1)
        ax2.legend(loc='upper right', fontsize=8)
        
        # 3. Hız ve Yakıt Tahmini
        ax3 = fig.add_subplot(gs[2])
        
        # Tahmini hız hesapla
        speeds = []
        fuel_rates = []
        
        for slope in slopes:
            # Eğime göre hız tahmini
            if abs(slope) < 2:
                speed = 60
                fuel_rate = 1.0
            elif abs(slope) < 5:
                speed = 50
                fuel_rate = 1.2
            elif abs(slope) < 10:
                speed = 40
                fuel_rate = 1.5
            elif abs(slope) < 15:
                speed = 30
                fuel_rate = 2.0
            else:
                speed = 20
                fuel_rate = 2.5
            
            speeds.append(speed)
            fuel_rates.append(fuel_rate)
        
        ax3_2 = ax3.twinx()
        
        # Hız grafiği
        ax3.plot(distances[:-1], speeds, 'g-', linewidth=2, label='Tahmini Hız')
        ax3.set_ylabel('Hız (km/sa)', fontsize=10, color='green')
        ax3.tick_params(axis='y', labelcolor='green')
        
        # Yakıt tüketim oranı
        ax3_2.plot(distances[:-1], fuel_rates, 'r--', linewidth=1.5, label='Yakıt Çarpanı')
        ax3_2.set_ylabel('Yakıt Tüketim Çarpanı', fontsize=10, color='red')
        ax3_2.tick_params(axis='y', labelcolor='red')
        
        ax3.set_xlabel('Mesafe (km)', fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        # Başlık ve bilgiler
        fig.suptitle(
            f"Araç: {vehicle_cap.get('vehicle_name', 'Bilinmiyor')} | "
            f"Toplam: {route_data.get('total_distance', 0):.2f}km | "
            f"Yakıt: {route_data.get('total_fuel', 0):.2f}L | "
            f"Maliyet: {route_data.get('fuel_cost', 0):.2f}TL",
            fontsize=11, y=0.98
        )
        
        # DÜZELTME: tight_layout kaldırıldı - constrained_layout kullanıldı
        return fig
    
    
    def save_visualization(self, route_data, filename_prefix="route"):
        """
        Tüm görselleştirmeleri kaydet
        
        Args:
            route_data (dict): Rota verisi
            filename_prefix (str): Dosya adı öneki
            
        Returns:
            dict: Kaydedilen dosya yolları
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        saved_files = {}
        
        # 1. Harita kaydet
        slope_map = self.create_slope_map(route_data)
        if slope_map:
            map_file = f"{self.output_dir}/{filename_prefix}_map_{timestamp}.html"
            slope_map.save(map_file)
            saved_files['map'] = map_file
            print(f"✅ Harita kaydedildi: {map_file}")
        
        # 2. Yükseklik profili kaydet
        elevation_fig = self.create_elevation_profile(route_data)
        if elevation_fig:
            profile_file = f"{self.output_dir}/{filename_prefix}_profile_{timestamp}.png"
            elevation_fig.savefig(profile_file, dpi=150, bbox_inches='tight')
            plt.close(elevation_fig)
            saved_files['profile'] = profile_file
            print(f"✅ Profil kaydedildi: {profile_file}")
        
        # 3. JSON veri kaydet
        json_file = f"{self.output_dir}/{filename_prefix}_data_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            # Google Maps URL'sini kısalt (çok uzun olabilir)
            route_data_copy = route_data.copy()
            if 'google_maps_url' in route_data_copy:
                route_data_copy['google_maps_url'] = route_data_copy['google_maps_url'][:200] + "..."
            
            json.dump(route_data_copy, f, indent=2, ensure_ascii=False)
        saved_files['data'] = json_file
        print(f"✅ Veri kaydedildi: {json_file}")
        
        return saved_files
    
    
    def print_route_comparison(self, routes):
        """
        Birden fazla rotayı karşılaştır ve tablo olarak yazdır
        
        Args:
            routes (list): Rota listesi
        """
        print("\n" + "="*100)
        print("ROTA KARŞILAŞTIRMASI")
        print("="*100)
        
        # Başlık satırı
        headers = ["Özellik", "Rota 1", "Rota 2", "Rota 3"]
        print(f"{headers[0]:<25} {headers[1]:<20} {headers[2]:<20} {headers[3]:<20}")
        print("-"*100)
        
        # Karşılaştırma verileri
        for i, route in enumerate(routes[:3]):
            if i == 0:
                print(f"{'Mod':<25}", end="")
            else:
                print(f"{'':<25}", end="")
            
            mode = route.get('mode', 'balanced')
            print(f" {mode:<20}", end="")
        
        print("\n" + "-"*100)
        
        # Metrikler
        metrics = [
            ('Toplam Mesafe (km)', 'total_distance', lambda x: f"{x:.2f}"),
            ('Süre (dakika)', 'total_time', lambda x: f"{x:.0f}"),
            ('Yakıt (L)', 'total_fuel', lambda x: f"{x:.2f}"),
            ('Maliyet (TL)', 'fuel_cost', lambda x: f"{x:.2f}"),
            ('Maks. Eğim (%)', 'max_slope', lambda x: f"{x:.1f}"),
            ('Kritik Bölge', 'critical_sections', lambda x: f"{x}")
        ]
        
        for metric_name, metric_key, formatter in metrics:
            print(f"{metric_name:<25}", end="")
            for route in routes[:3]:
                value = route.get(metric_key, 0)
                formatted = formatter(value)
                print(f" {formatted:<20}", end="")
            print()
        
        print("="*100)
        
        # En iyi değerleri belirt
        if len(routes) > 1:
            print("\n📊 EN İYİ DEĞERLER:")
            
            # En kısa mesafe
            shortest = min(routes, key=lambda x: x.get('total_distance', float('inf')))
            print(f"  • En Kısa: {shortest.get('mode', 'N/A')} ({shortest.get('total_distance', 0):.2f} km)")
            
            # En az yakıt
            most_efficient = min(routes, key=lambda x: x.get('total_fuel', float('inf')))
            print(f"  • En Ekonomik: {most_efficient.get('mode', 'N/A')} ({most_efficient.get('total_fuel', 0):.2f} L)")
            
            # En güvenli (en düşük maksimum eğim)
            safest = min(routes, key=lambda x: x.get('max_slope', float('inf')))
            print(f"  • En Güvenli: {safest.get('mode', 'N/A')} (Maks %{safest.get('max_slope', 0):.1f} eğim)")
            
        print()