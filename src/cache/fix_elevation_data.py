"""
Elevation Verilerini Doldur
Mevcut road network JSON dosyasına elevation verilerini ekle
"""

import json
import requests
import time
from tqdm import tqdm

def get_elevation_batch(coordinates):
    """
    Open-Elevation API kullanarak toplu yükseklik verisi al
    
    Args:
        coordinates: [(lat, lon), (lat, lon), ...]
    
    Returns:
        list: Yükseklik değerleri
    """
    try:
        # Open-Elevation API batch endpoint
        url = "https://api.open-elevation.com/api/v1/lookup"
        
        # Locations formatı
        locations = [{"latitude": lat, "longitude": lon} for lat, lon in coordinates]
        
        response = requests.post(
            url,
            json={"locations": locations},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            return [r.get('elevation', 0) for r in results]
        
        return [0] * len(coordinates)
        
    except Exception as e:
        print(f"  ⚠️ Elevation API hatası: {e}")
        return [0] * len(coordinates)


def add_elevations_to_road_network(input_file, output_file, batch_size=100):
    """
    Road network dosyasına elevation verilerini ekle
    
    Args:
        input_file: Giriş JSON dosyası
        output_file: Çıkış JSON dosyası
        batch_size: API'ye gönderilecek nokta sayısı
    """
    print(f"📁 Dosya okunuyor: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        road_network = json.load(f)
    
    nodes = road_network.get('nodes', {})
    
    print(f"📊 Toplam node sayısı: {len(nodes)}")
    print(f"🌐 Elevation verileri alınıyor...")
    
    # Node'ları batch'lere böl
    node_ids = list(nodes.keys())
    total_batches = (len(node_ids) + batch_size - 1) // batch_size
    
    for batch_idx in tqdm(range(total_batches), desc="Elevation verileri"):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, len(node_ids))
        batch_node_ids = node_ids[start_idx:end_idx]
        
        # Koordinatları topla
        coordinates = []
        valid_nodes = []
        
        for node_id in batch_node_ids:
            node = nodes[node_id]
            gps = node.get('gps', [])
            
            if len(gps) >= 2:
                coordinates.append((gps[0], gps[1]))
                valid_nodes.append(node_id)
        
        # Elevation verilerini al
        if coordinates:
            elevations = get_elevation_batch(coordinates)
            
            # Node'lara yaz
            for node_id, elevation in zip(valid_nodes, elevations):
                nodes[node_id]['elevation'] = round(elevation, 2)
        
        # Rate limiting (Open-Elevation için)
        if batch_idx < total_batches - 1:
            time.sleep(1)
    
    # Güncellenmiş veriyi kaydet
    print(f"\n💾 Dosya kaydediliyor: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(road_network, f, indent=2, ensure_ascii=False)
    
    # İstatistikler
    elevations_added = sum(1 for n in nodes.values() if n.get('elevation', 0) > 0)
    print(f"\n✅ Tamamlandı!")
    print(f"  • Elevation eklenen node: {elevations_added}/{len(nodes)}")
    print(f"  • Başarı oranı: {elevations_added/len(nodes)*100:.1f}%")


def check_elevation_data(json_file):
    """
    Mevcut elevation verilerini kontrol et
    """
    print(f"🔍 Kontrol ediliyor: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    nodes = data.get('nodes', {})
    
    with_elevation = 0
    without_elevation = 0
    elevation_sum = 0
    elevation_min = float('inf')
    elevation_max = float('-inf')
    
    for node_id, node_data in nodes.items():
        elevation = node_data.get('elevation', 0)
        
        if elevation > 0:
            with_elevation += 1
            elevation_sum += elevation
            elevation_min = min(elevation_min, elevation)
            elevation_max = max(elevation_max, elevation)
        else:
            without_elevation += 1
    
    print(f"\n📊 Elevation İstatistikleri:")
    print(f"  • Toplam node: {len(nodes)}")
    print(f"  • Elevation var: {with_elevation} (%{with_elevation/len(nodes)*100:.1f})")
    print(f"  • Elevation yok: {without_elevation} (%{without_elevation/len(nodes)*100:.1f})")
    
    if with_elevation > 0:
        print(f"  • Ortalama yükseklik: {elevation_sum/with_elevation:.1f}m")
        print(f"  • Min yükseklik: {elevation_min:.1f}m")
        print(f"  • Max yükseklik: {elevation_max:.1f}m")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Kullanım:")
        print("  1. Kontrol et: python fix_elevation_data.py check beykoz_road_network.json")
        print("  2. Düzelt: python fix_elevation_data.py fix beykoz_road_network.json beykoz_road_network_fixed.json")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        # Mevcut veriyi kontrol et
        input_file = sys.argv[2] if len(sys.argv) > 2 else "beykoz_road_network.json"
        check_elevation_data(input_file)
    
    elif command == "fix":
        # Elevation verilerini ekle
        input_file = sys.argv[2] if len(sys.argv) > 2 else "beykoz_road_network.json"
        output_file = sys.argv[3] if len(sys.argv) > 3 else "beykoz_road_network_fixed.json"
        
        add_elevations_to_road_network(input_file, output_file)
        
        print("\n🔍 Sonuç kontrolü:")
        check_elevation_data(output_file)
    
    else:
        print(f"❌ Bilinmeyen komut: {command}")
        print("Geçerli komutlar: check, fix")