"""
Görselleştirme Modülü - Rota Analizi ve Grafik Oluşturma
YENİ SİSTEM: OSM + A* tabanlı rota görselleştirmesi

=============================================================================
ESKİ SİSTEMDEN FARKLAR:
=============================================================================

1. ✅ EKLENEN: Kendi hesapladığımız rotayı gösterme
   - Eski: Sadece Google'ın rotası
   - Yeni: Bizim OSM/A* rotası + opsiyonel Google karşılaştırması

2. ✅ EKLENEN: Eğim-bazlı renk kodlama
   - Eski: Tek renk rota çizgisi
   - Yeni: Yeşil (güvenli) → Sarı (orta) → Kırmızı (kritik)

3. ✅ EKLENEN: Segment bazlı analiz
   - Eski: Genel yükseklik profili
   - Yeni: Her yol parçası için detaylı analiz

4. ✅ EKLENEN: Kritik nokta işaretleme
   - Eski: Sadece rakam
   - Yeni: Harita üzerinde marker'lar

5. ✅ EKLENEN: Rota karşılaştırma metrikleri
   - Eski: Tek rota analizi
   - Yeni: Bizim vs Google karşılaştırması

6. ✅ EKLENEN: Optimizasyon modu gösterimi
   - Eski: Yok
   - Yeni: fuel_saver, safety_first, balanced, time_saver

7. ✅ İYİLEŞTİRİLEN: Yakıt hesaplama görselleştirmesi
   - Eski: Genel tüketim
   - Yeni: Segment bazlı + eğim etkisi detaylı
=============================================================================
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
from datetime import datetime
import os

# Yerel modüller
from database import get_vehicle_specs, get_fuel_price, OPTIMIZATION_PROFILES


class RouteVisualizer:
    """
    YENİ: OSM/A* tabanlı rota görselleştirme sınıfı
    ESKİ: RouteElevationAnalyzer (Google API odaklıydı)
    """
    
    def __init__(self, output_dir='./visualizations'):
        """
        Args:
            output_dir (str): Çıktı dizini
        """
        self.output_dir = output_dir
        
        # Dizini oluştur
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # YENİ: Eğim bazlı renk paleti
        self.colors = {
            'safe': '#4CAF50',        # Yeşil (0-7%)
            'warning': '#FFC107',     # Sarı (7-12%)
            'critical': '#F44336',    # Kırmızı (12%+)
            'our_route': '#2196F3',   # Mavi (bizim rota)
            'google_route': '#9E9E9E',# Gri (Google rotası)
            'background': '#FAFAFA'   # Açık gri arka plan
        }
        
        print(f"✓ RouteVisualizer başlatıldı")
        print(f"  Çıktı dizini: {output_dir}")
    
    
    def visualize_custom_route(self, route_data, vehicle_name, time_of_day='peak', 
                               save_path=None):
        """
        YENİ FONKSĐYON: Kendi hesapladığımız rotayı görselleştir
        
        ESKİ: visualize_route() → Sadece Google rotası
        YENİ: visualize_custom_route() → OSM/A* rotası
        
        Args:
            route_data (dict): routing_engine.calculate_route() sonucu
            vehicle_name (str): Araç adı
            time_of_day (str): 'peak' veya 'offpeak'
            save_path (str): Kayıt yolu (opsiyonel)
            
        Returns:
            str: Kaydedilen dosya yolu
        """
        print(f"\n{'='*70}")
        print("YENİ SİSTEM - ROTA GÖRSELLEŞTİRME")
        print(f"{'='*70}")
        print(f"  Araç: {vehicle_name}")
        print(f"  Zaman: {time_of_day}")
        print(f"  Mod: {route_data.get('mode', 'balanced')}")
        print("-"*70)
        
        # Şekil oluştur (4x3 layout)
        fig = plt.figure(figsize=(20, 14))
        fig.patch.set_facecolor(self.colors['background'])
        
        # Başlık
        profile_name = OPTIMIZATION_PROFILES.get(route_data['mode'], {}).get('name', 'Dengeli')
        fig.suptitle(
            f'Rota Analizi: {vehicle_name}\n'
            f'Optimizasyon: {profile_name} | Zaman: {time_of_day.upper()}',
            fontsize=16, fontweight='bold', y=0.98
        )
        
        # Grid layout
        gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
        
        # 1. YENİ: GPS Harita (eğim renkli)
        ax_map = fig.add_subplot(gs[0:2, 0:2])
        self._plot_route_map_with_slopes(ax_map, route_data)
        
        # 2. İYİLEŞTİRİLEN: Yükselti Profili (segment detaylı)
        ax_elevation = fig.add_subplot(gs[0, 2])
        self._plot_elevation_profile_enhanced(ax_elevation, route_data)
        
        # 3. YENİ: Eğim Dağılım Histogramı
        ax_slope_hist = fig.add_subplot(gs[1, 2])
        self._plot_slope_histogram(ax_slope_hist, route_data)
        
        # 4. YENİ: Özet Metrikler Tablosu
        ax_metrics = fig.add_subplot(gs[2, 0])
        self._plot_metrics_table(ax_metrics, route_data, vehicle_name)
        
        # 5. İYİLEŞTİRİLEN: Segment Bazlı Yakıt Grafiği
        ax_fuel = fig.add_subplot(gs[2, 1])
        self._plot_fuel_by_segment(ax_fuel, route_data)
        
        # 6. YENİ: Kritik Bölge Listesi
        ax_critical = fig.add_subplot(gs[2, 2])
        self._plot_critical_sections(ax_critical, route_data)
        
        # Kaydet
        if save_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            vehicle_safe = vehicle_name.replace(' ', '_').replace('.', '')
            save_path = os.path.join(
                self.output_dir, 
                f'route_{vehicle_safe}_{route_data["mode"]}_{timestamp}.png'
            )
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor=self.colors['background'])
        plt.close()
        
        print(f"\n✓ Görselleştirme kaydedildi: {save_path}")
        print(f"{'='*70}\n")
        
        return save_path
    
    
    def _plot_route_map_with_slopes(self, ax, route_data):
        """
        YENİ FONKSĐYON: Eğim renkli harita
        
        ESKİ: Tek renkli çizgi
        YENİ: Her segment eğimine göre renkli
        """
        ax.set_title('Rota Haritası (Eğim Bazlı Renklendirme)', 
                    fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel('Boylam (Longitude)', fontsize=10)
        ax.set_ylabel('Enlem (Latitude)', fontsize=10)
        ax.set_facecolor(self.colors['background'])
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # GPS yolu
        gps_path = route_data['gps_path']
        lats = [gps[0] for gps in gps_path]
        lons = [gps[1] for gps in gps_path]
        
        # Segment bilgileri
        segments = route_data['route_details']['segments']
        
        # Her segmenti eğimine göre renklendir
        for i, segment in enumerate(segments):
            if i < len(lats) - 1:
                slope = abs(segment['slope_percent'])
                
                # Renk seç
                if slope < 7:
                    color = self.colors['safe']
                    linewidth = 2
                elif slope < 12:
                    color = self.colors['warning']
                    linewidth = 3
                else:
                    color = self.colors['critical']
                    linewidth = 4
                
                # Segment çiz
                ax.plot([lons[i], lons[i+1]], [lats[i], lats[i+1]], 
                       color=color, linewidth=linewidth, alpha=0.8, zorder=2)
        
        # Başlangıç ve bitiş marker'ları
        ax.plot(lons[0], lats[0], 'go', markersize=15, 
               label='Başlangıç', zorder=3, markeredgecolor='black', 
               markeredgewidth=2)
        ax.plot(lons[-1], lats[-1], 'rs', markersize=15, 
               label='Varış', zorder=3, markeredgecolor='black', 
               markeredgewidth=2)
        
        # YENİ: Kritik noktaları işaretle
        critical_sections = route_data.get('critical_sections', [])
        if critical_sections:
            for section in critical_sections:
                lat, lon = section['from_gps']
                ax.plot(lon, lat, 'r^', markersize=10, 
                       markeredgecolor='black', markeredgewidth=1.5, 
                       zorder=4, alpha=0.8)
        
        # Legend
        legend_elements = [
            mpatches.Patch(color=self.colors['safe'], label='Güvenli (0-7%)'),
            mpatches.Patch(color=self.colors['warning'], label='Dikkat (7-12%)'),
            mpatches.Patch(color=self.colors['critical'], label='Kritik (12%+)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', 
                 framealpha=0.9, fontsize=9)
        
        # Aspect ratio
        ax.set_aspect('equal', adjustable='box')
    
    
    def _plot_elevation_profile_enhanced(self, ax, route_data):
        """
        İYİLEŞTİRİLEN FONKSĐYON: Gelişmiş yükselti profili
        
        ESKİ: Basit yükselti grafiği
        YENİ: Segment detaylı + kritik bölge vurguları
        """
        ax.set_title('Yükselti Profili', fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel('Mesafe (km)', fontsize=10)
        ax.set_ylabel('Rakım (m)', fontsize=10)
        ax.set_facecolor(self.colors['background'])
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Segment verilerini topla
        segments = route_data['route_details']['segments']
        
        distances = [0]
        elevations = [segments[0]['from_gps'][0] if segments else 0]  # İlk nokta
        
        cumulative_dist = 0
        for segment in segments:
            cumulative_dist += segment['distance_m'] / 1000  # km
            distances.append(cumulative_dist)
            # Bitiş yüksekliği = başlangıç + yükselti farkı
            elevations.append(elevations[-1] + segment.get('slope_percent', 0) * segment['distance_m'] / 100)
        
        # Ana profil çizgisi
        ax.plot(distances, elevations, color=self.colors['our_route'], 
               linewidth=2.5, label='Rota Profili', zorder=2)
        
        # Alan doldur
        ax.fill_between(distances, elevations, alpha=0.3, 
                        color=self.colors['our_route'], zorder=1)
        
        # YENİ: Kritik bölgeleri vurgula
        critical_sections = route_data.get('critical_sections', [])
        if critical_sections:
            for i, segment in enumerate(segments):
                if abs(segment['slope_percent']) > 12:
                    if i < len(distances) - 1:
                        ax.axvspan(distances[i], distances[i+1], 
                                  color=self.colors['critical'], alpha=0.3, 
                                  zorder=0)
        
        # İstatistikler
        max_elev = max(elevations)
        min_elev = min(elevations)
        
        ax.text(0.02, 0.98, 
               f'Max: {max_elev:.0f}m\nMin: {min_elev:.0f}m\nFark: {max_elev-min_elev:.0f}m',
               transform=ax.transAxes, fontsize=9,
               verticalalignment='top', bbox=dict(boxstyle='round', 
               facecolor='white', alpha=0.8))
        
        ax.legend(loc='upper right', fontsize=9)
    
    
    def _plot_slope_histogram(self, ax, route_data):
        """
        YENİ FONKSĐYON: Eğim dağılım histogramı
        
        ESKİ: Yok
        YENİ: Rotadaki eğimlerin dağılımı
        """
        ax.set_title('Eğim Dağılımı', fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel('Eğim (%)', fontsize=10)
        ax.set_ylabel('Segment Sayısı', fontsize=10)
        ax.set_facecolor(self.colors['background'])
        ax.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        # Eğim verilerini topla
        segments = route_data['route_details']['segments']
        slopes = [segment['slope_percent'] for segment in segments]
        
        # Histogram
        n, bins, patches = ax.hist(slopes, bins=20, edgecolor='black', 
                                   linewidth=0.5, alpha=0.7)
        
        # Renklendirme
        for i, patch in enumerate(patches):
            bin_center = (bins[i] + bins[i+1]) / 2
            if abs(bin_center) < 7:
                patch.set_facecolor(self.colors['safe'])
            elif abs(bin_center) < 12:
                patch.set_facecolor(self.colors['warning'])
            else:
                patch.set_facecolor(self.colors['critical'])
        
        # Ortalama çizgisi
        avg_slope = np.mean([abs(s) for s in slopes])
        ax.axvline(avg_slope, color='red', linestyle='--', linewidth=2,
                  label=f'Ort. Eğim: {avg_slope:.1f}%')
        
        ax.legend(fontsize=9)
    
    
    def _plot_metrics_table(self, ax, route_data, vehicle_name):
        """
        YENİ FONKSĐYON: Özet metrikler tablosu
        
        ESKİ: Konsola yazdırma
        YENİ: Görsel tablo
        """
        ax.axis('off')
        ax.set_title('Rota Özeti', fontsize=12, fontweight='bold', pad=10)
        
        # Veri hazırla
        data = [
            ['Toplam Mesafe', f"{route_data['total_distance']:.2f} km"],
            ['Tahmini Süre', f"{route_data['estimated_time']:.0f} dk"],
            ['Toplam Yakıt', f"{route_data['total_fuel']:.2f} L"],
            ['Yakıt Maliyeti', f"{route_data['fuel_cost']:.2f} TL"],
            ['Maks. Eğim', f"{route_data['max_slope']:.1f}%"],
            ['Toplam Tırmanış', f"{route_data['total_elevation_gain']:.0f} m"],
            ['Kritik Bölge', f"{len(route_data['critical_sections'])} adet"],
            ['Araç', vehicle_name],
        ]
        
        # Tablo oluştur
        table = ax.table(cellText=data, 
                        colWidths=[0.5, 0.5],
                        cellLoc='left',
                        loc='center',
                        bbox=[0, 0, 1, 1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Stil
        for i in range(len(data)):
            table[(i, 0)].set_facecolor('#E3F2FD')
            table[(i, 0)].set_text_props(weight='bold')
            table[(i, 1)].set_facecolor('white')
            
            # Kritik değerleri vurgula
            if i == 4 and route_data['max_slope'] > 12:
                table[(i, 1)].set_facecolor('#FFCDD2')
            elif i == 6 and len(route_data['critical_sections']) > 0:
                table[(i, 1)].set_facecolor('#FFCDD2')
    
    
    def _plot_fuel_by_segment(self, ax, route_data):
        """
        İYİLEŞTİRİLEN FONKSĐYON: Segment bazlı yakıt grafiği
        
        ESKİ: Genel yakıt tüketimi
        YENİ: Her segment için ayrı + eğim etkisi görünür
        """
        ax.set_title('Segment Bazlı Yakıt Tüketimi', fontsize=12, 
                    fontweight='bold', pad=10)
        ax.set_xlabel('Segment #', fontsize=10)
        ax.set_ylabel('Yakıt (L)', fontsize=10)
        ax.set_facecolor(self.colors['background'])
        ax.grid(True, alpha=0.3, axis='y', linestyle='--')
        
        # Segment verilerini topla
        segments = route_data['route_details']['segments']
        
        segment_nums = list(range(1, len(segments) + 1))
        fuel_amounts = [seg['fuel_liters'] for seg in segments]
        slopes = [abs(seg['slope_percent']) for seg in segments]
        
        # Renk kodlama
        colors = [self.colors['safe'] if s < 7 else 
                 self.colors['warning'] if s < 12 else 
                 self.colors['critical'] for s in slopes]
        
        # Bar grafiği
        bars = ax.bar(segment_nums, fuel_amounts, color=colors, 
                     edgecolor='black', linewidth=0.5, alpha=0.8)
        
        # Ortalama çizgisi
        avg_fuel = np.mean(fuel_amounts)
        ax.axhline(avg_fuel, color='red', linestyle='--', linewidth=2,
                  label=f'Ortalama: {avg_fuel:.3f}L')
        
        # X ekseni etiketlerini azalt
        if len(segments) > 20:
            ax.set_xticks(segment_nums[::5])
        
        ax.legend(fontsize=9)
    
    
    def _plot_critical_sections(self, ax, route_data):
        """
        YENİ FONKSĐYON: Kritik bölge listesi
        
        ESKİ: Konsola yazdırma
        YENİ: Görsel liste
        """
        ax.axis('off')
        ax.set_title('Kritik Eğim Bölgeleri (>12%)', fontsize=12, 
                    fontweight='bold', pad=10)
        
        critical_sections = route_data.get('critical_sections', [])
        
        if not critical_sections:
            ax.text(0.5, 0.5, '✓ Kritik bölge yok\nGüvenli rota!',
                   ha='center', va='center', fontsize=14, color='green',
                   weight='bold', transform=ax.transAxes,
                   bbox=dict(boxstyle='round', facecolor=self.colors['safe'], 
                            alpha=0.3))
        else:
            # Tablo verisi hazırla
            data = [['#', 'Sokak', 'Eğim', 'Mesafe']]
            for i, section in enumerate(critical_sections[:5], 1):  # İlk 5
                data.append([
                    str(i),
                    section['street_name'][:20] + '...' if len(section['street_name']) > 20 
                        else section['street_name'],
                    f"{abs(section['slope']):.1f}%",
                    f"{section['distance_m']:.0f}m"
                ])
            
            # Tablo oluştur
            table = ax.table(cellText=data, 
                            colWidths=[0.1, 0.5, 0.2, 0.2],
                            cellLoc='left',
                            loc='center',
                            bbox=[0, 0, 1, 1])
            
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 2)
            
            # Header stilini ayarla
            for i in range(4):
                table[(0, i)].set_facecolor('#EF5350')
                table[(0, i)].set_text_props(weight='bold', color='white')
            
            # Veri satırlarını ayarla
            for i in range(1, len(data)):
                for j in range(4):
                    table[(i, j)].set_facecolor('#FFCDD2')
    
    
    def print_route_summary(self, route_data, vehicle_name):
        """
        YENİ FONKSĐYON: Konsola özet rapor yazdır
        
        ESKİ: print_detailed_report() → Çok uzun
        YENİ: print_route_summary() → Özet ve net
        """
        print(f"\n{'='*70}")
        print("ROTA ÖZET RAPORU")
        print(f"{'='*70}")
        print(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        print(f"Araç: {vehicle_name}")
        print(f"Optimizasyon Modu: {route_data['mode']}")
        
        print(f"\n📍 ROTA BİLGİLERİ:")
        print(f"  Mesafe: {route_data['total_distance']:.2f} km")
        print(f"  Süre: {route_data['estimated_time']:.0f} dakika")
        print(f"  Segment Sayısı: {len(route_data['route_details']['segments'])}")
        
        print(f"\n⛽ YAKIT TAHMİNİ:")
        print(f"  Toplam: {route_data['total_fuel']:.2f} L")
        print(f"  Maliyet: {route_data['fuel_cost']:.2f} TL")
        print(f"  100km başına: {(route_data['total_fuel']/route_data['total_distance']*100):.2f} L/100km")
        
        print(f"\n📊 EĞİM ANALİZİ:")
        print(f"  Maksimum: {route_data['max_slope']:.1f}%")
        print(f"  Toplam Tırmanış: {route_data['total_elevation_gain']:.0f} m")
        print(f"  Kritik Bölge: {len(route_data['critical_sections'])} adet")
        
        # Kritik bölgeler
        if route_data['critical_sections']:
            print(f"\n⚠️  KRİTİK BÖLGELER:")
            for i, section in enumerate(route_data['critical_sections'], 1):
                print(f"  {i}. {section['street_name']}: {abs(section['slope']):.1f}% "
                      f"({section['distance_m']:.0f}m)")
        else:
            print(f"\n✓ Kritik bölge yok - Güvenli rota!")
        
        print(f"{'='*70}\n")


# YENİ: Karşılaştırma fonksiyonu
def compare_routes(our_route, google_route, vehicle_name, save_path=None):
    """
    YENİ FONKSĐYON: Bizim rota vs Google rotası karşılaştırması
    
    ESKİ: Yok
    YENİ: İki rotayı yan yana karşılaştır
    
    Args:
        our_route (dict): Bizim hesapladığımız rota
        google_route (dict): Google'ın rotası (opsiyonel)
        vehicle_name (str): Araç adı
        save_path (str): Kayıt yolu
        
    Returns:
        dict: Karşılaştırma sonuçları
    """
    print(f"\n{'='*70}")
    print("ROTA KARŞILAŞTIRMASI")
    print(f"{'='*70}")
    
    comparison = {
        'our_route': {
            'distance_km': our_route['total_distance'],
            'fuel_liters': our_route['total_fuel'],
            'fuel_cost_tl': our_route['fuel_cost'],
            'time_min': our_route['estimated_time'],
            'max_slope': our_route['max_slope'],
            'critical_count': len(our_route['critical_sections'])
        }
    }
    
    if google_route:
        comparison['google_route'] = {
            'distance_km': google_route.get('total_distance', 0),
            'fuel_liters': google_route.get('total_fuel', 0),
            'fuel_cost_tl': google_route.get('fuel_cost', 0),
            'time_min': google_route.get('estimated_time', 0),
            'max_slope': google_route.get('max_slope', 0),
            'critical_count': len(google_route.get('critical_sections', []))
        }
        
        # Karşılaştırma tablosu
        print(f"\n{'Kriter':<20} {'Bizim Sistem':<20} {'Google Maps':<20} {'Fark':<15}")
        print("-"*75)
        
        for key in ['distance_km', 'fuel_liters', 'fuel_cost_tl', 'time_min', 
                    'max_slope', 'critical_count']:
            our_val = comparison['our_route'][key]
            google_val = comparison['google_route'][key]
            
            if google_val > 0:
                diff_pct = ((our_val - google_val) / google_val) * 100
                diff_str = f"{diff_pct:+.1f}%"
            else:
                diff_str = "N/A"
            
            print(f"{key:<20} {our_val:<20.2f} {google_val:<20.2f} {diff_str:<15}")
        
        # Sonuç
        print(f"\n{'='*70}")
        if comparison['our_route']['critical_count'] < comparison['google_route']['critical_count']:
            print("✓ BİZİM SİSTEM DAHA GÜVENLİ (daha az kritik eğim)")
        
        if comparison['our_route']['fuel_liters'] < comparison['google_route']['fuel_liters']:
            saving = comparison['google_route']['fuel_liters'] - comparison['our_route']['fuel_liters']
            saving_tl = comparison['google_route']['fuel_cost_tl'] - comparison['our_route']['fuel_cost_tl']
            print(f"✓ YAKIT TASARRUFU: {saving:.2f}L ({saving_tl:.2f}TL)")
        
        print(f"{'='*70}\n")
    
    return comparison


# Eski sistemle uyumluluk için (opsiyonel)
class RouteElevationAnalyzer:
    """
    ESKİ SİSTEM: Google API tabanlı analiz
    UYUMLULUK: Eski kod çalışmaya devam etsin
    """
    pass  # Eski kodu buraya ekleyebilirsiniz


# Test
if __name__ == "__main__":
    print("Visualization Module - Test")
    print("Gerçek test için routing_engine sonucu gereklidir")
