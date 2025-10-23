"""
Ana Program - Rota Analizi ve Yakıt Tüketimi Hesaplama Uygulaması
Bu program veritabanı, hesaplama ve görselleştirme modüllerini kullanır.
"""

from datetime import datetime
from database import VEHICLE_DATABASE, get_all_vehicles
from visualization import RouteElevationAnalyzer


def print_welcome_message():
    """Karşılama mesajı yazdır"""
    print("="*80)
    print("NAVİGASYON ASISTANI - YAKIT TÜKETİMİ VE ROTA ANALİZİ")
    print("="*80)
    print(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("Modüler yapı ile çalışan versiyon")
    print("-"*80)


def list_available_vehicles():
    """Mevcut araçları listele"""
    print("\n📋 VERİTABANINDAKİ ARAÇLAR:")
    print("-"*40)
    vehicles = get_all_vehicles()
    for i, vehicle in enumerate(vehicles, 1):
        specs = VEHICLE_DATABASE[vehicle]
        print(f"{i:2}. {vehicle}")
        print(f"    └─ {specs['hp']}HP | {specs['fuel_type']} | {specs['fuel_consumption_city']:.1f}L/100km (şehir içi)")
    return vehicles


def get_best_vehicles(vehicle_comparison):
    """En iyi araçları belirle ve öner"""
    print("\n" + "⭐"*40)
    print("EN İYİ ARAÇ ÖNERİLERİ")
    print("="*80)
    
    # En düşük yakıt tüketen
    best_fuel = min(vehicle_comparison.items(), 
                key=lambda x: x[1]['fuel']['total_fuel_liters'])
    print(f"\n⛽ EN AZ YAKIT TÜKETEN:")
    print(f"   {best_fuel[0]}")
    print(f"   └─ {best_fuel[1]['fuel']['total_fuel_liters']:.3f} Litre")
    print(f"   └─ {best_fuel[1]['fuel']['fuel_per_100km']:.2f} L/100km")
    
    # En düşük maliyetli
    best_cost = min(vehicle_comparison.items(), 
                key=lambda x: x[1]['fuel']['fuel_cost_tl'])
    print(f"\n💰 EN DÜŞÜK MALİYETLİ:")
    print(f"   {best_cost[0]}")
    print(f"   └─ {best_cost[1]['fuel']['fuel_cost_tl']:.2f} TL")
    print(f"   └─ {best_cost[1]['specs']['fuel_type']} yakıt")
    
    # En kolay sürüş
    difficulty_order = {'KOLAY': 0, 'ORTA': 1, 'ZOR': 2, 'ÇOK ZOR': 3}
    easiest = min(vehicle_comparison.items(), 
                key=lambda x: difficulty_order[x[1]['capability']['difficulty']])
    print(f"\n🎯 EN KOLAY SÜRÜŞ:")
    print(f"   {easiest[0]}")
    print(f"   └─ Zorluk: {easiest[1]['capability']['difficulty']}")
    print(f"   └─ Güç/Ağırlık: {easiest[1]['capability']['power_to_weight']:.3f} HP/kg")
    
    # En dengeli seçim (yakıt ve zorluk dengesi)
    balanced_scores = {}
    for vehicle, data in vehicle_comparison.items():
        # Normalleştirilmiş skorlar (0-1 arası)
        fuel_score = data['fuel']['fuel_per_100km'] / 10  # 10L/100km üzerinden
        difficulty_score = difficulty_order[data['capability']['difficulty']] / 3
        balanced_scores[vehicle] = (fuel_score + difficulty_score) / 2
    
    best_balanced = min(balanced_scores.items(), key=lambda x: x[1])
    print(f"\n⚖️ EN DENGELİ SEÇİM (Yakıt + Performans):")
    print(f"   {best_balanced[0]}")
    print(f"   └─ Denge skoru: {best_balanced[1]:.3f}")
    
    print("\n" + "="*80)


def main():
    """Ana program"""
    print_welcome_message()
    
    # API anahtarı (dikkat: gerçek uygulamada environment variable kullanın!)
    API_KEY = "AIzaSyDFkQuhvtavuFNPvnrlEFZcbh30BarQ-l4"
    
    # Analyzer oluştur
    print("\n🔧 Analiz motoru başlatılıyor...")
    analyzer = RouteElevationAnalyzer(API_KEY)
    
    # Örnek rota bilgileri
    origin = "Tınaztepe Sokak, Maltepe, İstanbul"
    destination = "Karagöz Sırtı Camii, Beykoz, İstanbul"
    
    print(f"\n📍 ROTA:")
    print(f"   Başlangıç: {origin}")
    print(f"   Varış: {destination}")
    print("-"*80)
    
    # Rota analizi
    print("\n🔍 Rota analizi başlatılıyor...")
    results = analyzer.analyze_route(origin, destination)
    
    if not results:
        print("❌ Rota analizi başarısız! Program sonlandırılıyor.")
        return
    
    # Mevcut araçları listele
    vehicles = list_available_vehicles()
    
    # Örnek araç seç
    example_vehicle = "Fiat Egea 1.3 Multijet"
    time_of_day = 'peak'  # 'peak' veya 'offpeak'
    
    print(f"\n🚗 SEÇİLEN ARAÇ: {example_vehicle}")
    print(f"⏰ ZAMAN DİLİMİ: {'Yoğun Saat (06-10, 17-21)' if time_of_day == 'peak' else 'Seyrek Saat'}")
    print("-"*80)
    
    # Detaylı rapor
    print("\n📊 DETAYLI ANALİZ:")
    analyzer.print_detailed_report(results, example_vehicle, time_of_day)
    
    # Görselleştirme
    print("\n📈 GÖRSELLEŞTİRME:")
    print("   Rota haritası ve analizler oluşturuluyor...")
    analyzer.visualize_route_with_fuel(
        results, 
        example_vehicle, 
        time_of_day,
        save_path='rota_analizi.png',
        origin_name=origin.split(',')[0],  # Sadece sokak adı
        destination_name=destination.split(',')[0]  # Sadece yer adı
    )
    
    # Tüm araçları karşılaştır
    print("\n🔄 TÜM ARAÇLAR KARŞILAŞTIRILIYOR...")
    vehicle_comparison = analyzer.compare_vehicles(results, time_of_day)
    
    # En iyi araçları öner
    get_best_vehicles(vehicle_comparison)
    
    print("\n✅ ANALİZ TAMAMLANDI!")
    print("   📁 Grafikler kaydedildi:")
    print("      - rota_analizi.png")
    print("      - arac_karsilastirma.png")
    print("\n" + "="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Program kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n\n❌ Hata oluştu: {str(e)}")
        print("Lütfen internet bağlantınızı ve API anahtarınızı kontrol edin.")