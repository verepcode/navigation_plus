"""
Minimal Routing Test - Elevation Kontrolü
"""

import json
import sys

# Modül import
sys.path.insert(0, '/home/ali/navigation_plus/src')
from enhanced_routing_engine import EnhancedRoutingEngine

print("="*70)
print("🧪 MINIMAL ROUTING TEST")
print("="*70)

# Veri yükle
print("\n📁 Veri yükleniyor...")
with open('beykoz_road_network.json', 'r', encoding='utf-8') as f:
    road_network = json.load(f)

with open('vehicle_database.json', 'r', encoding='utf-8') as f:
    vehicle_db = json.load(f)

with open('traffic_zones.json', 'r', encoding='utf-8') as f:
    traffic_zones = json.load(f)

# Engine oluştur
print("🔧 Engine başlatılıyor...")
engine = EnhancedRoutingEngine(road_network, vehicle_db, traffic_zones)

# Node elevation kontrolü
print("\n🔍 Node Elevation Kontrolü:")
nodes = road_network['nodes']
sample_node_id = '1634366281'  # Sizin örneğinizdeki node

if sample_node_id in nodes:
    sample_node = nodes[sample_node_id]
    print(f"  Node ID: {sample_node_id}")
    print(f"  GPS: {sample_node['gps']}")
    print(f"  Elevation: {sample_node['elevation']}")
else:
    # İlk node'u al
    sample_node_id = list(nodes.keys())[0]
    sample_node = nodes[sample_node_id]
    print(f"  Node ID: {sample_node_id}")
    print(f"  GPS: {sample_node['gps']}")
    print(f"  Elevation: {sample_node.get('elevation', 'YOK!')}")

# calculate_slope testi
print("\n🧮 calculate_slope() Testi:")
# İki ardışık node al
node_ids = list(nodes.keys())[:2]
from_id = node_ids[0]
to_id = node_ids[1]

print(f"  From Node: {from_id}")
print(f"    GPS: {nodes[from_id]['gps']}")
print(f"    Elevation: {nodes[from_id].get('elevation', 'YOK!')}")

print(f"  To Node: {to_id}")
print(f"    GPS: {nodes[to_id]['gps']}")
print(f"    Elevation: {nodes[to_id].get('elevation', 'YOK!')}")

slope_result = engine.calculate_slope(from_id, to_id)

print(f"\n  📊 Sonuç:")
print(f"    Slope: {slope_result['slope_percent']}%")
print(f"    From Elevation: {slope_result['from_elevation']}m")
print(f"    To Elevation: {slope_result['to_elevation']}m")
print(f"    Elevation Change: {slope_result['elevation_change']}m")
print(f"    Distance: {slope_result['distance_m']}m")

# Değerlendirme
print("\n" + "="*70)
print("📋 DEĞERLENDİRME")
print("="*70)

if slope_result['from_elevation'] == 0 and slope_result['to_elevation'] == 0:
    print("❌ SORUN VAR: Elevation değerleri 0!")
    print("   calculate_slope() elevation okuyamıyor!")
    
    print("\n🔍 Debug bilgisi:")
    # Engine'deki nodes'u kontrol et
    engine_node = engine.nodes.get(from_id, {})
    print(f"   Engine'deki node keys: {list(engine_node.keys())}")
    print(f"   Engine'deki elevation: {engine_node.get('elevation', 'YOK!')}")
    
elif slope_result['from_elevation'] == 50 and slope_result['to_elevation'] == 50:
    print("⚠️ SORUN VAR: Default değerler (50) kullanılıyor!")
    print("   Elevation okunamıyor, default'a düşüyor!")
    
else:
    print("✅ calculate_slope() DOĞRU ÇALIŞIYOR!")
    print(f"   Elevation değerleri gerçek: {slope_result['from_elevation']}m - {slope_result['to_elevation']}m")

print("\n" + "="*70)