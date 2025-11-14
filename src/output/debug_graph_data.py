"""
Grafik Verilerini Debug Et
Neden 0 göründüğünü bul
"""

import json
import sys

def debug_route_data(json_file):
    """
    Rota JSON dosyasını analiz et ve sorunları bul
    """
    print(f"🔍 Analiz ediliyor: {json_file}\n")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        route_data = json.load(f)
    
    print("="*70)
    print("1. GENEL BİLGİLER")
    print("="*70)
    
    # Ana metrikler
    metrics = {
        'total_distance_km': 'Toplam Mesafe',
        'total_time_minutes': 'Toplam Süre',
        'total_fuel_liters': 'Toplam Yakıt',
        'max_slope': 'Maksimum Eğim'
    }
    
    for key, label in metrics.items():
        value = route_data.get(key, 0)
        status = "✅" if value > 0 else "❌ SIFIR!"
        print(f"  {status} {label}: {value}")
    
    print("\n" + "="*70)
    print("2. SEGMENTS ANALİZİ")
    print("="*70)
    
    segments = route_data.get('segments', [])
    print(f"  Toplam segment: {len(segments)}")
    
    if not segments:
        print("  ❌ HİÇ SEGMENT YOK!")
        return
    
    # İlk birkaç segment'i kontrol et
    print(f"\n  İlk 3 Segment:")
    for i, seg in enumerate(segments[:3]):
        print(f"\n  Segment {i+1}:")
        print(f"    • Distance: {seg.get('distance', 0)}")
        print(f"    • Slope: {seg.get('slope', 0)}")
        print(f"    • From Elevation: {seg.get('from_elevation', 0)}")
        print(f"    • To Elevation: {seg.get('to_elevation', 0)}")
        print(f"    • Elevation Change: {seg.get('elevation_change', 0)}")
    
    # Elevation istatistikleri
    elevations = []
    slopes = []
    distances = []
    
    for seg in segments:
        from_elev = seg.get('from_elevation', 0)
        to_elev = seg.get('to_elevation', 0)
        elevations.extend([from_elev, to_elev])
        slopes.append(seg.get('slope', 0))
        distances.append(seg.get('distance', 0))
    
    print("\n" + "="*70)
    print("3. İSTATİSTİKLER")
    print("="*70)
    
    # Elevation
    non_zero_elevations = [e for e in elevations if e != 0]
    if non_zero_elevations:
        print(f"  ✅ Elevation Verileri:")
        print(f"    • Min: {min(non_zero_elevations):.1f}m")
        print(f"    • Max: {max(non_zero_elevations):.1f}m")
        print(f"    • Ortalama: {sum(non_zero_elevations)/len(non_zero_elevations):.1f}m")
    else:
        print(f"  ❌ TÜM ELEVATION DEĞERLERİ 0!")
        print(f"     Bu grafiklerin düz çizgi görünmesine neden olur.")
    
    # Slope
    non_zero_slopes = [s for s in slopes if s != 0]
    if non_zero_slopes:
        print(f"\n  ✅ Eğim Verileri:")
        print(f"    • Min: {min(slopes):.1f}%")
        print(f"    • Max: {max(slopes):.1f}%")
        print(f"    • Ortalama: {sum(slopes)/len(slopes):.1f}%")
    else:
        print(f"\n  ❌ TÜM EĞİM DEĞERLERİ 0!")
        print(f"     Bu eğim grafiğinin boş görünmesine neden olur.")
    
    # Distance
    non_zero_distances = [d for d in distances if d != 0]
    if non_zero_distances:
        print(f"\n  ✅ Mesafe Verileri:")
        print(f"    • Toplam: {sum(distances)/1000:.2f}km")
        print(f"    • Ortalama segment: {sum(distances)/len(distances):.1f}m")
    else:
        print(f"\n  ❌ TÜM MESAFE DEĞERLERİ 0!")
    
    print("\n" + "="*70)
    print("4. NODES KONTROLÜ")
    print("="*70)
    
    nodes = route_data.get('nodes', {})
    print(f"  Toplam node: {len(nodes)}")
    
    if nodes:
        # İlk node'u kontrol et
        first_node_id = list(nodes.keys())[0]
        first_node = nodes[first_node_id]
        
        print(f"\n  İlk Node ({first_node_id}):")
        print(f"    • GPS: {first_node.get('gps', [])}")
        print(f"    • Elevation: {first_node.get('elevation', 0)}")
        
        # Node elevation istatistikleri
        node_elevations = [n.get('elevation', 0) for n in nodes.values()]
        non_zero_node_elevations = [e for e in node_elevations if e != 0]
        
        if non_zero_node_elevations:
            print(f"\n  ✅ Node Elevation Verileri:")
            print(f"    • Sıfır olmayan: {len(non_zero_node_elevations)}/{len(nodes)}")
            print(f"    • Min: {min(non_zero_node_elevations):.1f}m")
            print(f"    • Max: {max(non_zero_node_elevations):.1f}m")
        else:
            print(f"\n  ❌ TÜM NODE ELEVATION DEĞERLERİ 0!")
            print(f"     SORUN BURADA! Node'larda elevation verisi yok.")
    
    print("\n" + "="*70)
    print("5. SORUN TESPİTİ VE ÇÖZÜM")
    print("="*70)
    
    problems = []
    
    # Elevation kontrolü
    if not non_zero_elevations:
        problems.append({
            'problem': 'Elevation verileri yok',
            'solution': 'fix_elevation_data.py script\'ini çalıştırın'
        })
    
    # Slope kontrolü
    if not non_zero_slopes:
        problems.append({
            'problem': 'Eğim verileri yok',
            'solution': 'Elevation verileri eklendikten sonra rotayı yeniden hesaplayın'
        })
    
    # Distance kontrolü
    if not non_zero_distances:
        problems.append({
            'problem': 'Mesafe verileri yok',
            'solution': 'GPS koordinatlarını kontrol edin'
        })
    
    if problems:
        print("\n  ❌ BULUNAN SORUNLAR:")
        for i, p in enumerate(problems, 1):
            print(f"\n  {i}. {p['problem']}")
            print(f"     ➡️  ÇÖZÜM: {p['solution']}")
    else:
        print("\n  ✅ Veri sounu bulunamadı!")
        print("     Grafik oluşturma kodunda sorun olabilir.")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python debug_graph_data.py <route_json_file>")
        print("Örnek: python debug_graph_data.py route_Fiat_Egea_13_Multijet_data_20251102_135750.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    debug_route_data(json_file)