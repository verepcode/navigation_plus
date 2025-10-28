"""
Ana Program - Rota Analizi ve Alternatif Rota Önerisi (Geliştirilmiş)
Kritik eğim bölgeleri tespit edilir ve alternatif rotalar önerilir.
"""

from datetime import datetime
from database import (VEHICLE_DATABASE, get_all_vehicles, 
                     FUEL_PRICES, PEAK_HOURS, is_peak_hour)
from visualization_enhanced import RouteElevationAnalyzer


def print_welcome_message():
    """Karşılama mesajı yazdır"""
    print("="*80)
    print("NAVİGASYON ASISTANI - AKILLI ROTA SEÇİMİ v3.0")
    print("Kritik Eğim Tespiti ve Alternatif Rota Önerisi")
    print("="*80)
    print(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("-"*80)
    print("📊 GÜNCEL YAKIT FİYATLARI:")
    for fuel_type, price in FUEL_PRICES.items():
        print(f"   {fuel_type}: {price:.2f} TL/Litre")
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


def main():
    """Ana program"""
    print_welcome_message()
    
    # API anahtarı
    API_KEY = "AIzaSyDFkQuhvtavuFNPvnrlEFZcbh30BarQ-l4"
    
    # Analyzer oluştur
    print("\n🔧 Gelişmiş analiz motoru başlatılıyor...")
    print("   ✓ Kritik eğim tespiti aktif")
    print("   ✓ Alternatif rota arama aktif")
    print("   ✓ Çoklu rota karşılaştırması aktif")
    
    analyzer = RouteElevationAnalyzer(API_KEY)
    
    # Örnek rota bilgileri
    origin = "Beykoz Sosyal Tesisleri, Beykoz, İstanbul"
    destination = "Karagöz Sırtı Camii, Beykoz, İstanbul"
    
    print(f"\n📍 ROTA:")
    print(f"   Başlangıç: {origin}")
    print(f"   Varış: {destination}")
    print("-"*80)
    
    # Çoklu rota analizi (orijinal + alternatifler)
    print("\n🔍 Rota analizi başlatılıyor...")
    print("   → Orijinal rota analiz ediliyor")
    print("   → Alternatif rotalar aranıyor")
    print("   → Kritik eğim bölgeleri tespit ediliyor")
    
    route_analyses = analyzer.analyze_route(
        origin, 
        destination, 
        num_samples=50,
        include_alternatives=True  # Alternatif rotaları dahil et
    )
    
    if not route_analyses:
        print("❌ Rota analizi başarısız! Program sonlandırılıyor.")
        return
    
    # Mevcut araçları listele
    # vehicles = list_available_vehicles()
    
    # Örnek araç seç
    example_vehicle = "Fiat Egea 1.3 Multijet"
    
    # Otomatik olarak peak/offpeak belirle
    current_hour = datetime.now().hour
    time_of_day = 'peak' if is_peak_hour(current_hour) else 'offpeak'
    time_description = 'YOĞUN SAAT (07:00-10:00, 17:00-20:00)' if time_of_day == 'peak' else 'SEYREK SAAT'
    
    print(f"\n🚗 SEÇİLEN ARAÇ: {example_vehicle}")
    print(f"⏰ ŞU ANKİ SAAT: {datetime.now().strftime('%H:%M')}")
    print(f"📊 TRAFİK DURUMU: {time_description}")
    print("-"*80)
    
    # Rota sayısını bildir
    total_routes = len(route_analyses.get('routes', []))
    print(f"\n✓ Toplam {total_routes} rota analiz edildi:")
    print(f"  • 1 Orijinal Rota")
    if total_routes > 1:
        print(f"  • {total_routes - 1} Alternatif Rota")
    
    # Kritik bölgeleri rapor et
    original_route = route_analyses.get('original_route')
    if original_route:
        critical_count = len(original_route.get('critical_sections', []))
        if critical_count > 0:
            print(f"\n⚠️  ORİJİNAL ROTADA {critical_count} KRİTİK BÖLGE TESPİT EDİLDİ!")
            print(f"   → %15'ten dik eğimli yollar bulundu")
            if total_routes > 1:
                print(f"   → Alternatif rotalar önerildi")
        else:
            print(f"\n✓ Orijinal rotada kritik eğim bölgesi yok")
    
    # Detaylı karşılaştırma raporu
    analyzer.print_route_comparison_report(route_analyses, example_vehicle, time_of_day)
    
    # Görselleştirme - Rota Karşılaştırması
    print("\n📈 GÖRSELLEŞTİRME:")
    print("   Rota karşılaştırma grafikleri oluşturuluyor...")
    analyzer.visualize_route_comparison(
        route_analyses,
        example_vehicle,
        time_of_day,
        save_path='rota_karsilastirma.png'
    )
    
    # Özet istatistikler
    print("\n" + "="*80)
    print("📋 ÖZET İSTATİSTİKLER")
    print("="*80)
    
    # Karşılaştırma sonuçlarını göster
    comparison = analyzer.compare_routes(route_analyses, example_vehicle, time_of_day)
    if comparison and comparison['comparisons']:
        print("\nRota Özeti:")
        print(f"{'Rota':<25} {'Mesafe':<12} {'Maliyet':<12} {'Kritik Bölge':<15}")
        print("-" * 65)
        
        for comp in comparison['comparisons']:
            route_name = comp['route_name'][:23]
            if comp['is_recommended']:
                route_name += " ⭐"
            
            distance = f"{comp['distance_km']:.1f} km"
            cost = f"{comp['fuel_consumption']['total_cost_tl']:.1f} TL"
            critical = f"{comp['critical_sections_count']} bölge"
            
            print(f"{route_name:<25} {distance:<12} {cost:<12} {critical:<15}")
        
        # En iyi öneri
        if comparison['recommended_route']:
            rec = comparison['recommended_route']
            print("\n" + "="*80)
            print("🎯 ÖNERİLEN ROTA")
            print("="*80)
            print(f"Rota: {rec['route_name']}")
            print(f"Sebep: ")
            print(f"  • En uygun maliyet: {rec['fuel_consumption']['total_cost_tl']:.2f} TL")
            print(f"  • Kritik bölge sayısı: {rec['critical_sections_count']}")
            print(f"  • Zorluk seviyesi: {rec['capability']['difficulty']}")
            
            # Google Maps linki
            if comparison.get('google_maps_link'):
                print(f"\n🗺️  GOOGLE MAPS LİNKİ:")
                print(f"   {comparison['google_maps_link']}")
                print(f"\n   👆 Bu linke tıklayarak rotayı Google Maps'te görüntüleyebilirsiniz!")
            
            # Tasarruf hesapla (en pahalı rotaya göre)
            max_cost = max([c['fuel_consumption']['total_cost_tl'] for c in comparison['comparisons']])
            if max_cost > rec['fuel_consumption']['total_cost_tl']:
                savings = max_cost - rec['fuel_consumption']['total_cost_tl']
                savings_percent = (savings / max_cost) * 100
                print(f"\n💰 Tasarruf: {savings:.2f} TL (%{savings_percent:.1f})")
        # GERÇEKÇI SİSTEM UYARISI EKLE
        if comparison.get('unavoidable_critical', False):
            print("\n" + "⚠️ "*20)
            print("⚠️  KRİTİK EĞİM UYARISI")
            print("⚠️ "*20)
            
            warning = comparison.get('warning', {})
            
            print(f"\n❗ {warning.get('message', 'Bu güzergahta kritik eğim var')}")
            print(f"\n💡 Neden?")
            print(f"   {warning.get('reason', 'Yükseklik farkı nedeniyle')}")
            
            # Sürüş ipuçları
            tips = warning.get('driving_tips', [])
            if tips:
                print(f"\n⚠️  SÜRÜŞ İPUÇLARI:")
                for tip in tips:
                    print(f"   • {tip}")
            
            # Alternatif çözümler
            alternatives = warning.get('alternatives', [])
            if alternatives:
                print(f"\n💡 ALTERNATİF ÇÖZÜMLER:")
                print(f"   (Daha güvenli seçenekler)")
                print()
                
                for alt in alternatives:
                    alt_type = alt.get('type', 'unknown')
                    
                    if alt_type == 'taxi':
                        print(f"   🚕 TAKSİ:")
                        print(f"      • Maliyet: {alt.get('cost', 'Bilinmiyor')}")
                        print(f"      • Avantaj: {alt.get('benefit', '')}")
                    
                    elif alt_type == 'walking':
                        print(f"\n   🚶 YÜRÜYÜŞ:")
                        print(f"      • Süre: {alt.get('duration', 'Bilinmiyor')}")
                        print(f"      • Avantaj: {alt.get('benefit', '')}")
                    
                    elif alt_type == 'different_vehicle':
                        print(f"\n   🚗 FARKLI ARAÇ:")
                        suggestions = alt.get('suggestions', [])
                        print(f"      • Öneriler: {', '.join(suggestions)}")
                        print(f"      • Avantaj: {alt.get('benefit', '')}")
                    
                    elif alt_type == 'different_time':
                        print(f"\n   ⏰ FARKLI ZAMAN:")
                        suggestions = alt.get('suggestions', [])
                        for sug in suggestions:
                            print(f"      • {sug}")
                        print(f"      • Avantaj: {alt.get('benefit', '')}")
                    
                    elif alt_type == 'reduce_weight':
                        print(f"\n   👥 YOLCU İNDİRME:")
                        print(f"      • {alt.get('description', '')}")
                        print(f"      • Avantaj: {alt.get('benefit', '')}")
            
            print("\n" + "⚠️ "*20)
            print()
        
        # Mevcut karşılaştırma tablosu devam eder...
        print(f"\n{'Rota':<25} {'Mesafe':<10} {'Yakıt':<10} {'Maliyet':<10} {'Kritik':<10} {'Skor':<10}")
    
    print("\n✅ ANALİZ TAMAMLANDI!")
    print("   📁 Grafikler kaydedildi:")
    print("      - rota_karsilastirma.png")
    
    # Kullanım ipuçları
    print("\n" + "="*80)
    print("💡 KULLANIM İPUÇLARI")
    print("="*80)
    print("• Kritik eğim eşiği: %15 (değiştirilebilir)")
    print("• Alternatif rotalar otomatik olarak Google Maps'ten alınır")
    print("• Önerilen rota: maliyet, kritik bölge ve zorluk dengesine göre seçilir")
    print("• Trafik durumuna göre (yoğun/seyrek) hesaplama değişir")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Program kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n\n❌ Hata oluştu: {str(e)}")
        import traceback
        print(traceback.format_exc())
        print("Lütfen internet bağlantınızı ve API anahtarınızı kontrol edin.")
