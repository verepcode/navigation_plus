import json
import webbrowser
import sys

def create_detailed_maps_url(route_data):
    """
    JSON dosyasındaki rota bilgisinden detaylı Google Maps URL'i oluşturur.
    """
    nodes = route_data['nodes']
    path = route_data['path']  # 'route' yerine 'path' kullanılıyor
    
    if len(path) < 2:
        print("Hata: Rotada en az 2 nokta olmalı!")
        return None
    
    # İlk ve son nokta
    start_node = nodes[path[0]]
    end_node = nodes[path[-1]]
    start = start_node['gps']
    end = end_node['gps']
    
    print(f"Başlangıç: {start[0]}, {start[1]}")
    print(f"Bitiş: {end[0]}, {end[1]}")
    print(f"Toplam nokta sayısı: {len(path)}")
    
    # Ara noktalar (waypoints) - Google Maps maksimum 9 waypoint destekler
    waypoints = []
    if len(path) > 2:
        # Rotayı eşit aralıklarla böl ve maksimum 9 ara nokta seç
        step = max(1, (len(path) - 2) // 9)
        for i in range(1, len(path) - 1, step):
            if len(waypoints) >= 9:  # Maksimum 9 waypoint
                break
            node = nodes[path[i]]
            gps = node['gps']
            waypoints.append(f"{gps[0]},{gps[1]}")
        
        print(f"Ara nokta sayısı: {len(waypoints)}")
    
    # URL oluştur
    url = f"https://www.google.com/maps/dir/?api=1"
    url += f"&origin={start[0]},{start[1]}"
    url += f"&destination={end[0]},{end[1]}"
    
    if waypoints:
        url += f"&waypoints={'|'.join(waypoints)}"
    
    url += "&travelmode=driving"
    
    return url

def main():
    # JSON dosya yolu
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_file = 'route_Fiat_Egea_13_Multijet_data_20251112_141306.json'
    
    print(f"JSON dosyası okunuyor: {json_file}")
    
    try:
        # JSON dosyasını oku
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("JSON dosyası başarıyla yüklendi.")
        
        # Google Maps URL'sini oluştur
        url = create_detailed_maps_url(data)
        
        if url:
            print(f"\nGoogle Maps URL'si:\n{url}\n")
            
            # Tarayıcıda aç
            print("Google Maps tarayıcıda açılıyor...")
            webbrowser.open(url)
            print("İşlem tamamlandı!")
        
    except FileNotFoundError:
        print(f"Hata: '{json_file}' dosyası bulunamadı!")
    except json.JSONDecodeError as e:
        print(f"Hata: JSON dosyası okunamadı! {e}")
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")

if __name__ == "__main__":
    main()