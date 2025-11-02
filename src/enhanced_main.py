"""
Enhanced Navigation System - Geliştirilmiş Navigasyon Sistemi
Eğim optimizasyonlu, araç gücüne dayalı akıllı rota planlama
Google Maps entegrasyonu ve detaylı görselleştirme
"""

import os
import sys
import json
from datetime import datetime

# Mevcut modüller
from database import VEHICLE_DATABASE, TRAFFIC_ZONES, BEYKOZ_REGION
from road_network import RoadNetworkManager

# Geliştirilmiş modüller
from enhanced_routing_engine import EnhancedRoutingEngine, get_elevation_from_api
from enhanced_visualization import EnhancedVisualization


class EnhancedNavigationSystem:
    """
    Geliştirilmiş navigasyon sistemi - Ana kontrol sınıfı
    """
    
    def __init__(self, cache_dir='./cache', output_dir='./output'):
        """
        Sistemi başlat
        
        Args:
            cache_dir (str): Yol ağı önbellek dizini
            output_dir (str): Çıktı dosyaları dizini
        """
        print(f"\n{'='*80}")
        print(" "*15 + "GELİŞTİRİLMİŞ NAVİGASYON SİSTEMİ")
        print(" "*10 + "🚗 Eğim Optimizasyonlu • Araç Gücü Analizi • Google Maps")
        print(f"{'='*80}\n")
        
        self.cache_dir = cache_dir
        self.output_dir = output_dir
        
        # Dizinleri oluştur
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Bileşenleri başlat
        print("📦 Sistem bileşenleri yükleniyor...")
        print("[1/3] Yol ağı yöneticisi...")
        self.network_manager = RoadNetworkManager(cache_dir=cache_dir)
        
        print("[2/3] Görselleştirme motoru...")
        self.visualizer = EnhancedVisualization(output_dir=output_dir)
        
        print("[3/3] Geliştirilmiş rota motoru...")
        self.router = None  # Graf yüklendikten sonra başlatılacak
        
        self.current_graph = None
        
        print("\n✅ Sistem hazır!\n")
    
    
    def initialize_region(self, region_name='beykoz', bbox=None, force_download=False, add_elevation=True):
        """
        Bölge verilerini hazırla ve yükseklik verisi ekle
        
        Args:
            region_name (str): Bölge adı
            bbox (tuple): Bounding box
            force_download (bool): Zorla yeniden indir
            add_elevation (bool): Yükseklik verisi ekle
            
        Returns:
            bool: Başarılı ise True
        """
        print(f"\n{'='*80}")
        print(f"📍 BÖLGE HAZIRLANIYOR: {region_name.upper()}")
        print(f"{'='*80}\n")
        
        # Varsayılan bbox
        if bbox is None:
            bbox = BEYKOZ_REGION['bbox']
        
        # Cache kontrolü ve yükleme
        success = False
        if not force_download and self.network_manager.cache_exists(region_name):
            print(f"✓ {region_name} bölgesi cache'de bulundu")
            success = self.network_manager.load_cache(region_name)
        
        if not success or force_download:
            print(f"⏳ {region_name} bölgesi indiriliyor...")
            success = self.network_manager.download_and_build(bbox, region_name)
        
        if not success:
            print("❌ Bölge hazırlanamadı!")
            return False
        
        # Graf'ı al
        self.current_graph = self.network_manager.get_graph()
        print("Graph alındı")
        # Yükseklik verisi ekle
        if add_elevation:
            print("\n🏔️ Yükseklik verileri ekleniyor...")
            self._add_elevation_data()
        
        # Enhanced routing engine'i başlat
        self.router = EnhancedRoutingEngine(
            road_network=self.current_graph,
            vehicle_db=VEHICLE_DATABASE,
            traffic_zones=TRAFFIC_ZONES
        )
        
        print(f"\n✅ Bölge hazır!")
        print(f"  • {len(self.current_graph['nodes'])} düğüm")
        print(f"  • {len(self.current_graph['edges'])} kenar")
        print(f"  • Yükseklik verisi: {'Eklendi' if add_elevation else 'Yok'}\n")
        
        return True
    
    
    def _add_elevation_data(self):
        """
        Düğümlere yükseklik verisi ekle
        (Demo için rastgele veri, gerçek uygulamada API kullanılmalı)
        """
        import random
        
        nodes = self.current_graph.get('nodes', {})
        
        # Beykoz için gerçekçi yükseklik aralığı (0-250m)
        base_elevation = 50  # Deniz seviyesinden ortalama yükseklik
        
        for node_id, node_data in nodes.items():
            # Gerçek uygulamada: elevation = get_elevation_from_api(lat, lon)
            # Demo için rastgele yükseklik
            lat = node_data.get('lat', 0)
            lon = node_data.get('lon', 0)
            
            # Konuma göre değişken yükseklik (kuzey ve doğuya gittikçe yüksel)
            elevation_variation = (lat - 41.10) * 1000 + (lon - 29.05) * 500
            elevation = base_elevation + elevation_variation + random.uniform(-20, 20)
            elevation = max(0, min(250, elevation))  # 0-250m arasında sınırla
            
            node_data['elevation'] = round(elevation, 1)
    
    
    def calculate_power_optimized_route(self, start_location, end_location, vehicle_name,
                                       time_of_day='offpeak', avoid_steep=True):
        """
        Araç gücüne optimize edilmiş rota hesapla
        
        Args:
            start_location: Başlangıç (GPS tuple veya lokasyon adı)
            end_location: Varış (GPS tuple veya lokasyon adı)
            vehicle_name (str): Araç adı
            time_of_day (str): 'peak' veya 'offpeak'
            avoid_steep (bool): Dik eğimlerden kaçın
            
        Returns:
            dict: Rota detayları
        """
        if self.router is None:
            print("❌ Rota motoru hazır değil!")
            return None
        
        # Lokasyonları GPS'e çevir
        start_gps = self._resolve_location(start_location)
        end_gps = self._resolve_location(end_location)
        
        if not start_gps or not end_gps:
            print("❌ Lokasyon bulunamadı!")
            return None
        
        print(f"\n{'='*70}")
        print("🚗 ARAÇ GÜCÜNE UYGUN ROTA HESAPLANIYOR")
        print(f"{'='*70}")
        print(f"  Başlangıç: {start_location}")
        print(f"  Varış: {end_location}")
        print(f"  Araç: {vehicle_name}")
        print(f"  Dik eğimlerden kaçın: {'Evet' if avoid_steep else 'Hayır'}")
        print(f"{'='*70}\n")
        
        # Araç kapasitesini kontrol et
        vehicle_cap = self.router.calculate_vehicle_capability(vehicle_name)
        if not vehicle_cap:
            print(f"❌ Araç bulunamadı: {vehicle_name}")
            return None
        
        print(f"📊 Araç Özellikleri:")
        print(f"  • Güç/Ağırlık: {vehicle_cap['power_weight_ratio']} HP/ton")
        print(f"  • Rahat eğim limiti: %{vehicle_cap['comfortable_slope']}")
        print(f"  • Zorlu eğim limiti: %{vehicle_cap['manageable_slope']}")
        print(f"  • Maksimum eğim: %{vehicle_cap['maximum_slope']}\n")
        
        # Optimizasyon modunu belirle
        mode = 'power_optimized' if avoid_steep else 'balanced'
        
        # Rota hesapla
        route = self.router.find_optimal_route(
            start_gps=start_gps,
            end_gps=end_gps,
            vehicle_name=vehicle_name,
            time_of_day=time_of_day,
            mode=mode
        )
        
        if route:
            # Graf düğümlerini ekle (görselleştirme için)
            route['nodes'] = self.current_graph['nodes']
            route['mode'] = mode
        
        return route
    
    
    def compare_routes_for_vehicle(self, start, end, vehicle_name):
        """
        Bir araç için farklı modlarda rota karşılaştır
        
        Args:
            start: Başlangıç lokasyonu
            end: Varış lokasyonu
            vehicle_name: Araç adı
            
        Returns:
            list: Rota listesi
        """
        print(f"\n{'='*70}")
        print(f"📊 ROTA KARŞILAŞTIRMASI: {vehicle_name}")
        print(f"{'='*70}\n")
        
        modes = ['power_optimized', 'fuel_saver', 'time_saver', 'balanced']
        routes = []
        
        for mode in modes:
            print(f"\n🔄 {mode} modu hesaplanıyor...")
            
            # Lokasyonları çözümle
            start_gps = self._resolve_location(start)
            end_gps = self._resolve_location(end)
            
            if not start_gps or not end_gps:
                continue
            
            # Rota hesapla
            route = self.router.find_optimal_route(
                start_gps=start_gps,
                end_gps=end_gps,
                vehicle_name=vehicle_name,
                time_of_day='offpeak',
                mode=mode
            )
            
            if route:
                route['nodes'] = self.current_graph['nodes']
                route['mode'] = mode
                routes.append(route)
        
        # Karşılaştırma tablosu
        if routes:
            self.visualizer.print_route_comparison(routes)
        
        return routes
    
    
    def visualize_and_save(self, route, vehicle_name):
        """
        Rotayı görselleştir ve kaydet
        
        Args:
            route (dict): Rota verisi
            vehicle_name (str): Araç adı
            
        Returns:
            dict: Kaydedilen dosyalar
        """
        if not route:
            print("❌ Görselleştirilecek rota yok!")
            return None
        
        print(f"\n📊 Görselleştirme hazırlanıyor...")
        
        # Dosya adı için araç adını temizle
        safe_vehicle_name = vehicle_name.replace(" ", "_").replace(".", "")
        
        # Görselleştirmeleri kaydet
        saved_files = self.visualizer.save_visualization(
            route_data=route,
            filename_prefix=f"route_{safe_vehicle_name}"
        )
        
        print(f"\n✅ Görselleştirme tamamlandı!")
        print(f"  • Harita: {saved_files.get('map', 'N/A')}")
        print(f"  • Profil: {saved_files.get('profile', 'N/A')}")
        print(f"  • Veri: {saved_files.get('data', 'N/A')}")
        
        # Google Maps linkini göster
        if 'google_maps_url' in route:
            print(f"\n🗺️ Google Maps Linki:")
            print(f"  {route['google_maps_url'][:100]}...")
            print(f"\n  (Tam link veri dosyasında kayıtlı)")
        
        return saved_files
    
    
    def _resolve_location(self, location):
        """
        Lokasyon adını GPS koordinatına çevir
        
        Args:
            location: GPS tuple veya lokasyon adı
            
        Returns:
            tuple: (lat, lon) veya None
        """
        # Zaten GPS tuple ise
        if isinstance(location, (tuple, list)) and len(location) == 2:
            return tuple(location)
        
        # Lokasyon adı ise
        if isinstance(location, str):
            known_locations = BEYKOZ_REGION.get('known_locations', {})
            if location in known_locations:
                return known_locations[location]['gps']
        
        return None
    
    
    def run_demo(self):
        """
        Demo senaryo çalıştır
        """
        print(f"\n{'='*80}")
        print(" "*25 + "DEMO SENARYO")
        print(" "*15 + "Beykoz Bölgesi - Eğim Optimizasyonu")
        print(f"{'='*80}\n")
        
        # 1. Bölgeyi hazırla
        print("📍 Beykoz bölgesi hazırlanıyor...")
        success = self.initialize_region('beykoz', add_elevation=True)
        
        if not success:
            print("❌ Demo çalıştırılamadı!")
            return
        
        # 2. Test lokasyonları
        start = "Beykoz_Sosyal_Tesisleri"
        end = "Karagoz_Sirti_Camii"
        
        print(f"\n📍 ROTA:")
        print(f"  Başlangıç: {start}")
        print(f"  Varış: {end}")
        
        # 3. Farklı araçlar için test
        test_vehicles = [
            "Fiat Egea 1.3 Multijet"
        ]
        
        all_routes = []
        
        for vehicle_name in test_vehicles:
            print(f"\n{'='*70}")
            print(f"🚗 TEST ARACI: {vehicle_name}")
            print(f"{'='*70}")
            
            # Güce optimize rota hesapla
            route = self.calculate_power_optimized_route(
                start_location=start,
                end_location=end,
                vehicle_name=vehicle_name,
                time_of_day='offpeak',
                avoid_steep=True
            )
            
            if route:
                all_routes.append(route)
                
                # Görselleştir ve kaydet
                self.visualize_and_save(route, vehicle_name)
        
        # 4. Araçları karşılaştır
        if len(all_routes) > 1:
            print(f"\n{'='*80}")
            print("ARAÇ KARŞILAŞTIRMASI")
            print(f"{'='*80}\n")
            
            for i, route in enumerate(all_routes):
                vehicle_name = test_vehicles[i]
                print(f"\n{vehicle_name}:")
                print(f"  • Mesafe: {route['total_distance']:.2f} km")
                print(f"  • Yakıt: {route['total_fuel']:.2f} L")
                print(f"  • Maks Eğim: %{route['max_slope']:.1f}")
                print(f"  • Kritik Bölge: {route['critical_sections']} adet")
        
        print(f"\n{'='*80}")
        print("✅ DEMO TAMAMLANDI!")
        print(f"  Sonuçlar {self.output_dir} klasöründe")
        print(f"{'='*80}\n")
    
    
    def interactive_mode(self):
        """
        İnteraktif kullanım modu
        """
        print(f"\n{'='*80}")
        print(" "*20 + "İNTERAKTİF MOD")
        print(f"{'='*80}\n")
        
        # Bölge seç
        print("Bölge seçin:")
        print("1. Beykoz (Hazır)")
        print("2. Özel Koordinat")
        
        choice = input("\nSeçim (1-2): ").strip()
        
        if choice == '1':
            success = self.initialize_region('beykoz', add_elevation=True)
        else:
            print("\nBounding Box girin (min_lat, min_lon, max_lat, max_lon):")
            bbox_str = input("Örnek: 41.10,29.05,41.15,29.10 : ").strip()
            try:
                bbox = tuple(map(float, bbox_str.split(',')))
                success = self.initialize_region('custom', bbox=bbox, add_elevation=True)
            except:
                print("❌ Geçersiz koordinat!")
                return
        
        if not success:
            print("❌ Bölge yüklenemedi!")
            return
        
        # Başlangıç ve bitiş
        print("\n📍 Başlangıç Koordinatı (lat,lon):")
        start_str = input("Örnek: 41.1234,29.0567 : ").strip()
        
        print("\n📍 Varış Koordinatı (lat,lon):")
        end_str = input("Örnek: 41.1456,29.0789 : ").strip()
        
        try:
            start_gps = tuple(map(float, start_str.split(',')))
            end_gps = tuple(map(float, end_str.split(',')))
        except:
            print("❌ Geçersiz koordinat!")
            return
        
        # Araç seç
        print("\n🚗 Araç Seçin:")
        for i, vehicle in enumerate(VEHICLE_DATABASE.keys(), 1):
            print(f"{i}. {vehicle}")
        
        vehicle_idx = int(input("\nAraç numarası: ").strip()) - 1
        vehicle_name = list(VEHICLE_DATABASE.keys())[vehicle_idx]
        
        # Rota hesapla
        print("\n⏳ Rota hesaplanıyor...")
        route = self.calculate_power_optimized_route(
            start_location=start_gps,
            end_location=end_gps,
            vehicle_name=vehicle_name,
            time_of_day='offpeak',
            avoid_steep=True
        )
        
        if route:
            # Görselleştir
            self.visualize_and_save(route, vehicle_name)
            
            print("\n✅ İşlem tamamlandı!")
            print(f"  Sonuçlar {self.output_dir} klasöründe")
        else:
            print("\n❌ Rota hesaplanamadı!")


def main():
    """
    Ana program
    """
    print("\n" + "="*80)
    print(" "*15 + "🗺️ GELİŞTİRİLMİŞ NAVİGASYON SİSTEMİ")
    print(" "*10 + "Eğim Optimizasyonlu • Araç Gücü Analizi • Google Maps")
    print("="*80)
    
    # Sistemi başlat
    system = EnhancedNavigationSystem()
    
    # Menü
    while True:
        print("\n" + "─"*60)
        print("ANA MENÜ")
        print("─"*60)
        print("1. 🎮 Demo Senaryoyu Çalıştır (Beykoz)")
        print("2. 📊 Araç Karşılaştırması Yap")
        print("3. 🗺️ İnteraktif Rota Hesapla")
        print("4. 🚗 Araç Listesi")
        print("5. 📈 Araç Güç Analizi")
        print("0. 🚪 Çıkış")
        print("─"*60)
        
        choice = input("\nSeçim: ").strip()
        
        if choice == '1':
            # Demo
            system.run_demo()
            
        elif choice == '2':
            # Araç karşılaştırması
            print("\n📍 Beykoz bölgesi yükleniyor...")
            system.initialize_region('beykoz', add_elevation=True)
            
            start = "Beykoz_Sosyal_Tesisleri"
            end = "Karagoz_Sirti_Camii"
            
            print("\nAraç seçin:")
            vehicles = list(VEHICLE_DATABASE.keys())
            for i, v in enumerate(vehicles[:5], 1):
                print(f"{i}. {v}")
            
            v_idx = int(input("\nAraç no: ").strip()) - 1
            vehicle = vehicles[v_idx]
            
            routes = system.compare_routes_for_vehicle(start, end, vehicle)
            
            if routes:
                # En iyi rotayı kaydet
                best_route = min(routes, key=lambda x: x['total_fuel'])
                system.visualize_and_save(best_route, vehicle)
            
        elif choice == '3':
            # İnteraktif mod
            system.interactive_mode()
            
        elif choice == '4':
            # Araç listesi
            print(f"\n{'='*70}")
            print("MEVCUT ARAÇLAR")
            print(f"{'='*70}")
            
            for i, (name, specs) in enumerate(VEHICLE_DATABASE.items(), 1):
                print(f"\n{i}. {name}")
                print(f"   Güç: {specs['hp']} HP | Tork: {specs['torque_nm']} Nm")
                print(f"   Ağırlık: {specs['weight_kg']} kg")
                print(f"   Yakıt: {specs['fuel_type']}")
                print(f"   Şehir içi: {specs['fuel_consumption_city']} L/100km")
            
        elif choice == '5':
            # Araç güç analizi
            print(f"\n{'='*70}")
            print("ARAÇ GÜÇ ANALİZİ")
            print(f"{'='*70}")
            
            # Geçici router oluştur
            temp_router = EnhancedRoutingEngine({}, VEHICLE_DATABASE, {})
            
            results = []
            for vehicle_name in VEHICLE_DATABASE.keys():
                cap = temp_router.calculate_vehicle_capability(vehicle_name)
                results.append(cap)
            
            # Güce göre sırala
            results.sort(key=lambda x: x['maximum_slope'], reverse=True)
            
            print(f"\n{'Araç':<30} {'HP/ton':<10} {'Rahat':<8} {'Zorlu':<8} {'Max':<8}")
            print("-"*70)
            
            for r in results:
                print(f"{r['vehicle_name']:<30} {r['power_weight_ratio']:<10.1f} "
                      f"%{r['comfortable_slope']:<7.1f} %{r['manageable_slope']:<7.1f} "
                      f"%{r['maximum_slope']:<7.1f}")
            
        elif choice == '0':
            print("\n👋 Güle güle!\n")
            break
            
        else:
            print("\n❌ Geçersiz seçim!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Program durduruldu")
        print("👋 Güle güle!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
