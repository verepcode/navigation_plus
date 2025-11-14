"""
Road Network Manager - Yol Ağı Yönetim Modülü
OpenStreetMap'ten veri indirme, işleme ve önbellekleme
"""

import json
import os
import time
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
import requests


class RoadNetworkManager:
    """
    Yol ağı verilerini OSM'den indirip işleyen sınıf
    """
    
    def __init__(self, cache_dir='./cache'):
        """
        Args:
            cache_dir (str): Önbellek dizini
        """
        self.cache_dir = cache_dir
        self.nodes = {}
        self.edges = []
        self.bbox = None
        self.last_update = None
        
        # Cache dizinini oluştur
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    
    def cache_exists(self, region_name='default'):
        """
        Belirtilen bölge için cache var mı kontrol et
        
        Args:
            region_name (str): Bölge adı
            
        Returns:
            bool: Cache varsa True
        """
        cache_file = os.path.join(self.cache_dir, f'{region_name}_road_network.json')
        return os.path.exists(cache_file)
    
    
    def download_and_build(self, bbox, region_name='default'):
        """
        OSM'den veri indir ve graf yapısı oluştur
        
        Args:
            bbox (tuple): (min_lat, min_lon, max_lat, max_lon)
            region_name (str): Bölge adı (cache için)
        """
        print(f"\n{'='*60}")
        print(f"YOL AĞI İNDİRİLİYOR: {region_name}")
        print(f"{'='*60}")
        
        # 1. OSM verisi indir
        print("\n[1/6] OpenStreetMap'ten yol verisi indiriliyor...")
        osm_data = self._download_osm_data(bbox)
        
        if not osm_data:
            print("❌ OSM verisi indirilemedi!")
            return False
        
        # 2. Düğümleri ve kenarları parse et
        print("\n[2/6] Yol ağı parse ediliyor...")
        self._parse_osm_data(osm_data)
        
        # 3. Elevation verisi ekle
        print("\n[3/6] Rakım verileri alınıyor...")
        self._enrich_with_elevation()
        
        # 4. Kenar özelliklerini hesapla
        print("\n[4/6] Yol özellikleri hesaplanıyor...")
        self._calculate_edge_properties()
        
        # 5. Trafik bölgeleri ile eşleştir
        print("\n[5/6] Trafik bölgeleri eşleştiriliyor...")
        self._match_traffic_zones()
        
        # 6. Cache'e kaydet
        print("\n[6/6] Önbelleğe kaydediliyor...")
        self.save_cache(region_name)
        
        print(f"\n{'='*60}")
        print("✓ YOL AĞI HAZIR!")
        print(f"  • Toplam düğüm: {len(self.nodes)}")
        print(f"  • Toplam kenar: {len(self.edges)}")
        print(f"{'='*60}\n")
        
        return True
    
    
    def _download_osm_data(self, bbox):
        """
        Overpass API kullanarak OSM verisi indir
        
        Args:
            bbox (tuple): (min_lat, min_lon, max_lat, max_lon)
            
        Returns:
            dict: OSM JSON verisi
        """
        min_lat, min_lon, max_lat, max_lon = bbox
        self.bbox = bbox
        
        # Overpass API sorgusu
        overpass_url = "http://overpass-api.de/api/interpreter"
        
        # Sorgu: Sadece araç yolları (highway), yaya/bisiklet yolları hariç
        overpass_query = f"""
        [out:json][timeout:90];
        (
          way["highway"]["highway"!="footway"]["highway"!="path"]
              ["highway"!="cycleway"]["highway"!="pedestrian"]
              ["highway"!="steps"]["highway"!="track"]
              ({min_lat},{min_lon},{max_lat},{max_lon});
        );
        out body;
        >;
        out skel qt;
        """
        
        try:
            print(f"   Bölge: {bbox}")
            print("   API'ye bağlanılıyor...")
            
            response = requests.post(
                overpass_url,
                data={'data': overpass_query},
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # İstatistikler
                nodes_count = len([e for e in data['elements'] if e['type'] == 'node'])
                ways_count = len([e for e in data['elements'] if e['type'] == 'way'])
                
                print(f"   ✓ Başarılı!")
                print(f"   ✓ {nodes_count} düğüm, {ways_count} yol indirildi")
                
                return data
            else:
                print(f"   ❌ HTTP Hatası: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("   ❌ Zaman aşımı! API yanıt vermiyor.")
            return None
        except Exception as e:
            print(f"   ❌ Hata: {str(e)}")
            return None
    
    
    def _parse_osm_data(self, osm_data):
        """
        OSM JSON verisini düğümler ve kenarlara dönüştür
        
        Args:
            osm_data (dict): OSM JSON verisi
        """
        elements = osm_data.get('elements', [])
        
        # Önce tüm node'ları topla
        osm_nodes = {}
        for element in elements:
            if element['type'] == 'node':
                node_id = str(element['id'])
                osm_nodes[node_id] = {
                    'gps': (element['lat'], element['lon']),
                    'elevation': None  # Sonra eklenecek
                }
        
        # Way'leri işle ve kenarlar oluştur
        edge_count = 0
        for element in elements:
            if element['type'] == 'way':
                way_nodes = element.get('nodes', [])
                tags = element.get('tags', {})
                
                # Yol bilgileri
                highway_type = tags.get('highway', 'unclassified')
                street_name = tags.get('name', 'Unnamed Road')
                
                # Tek yön kontrolü
                oneway = tags.get('oneway', 'no')
                if oneway in ['yes', '1', 'true']:
                    direction = 'oneway'
                elif oneway == '-1':
                    direction = 'reverse_only'
                else:
                    direction = 'bidirectional'
                
                # Hız limiti
                maxspeed = tags.get('maxspeed', '50')
                try:
                    speed_limit = int(maxspeed)
                except:
                    speed_limit = 50
                
                # Şerit sayısı
                lanes = tags.get('lanes', '1')
                try:
                    lane_count = int(lanes)
                except:
                    lane_count = 1
                
                # Ardışık düğümler arasında kenarlar oluştur
                for i in range(len(way_nodes) - 1):
                    node_from = str(way_nodes[i])
                    node_to = str(way_nodes[i + 1])
                    
                    # Her iki düğüm de varsa kenar oluştur
                    if node_from in osm_nodes and node_to in osm_nodes:
                        edge = {
                            'from': node_from,
                            'to': node_to,
                            'direction': direction,
                            'road_type': highway_type,
                            'street_name': street_name,
                            'speed_limit': speed_limit,
                            'lanes': lane_count,
                            # Aşağıdakiler sonra hesaplanacak
                            'distance': None,
                            'elevation_gain': None,
                            'slope_percent': None,
                            'traffic_zone': None,
                            'avg_speed_peak': None,
                            'avg_speed_offpeak': None
                        }
                        
                        self.edges.append(edge)
                        edge_count += 1
        
        # Node'ları kaydet
        self.nodes = osm_nodes
        
        print(f"   ✓ {len(self.nodes)} düğüm işlendi")
        print(f"   ✓ {edge_count} kenar oluşturuldu")
    
    
    def _enrich_with_elevation(self):
        """
        Google Elevation API kullanarak rakım verisi ekle
        """
        if not self.nodes:
            print("   ⚠ Düğüm bulunamadı!")
            return
        
        # API anahtarı (environment variable'dan al)
        api_key = os.environ.get('GOOGLE_ELEVATION_API_KEY', 
                                 'AIzaSyDFkQuhvtavuFNPvnrlEFZcbh30BarQ-l4')
        
        # Batch halinde işle (512 nokta/istek)
        batch_size = 512
        node_list = list(self.nodes.items())
        total_batches = (len(node_list) + batch_size - 1) // batch_size
        
        print(f"   Toplam {len(node_list)} düğüm için rakım alınacak")
        print(f"   {total_batches} batch işlenecek (her batch {batch_size} nokta)")
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(node_list))
            batch = node_list[start_idx:end_idx]
            
            # GPS koordinatlarını topla
            locations = [node_data['gps'] for node_id, node_data in batch]
            locations_str = '|'.join([f"{lat},{lon}" for lat, lon in locations])
            for lat, lon in locations:
                print(f"{lat},{lon}")
            
            # API isteği
            url = f"https://maps.googleapis.com/maps/api/elevation/json"
            params = {
                'locations': locations_str,
                'key': api_key
            }
            
            try:
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data['status'] == 'OK':
                        results = data['results']
                        print(f"Received elevation")
                        # Sonuçları düğümlere ekle
                        for idx, (node_id, node_data) in enumerate(batch):
                            print(f"elevation_from api: {results[idx]['elevation']}")
                            if idx < len(results):
                                
                                self.nodes[node_id]['elevation'] = results[idx]['elevation']
                        
                        print(f"   ✓ Batch {batch_num + 1}/{total_batches} tamamlandı")
                    else:
                        print(f"   ⚠ Batch {batch_num + 1} API hatası: {data['status']}")
                else:
                    print(f"   ⚠ Batch {batch_num + 1} HTTP hatası: {response.status_code}")
                
                # Rate limiting için kısa bekleme
                time.sleep(0.2)
                
            except Exception as e:
                print(f"   ⚠ Batch {batch_num + 1} hatası: {str(e)}")
        
        # Eksik elevation'ları kontrol et
        missing = sum(1 for node in self.nodes.values() if node['elevation'] is None)
        if missing > 0:
            print(f"   ⚠ {missing} düğümün rakımı alınamadı (varsayılan: 0m)")
            # Eksikleri 0 yap
            for node_data in self.nodes.values():
                if node_data['elevation'] is None:
                    node_data['elevation'] = 0
    
    
    def _calculate_edge_properties(self):
        """
        Her kenar için mesafe, eğim ve diğer özellikleri hesapla
        """
        if not self.edges:
            print("   ⚠ Kenar bulunamadı!")
            return
        
        for edge in self.edges:
            node_from = self.nodes.get(edge['from'])
            node_to = self.nodes.get(edge['to'])
            
            if not node_from or not node_to:
                continue
            
            # 1. Mesafe (Haversine)
            lat1, lon1 = node_from['gps']
            lat2, lon2 = node_to['gps']
            edge['distance'] = self._haversine_distance(lat1, lon1, lat2, lon2)
            
            # 2. Yükselti farkı ve eğim
            elev1 = node_from['elevation'] or 0
            elev2 = node_to['elevation'] or 0
            edge['elevation_gain'] = elev2 - elev1
            
            if edge['distance'] > 0:
                edge['slope_percent'] = (edge['elevation_gain'] / edge['distance']) * 100
            else:
                edge['slope_percent'] = 0
        
        print(f"   ✓ {len(self.edges)} kenar için özellikler hesaplandı")
    
    
    def _match_traffic_zones(self):
        """
        Her kenarı database.py'deki trafik bölgeleri ile eşleştir
        """
        try:
            from database import TRAFFIC_ZONES
        except ImportError:
            print("   ⚠ database.py bulunamadı, varsayılan değerler kullanılacak")
            TRAFFIC_ZONES = {}
        
        # Varsayılan değerler
        default_zone = {
            'avg_speed_peak': 30,
            'avg_speed_offpeak': 50,
            'traffic_multiplier': 1.5
        }
        
        for edge in self.edges:
            # Kenarın orta noktasını al
            node_from = self.nodes.get(edge['from'])
            if not node_from:
                continue
            
            lat, lon = node_from['gps']
            
            # En yakın zone'u bul (basit yaklaşım: bbox kontrolü)
            # Gerçek uygulamada daha sofistike eşleştirme yapılmalı
            matched_zone = None
            
            # Önce yol tipine göre genel bir zone bul
            road_type = edge['road_type']
            
            if road_type in ['motorway', 'trunk']:
                # Otoyol tipi
                for zone_key, zone_data in TRAFFIC_ZONES.items():
                    if zone_data.get('road_type') == 'Otoyol':
                        matched_zone = zone_data
                        break
            elif road_type in ['primary', 'secondary']:
                # Ana arter
                for zone_key, zone_data in TRAFFIC_ZONES.items():
                    if zone_data.get('road_type') == 'Ana Arter':
                        matched_zone = zone_data
                        break
            elif road_type in ['residential', 'tertiary']:
                # Mahalle içi
                for zone_key, zone_data in TRAFFIC_ZONES.items():
                    if zone_data.get('road_type') == 'Şehir İçi':
                        matched_zone = zone_data
                        break
            
            # Zone bulunamadıysa varsayılan kullan
            if not matched_zone:
                matched_zone = default_zone
            
            # Kenar bilgilerini güncelle
            edge['avg_speed_peak'] = matched_zone.get('avg_speed_peak', 30)
            edge['avg_speed_offpeak'] = matched_zone.get('avg_speed_offpeak', 50)
            edge['traffic_multiplier'] = matched_zone.get('traffic_multiplier', 1.5)
        
        print(f"   ✓ Trafik bölgeleri eşleştirildi")
    
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        İki GPS noktası arası mesafe (metre)
        
        Args:
            lat1, lon1: İlk nokta (derece)
            lat2, lon2: İkinci nokta (derece)
            
        Returns:
            float: Mesafe (metre)
        """
        # Radyana çevir
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formülü
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Dünya yarıçapı (metre)
        r = 6371000
        
        return r * c
    
    
    def save_cache(self, region_name='default'):
        """
        Graf verisini JSON olarak kaydet
        
        Args:
            region_name (str): Bölge adı
        """
        cache_file = os.path.join(self.cache_dir, f'{region_name}_road_network.json')
        
        cache_data = {
            'nodes': self.nodes,
            'edges': self.edges,
            'bbox': self.bbox,
            'last_update': datetime.now().isoformat(),
            'stats': {
                'node_count': len(self.nodes),
                'edge_count': len(self.edges)
            }
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        print(f"   ✓ Cache kaydedildi: {cache_file}")
        print(f"   ✓ Dosya boyutu: {os.path.getsize(cache_file) / 1024:.1f} KB")
    
    
    def load_cache(self, region_name='default'):
        """
        Önbellekten yükle
        
        Args:
            region_name (str): Bölge adı
            
        Returns:
            bool: Başarılı ise True
        """
        cache_file = os.path.join(self.cache_dir, f'{region_name}_road_network.json')
        
        if not os.path.exists(cache_file):
            print(f"   ❌ Cache bulunamadı: {cache_file}")
            return False
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            self.nodes = cache_data['nodes']
            self.edges = cache_data['edges']
            self.bbox = tuple(cache_data['bbox']) if cache_data['bbox'] else None
            self.last_update = cache_data.get('last_update')
            
            stats = cache_data.get('stats', {})
            
            test_node = list(cache_data['nodes'].values())[0]
            print(f"🔍 Dosyadan yüklenen ilk node elevation: {test_node.get('elevation')}")
            if test_node.get('elevation') == 0:
                print("❌ SORUN: Dosyada elevation=0!")
                print(f"   Kontrol: grep -A 3 'elevation' beykoz_road_network.json | head -10")
            else:
                print(f"✅ Dosyada elevation VAR: {test_node.get('elevation')}m")
            print(f"   ✓ Cache yüklendi: {cache_file}")
            print(f"   ✓ {stats.get('node_count', 0)} düğüm, {stats.get('edge_count', 0)} kenar")
            print(f"   ✓ Son güncelleme: {self.last_update}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Cache yükleme hatası: {str(e)}")
            return False
    
    
    def get_graph(self):
        """
        Graf verisini döndür
        
        Returns:
            dict: {'nodes': dict, 'edges': list}
        """
        return {
            'nodes': self.nodes,
            'edges': self.edges,
            'bbox': self.bbox,
            'last_update': self.last_update
        }
    
    
    def find_nearest_node(self, lat, lon, max_distance_m=500):
        """
        Verilen GPS koordinatına en yakın düğümü bul
        
        Args:
            lat (float): Enlem
            lon (float): Boylam
            max_distance_m (float): Maksimum arama mesafesi (metre)
            
        Returns:
            tuple: (node_id, distance) veya (None, None)
        """
        min_distance = float('inf')
        nearest_node = None
        
        for node_id, node_data in self.nodes.items():
            node_lat, node_lon = node_data['gps']
            distance = self._haversine_distance(lat, lon, node_lat, node_lon)
            
            if distance < min_distance and distance <= max_distance_m:
                min_distance = distance
                nearest_node = node_id
        
        if nearest_node:
            return nearest_node, min_distance
        
        return None, None
    
    
    def get_node_info(self, node_id):
        """
        Düğüm bilgisini getir
        
        Args:
            node_id (str): Düğüm ID
            
        Returns:
            dict: Düğüm bilgileri
        """
        return self.nodes.get(node_id)
    
    
    def get_edges_from_node(self, node_id):
        """
        Belirli bir düğümden çıkan kenarları getir
        
        Args:
            node_id (str): Düğüm ID
            
        Returns:
            list: Kenar listesi
        """
        return [edge for edge in self.edges if edge['from'] == node_id]
    
    
    def get_edges_to_node(self, node_id):
        """
        Belirli bir düğüme gelen kenarları getir
        
        Args:
            node_id (str): Düğüm ID
            
        Returns:
            list: Kenar listesi
        """
        return [edge for edge in self.edges if edge['to'] == node_id]


# Yardımcı fonksiyonlar

def validate_bbox(bbox):
    """
    Bounding box'ın geçerli olup olmadığını kontrol et
    
    Args:
        bbox (tuple): (min_lat, min_lon, max_lat, max_lon)
        
    Returns:
        bool: Geçerli ise True
    """
    if not isinstance(bbox, (tuple, list)) or len(bbox) != 4:
        return False
    
    min_lat, min_lon, max_lat, max_lon = bbox
    
    # Koordinat aralıkları
    if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
        return False
    if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
        return False
    
    # Min < Max kontrolü
    if min_lat >= max_lat or min_lon >= max_lon:
        return False
    
    return True


def calculate_bbox_size(bbox):
    """
    Bounding box'ın yaklaşık boyutunu hesapla (km²)
    
    Args:
        bbox (tuple): (min_lat, min_lon, max_lat, max_lon)
        
    Returns:
        float: Alan (km²)
    """
    min_lat, min_lon, max_lat, max_lon = bbox
    
    # Orta noktadaki yaklaşık mesafeler
    lat_dist = (max_lat - min_lat) * 111  # 1 derece enlem ≈ 111 km
    lon_dist = (max_lon - min_lon) * 111 * cos(radians((min_lat + max_lat) / 2))
    
    return lat_dist * lon_dist


# Test fonksiyonu
if __name__ == "__main__":
    print("Road Network Manager - Test")
    print("="*60)
    
    # Beykoz bölgesi
    BEYKOZ_BBOX = (41.10, 29.05, 41.15, 29.15)
    
    # Bbox doğrulama
    if validate_bbox(BEYKOZ_BBOX):
        print("✓ Bounding box geçerli")
        print(f"  Alan: {calculate_bbox_size(BEYKOZ_BBOX):.2f} km²")
    else:
        print("❌ Bounding box geçersiz")
    
    # Manager oluştur
    manager = RoadNetworkManager(cache_dir='./cache')
    
    # Cache kontrolü
    if manager.cache_exists('beykoz'):
        print("\n Cache mevcut, yükleniyor...")
        manager.load_cache('beykoz')
    else:
        print("\n⚠ Cache yok, indiriliyor...")
        manager.download_and_build(BEYKOZ_BBOX, 'beykoz')
    
    # İstatistikler
    graph = manager.get_graph()
    print(f"\nGraf İstatistikleri:")
    print(f"  Düğüm sayısı: {len(graph['nodes'])}")
    print(f"  Kenar sayısı: {len(graph['edges'])}")
    
    # En yakın düğüm testi
    test_gps = (41.1133, 29.0877)  # Beykoz Sosyal Tesisleri
    nearest, distance = manager.find_nearest_node(*test_gps)
    if nearest:
        print(f"\nTest GPS: {test_gps}")
        print(f"  En yakın düğüm: {nearest}")
        print(f"  Uzaklık: {distance:.1f} metre")
