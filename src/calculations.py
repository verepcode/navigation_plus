"""
Hesaplama Modülü - Rota Analizi ve Yakıt Tüketimi Hesaplamaları
Bu modül tüm hesaplama algoritmalarını içerir.
"""

import numpy as np
from database import (TRAFFIC_ZONES, FUEL_PRICES, PEAK_HOURS, 
                     find_zone_by_keyword, is_peak_hour, calculate_toll_cost)

class RouteSegmentAnalyzer:
    """Rota segmentlerini analiz eder ve trafik özelliklerini belirler"""
    
    @staticmethod
    def classify_route_segments(coordinates, elevations, distances, route_info=None):
        """
        Rotayı segmentlere ayırır ve her segmentin özelliklerini belirler
        
        Args:
            coordinates (list): Koordinat listesi [(lat, lng), ...]
            elevations (list): Yükseklik listesi
            distances (list): Mesafe listesi (kümülatif)
            route_info (dict): Google Maps'ten gelen rota bilgisi (opsiyonel)
            
        Returns:
            list: Segment listesi
        """
        segments = []
        
        for i in range(len(coordinates) - 1):
            lat1, lng1 = coordinates[i]
            lat2, lng2 = coordinates[i + 1]
            
            segment_distance = distances[i + 1] - distances[i]
            if segment_distance == 0:
                continue
            
            # Eğim hesapla
            elevation_change = elevations[i + 1] - elevations[i]
            gradient = (elevation_change / (segment_distance * 1000)) * 100 if segment_distance > 0 else 0
            
            # Segment tipini belirle
            segment_type, segment_zone = RouteSegmentAnalyzer.determine_segment_type(
                lat1, lng1, lat2, lng2, route_info
            )
            
            segments.append({
                'start_idx': i,
                'end_idx': i + 1,
                'distance_km': segment_distance,
                'gradient': gradient,
                'elevation_change': elevation_change,
                'type': segment_type,
                'traffic_zone': segment_zone,
                'coordinates': [(lat1, lng1), (lat2, lng2)]
            })
        
        return segments
    
    @staticmethod
    def determine_segment_type(lat1, lng1, lat2, lng2, route_info=None):
        """
        Koordinatlara ve rota bilgisine göre segment tipini belirle
        
        Args:
            lat1, lng1, lat2, lng2: Başlangıç ve bitiş koordinatları
            route_info: Google Maps'ten gelen rota bilgisi
            
        Returns:
            tuple: (segment_type, zone_data)
        """
        # İstanbul'un yaklaşık koordinat aralıkları
        # Avrupa Yakası: lng < 29.0
        # Anadolu Yakası: lng > 29.0
        # Kuzey (TEM/3. Köprü): lat > 41.1
        # Güney (Sahil): lat < 40.95
        
        avg_lat = (lat1 + lat2) / 2
        avg_lng = (lng1 + lng2) / 2
        
        # Boğaz geçişleri kontrolü (köprü veya tünel)
        if abs(lng1 - lng2) > 0.05:  # Büyük boylam değişimi = boğaz geçişi
            if avg_lat > 41.15:
                return 'YSS_Kopru', TRAFFIC_ZONES['YSS_Kopru']
            elif avg_lat > 41.08:
                return 'FSM_Kopru', TRAFFIC_ZONES['FSM_Kopru']
            elif avg_lat > 41.03:
                return '15_Temmuz_Kopru', TRAFFIC_ZONES['15_Temmuz_Kopru']
            elif avg_lat < 40.99:
                return 'Avrasya_Tuneli', TRAFFIC_ZONES['Avrasya_Tuneli']
        
        # Kuzey Marmara Otoyolu
        if avg_lat > 41.15:
            if avg_lng < 28.7 or avg_lng > 29.3:
                return 'Kuzey_Marmara_Otoyolu', TRAFFIC_ZONES['Kuzey_Marmara_Otoyolu']
        
        # TEM Otoyolu
        if 41.05 < avg_lat < 41.15:
            return 'O-1_O-2_Otoyol', TRAFFIC_ZONES['O-1_O-2_Otoyol']
        
        # E-5 / D-100
        if 40.97 < avg_lat < 41.02:
            return 'D100_E5', TRAFFIC_ZONES['D100_E5']
        
        # Sahil yolları
        if avg_lat < 40.97:
            if avg_lng < 29.0:
                return 'Sahil_Yolu_Avrupa', TRAFFIC_ZONES['Sahil_Yolu_Avrupa']
            else:
                return 'Sahil_Yolu_Anadolu', TRAFFIC_ZONES['Sahil_Yolu_Anadolu']
        
        # Bölgesel ayrımlar
        # Avrupa Yakası
        if avg_lng < 29.0:
            # Beylikdüzü-Büyükçekmece
            if avg_lng < 28.7:
                return 'Beylikduzu_Buyukcekmece', TRAFFIC_ZONES['Beylikduzu_Buyukcekmece']
            # Şişli-Taksim
            elif 28.96 < avg_lng < 29.0 and 41.03 < avg_lat < 41.07:
                return 'Taksim_Sisli', TRAFFIC_ZONES['Taksim_Sisli']
            # Barbaros Bulvarı
            elif 29.0 < avg_lng < 29.05 and avg_lat > 41.04:
                return 'Barbaros_Bulvari', TRAFFIC_ZONES['Barbaros_Bulvari']
            # Basın Ekspres
            elif 28.8 < avg_lng < 28.9:
                return 'Basin_Ekspres', TRAFFIC_ZONES['Basin_Ekspres']
        
        # Anadolu Yakası
        else:
            # Kadıköy merkez
            if 29.0 < avg_lng < 29.05 and 40.98 < avg_lat < 41.02:
                return 'Kadikoy_Merkez', TRAFFIC_ZONES['Kadikoy_Merkez']
            # Bağdat Caddesi
            elif 29.02 < avg_lng < 29.15 and avg_lat < 40.98:
                return 'Bagdat_Caddesi', TRAFFIC_ZONES['Bagdat_Caddesi']
            # Üsküdar-Ümraniye
            elif 29.0 < avg_lng < 29.1 and 41.0 < avg_lat < 41.05:
                return 'Uskudar_Umraniye', TRAFFIC_ZONES['Uskudar_Umraniye']
            # Tuzla-Gebze
            elif avg_lng > 29.3:
                return 'Tuzla_Gebze', TRAFFIC_ZONES['Tuzla_Gebze']
            # Sancaktepe-Sultanbeyli
            elif avg_lng > 29.15 and avg_lat > 40.95:
                return 'Sancaktepe_Sultanbeyli', TRAFFIC_ZONES['Sancaktepe_Sultanbeyli']
        
        # Varsayılan: TEM Bağlantı
        return 'TEM_Baglanti', TRAFFIC_ZONES['TEM_Baglanti']


class FuelConsumptionCalculator:
    """Yakıt tüketimi hesaplama motoru"""
    
    @staticmethod
    def calculate_fuel_consumption(vehicle_specs, route_data, time_of_day='peak', route_info=None):
        """
        Segment bazlı gerçekçi yakıt tüketimi hesaplama
        
        Args:
            vehicle_specs (dict): Araç özellikleri
            route_data (dict): Rota verileri
            time_of_day (str): 'peak' veya 'offpeak'
            route_info (dict): Google Maps rota bilgisi
            
        Returns:
            dict: Yakıt tüketimi sonuçları
        """
        # Rota segmentlerini al
        segments = RouteSegmentAnalyzer.classify_route_segments(
            route_data['coordinates'],
            route_data['elevations'],
            route_data['distances'],
            route_info
        )
        
        total_fuel = 0
        segment_stats = {}
        zones_used = []
        
        for segment in segments:
            zone = segment['traffic_zone']
            
            # Zone istatistiklerini başlat
            if zone['name'] not in segment_stats:
                segment_stats[zone['name']] = {
                    'distance': 0, 
                    'fuel': 0,
                    'avg_speed': zone['avg_speed_peak'] if time_of_day == 'peak' else zone['avg_speed_offpeak'],
                    'road_type': zone['road_type'],
                    'toll': zone.get('toll', False),
                    'toll_price': zone.get('toll_price', 0)
                }
                if zone.get('toll', False):
                    zones_used.append(segment['type'])
            
            # Temel yakıt tüketimi
            base_consumption = FuelConsumptionCalculator._calculate_base_consumption(
                vehicle_specs, 
                zone,
                time_of_day
            )
            
            # Eğim faktörü
            gradient_factor = FuelConsumptionCalculator._calculate_gradient_factor(
                segment['gradient'],
                vehicle_specs
            )
            
            # Segment yakıt tüketimi
            segment_fuel = segment['distance_km'] * base_consumption * gradient_factor / 100
            total_fuel += segment_fuel
            
            # İstatistikleri güncelle
            segment_stats[zone['name']]['distance'] += segment['distance_km']
            segment_stats[zone['name']]['fuel'] += segment_fuel
        
        # Yakıt maliyeti hesapla
        fuel_price = FUEL_PRICES.get(vehicle_specs['fuel_type'], 42)
        fuel_cost = total_fuel * fuel_price
        
        # Geçiş ücretlerini hesapla
        toll_cost = calculate_toll_cost(zones_used)
        
        # Toplam maliyet
        total_cost = fuel_cost + toll_cost
        
        return {
            'total_fuel_liters': total_fuel,
            'fuel_per_100km': (total_fuel / route_data['total_distance_km']) * 100 if route_data['total_distance_km'] > 0 else 0,
            'fuel_cost_tl': fuel_cost,
            'toll_cost_tl': toll_cost,
            'total_cost_tl': total_cost,
            'fuel_price_per_liter': fuel_price,
            'segment_stats': segment_stats,
            'time_of_day': time_of_day,
            'zones_used': list(set(zones_used))
        }
    
    @staticmethod
    def _calculate_base_consumption(vehicle_specs, zone_info, time_of_day):
        """
        Baz yakıt tüketimini hesapla
        
        Args:
            vehicle_specs (dict): Araç özellikleri
            zone_info (dict): Trafik bölgesi bilgileri
            time_of_day (str): Zaman dilimi
            
        Returns:
            float: L/100km cinsinden baz tüketim
        """
        # Temel tüketim değeri
        city_consumption = vehicle_specs['fuel_consumption_city']
        highway_consumption = vehicle_specs['fuel_consumption_highway']
        
        # Hıza göre tüketimi hesapla
        avg_speed = zone_info['avg_speed_peak'] if time_of_day == 'peak' else zone_info['avg_speed_offpeak']
        
        # Hız bazlı interpolasyon
        if avg_speed <= 20:
            base_consumption = city_consumption * 1.4  # Çok yavaş trafik
        elif avg_speed <= 30:
            base_consumption = city_consumption * 1.2
        elif avg_speed <= 50:
            base_consumption = city_consumption
        elif avg_speed <= 80:
            # Şehir içi ve şehir dışı arasında interpolasyon
            ratio = (avg_speed - 50) / 30
            base_consumption = city_consumption * (1 - ratio) + highway_consumption * ratio
        elif avg_speed <= 100:
            base_consumption = highway_consumption
        else:
            # Yüksek hızda tüketim artar
            base_consumption = highway_consumption * 1.15
        
        # Trafik çarpanını uygula
        base_consumption *= zone_info['traffic_multiplier']
        
        # Dur-kalk etkisi (şehir içi yoğun bölgelerde)
        if zone_info['road_type'] == 'Şehir İçi' and time_of_day == 'peak':
            base_consumption *= 1.2  # %20 ek tüketim
        elif zone_info['road_type'] == 'Cadde' and avg_speed < 30:
            base_consumption *= 1.15  # %15 ek tüketim
        
        return base_consumption
    
    @staticmethod
    def _calculate_gradient_factor(gradient, vehicle_specs):
        """
        Eğim faktörünü hesapla
        
        Args:
            gradient (float): Eğim yüzdesi
            vehicle_specs (dict): Araç özellikleri
            
        Returns:
            float: Eğim çarpanı
        """
        if abs(gradient) < 1:
            return 1.0
        
        # Güç/ağırlık oranını hesapla
        power_to_weight = vehicle_specs['hp'] / vehicle_specs['weight_kg']
        
        # Tırmanış
        if gradient > 0:
            # Her %1 eğim için yaklaşık %2-3 ek tüketim
            base_increase = 0.025
            # Düşük güç/ağırlık oranı için ceza
            if power_to_weight < 0.07:
                base_increase *= 1.3
            elif power_to_weight < 0.09:
                base_increase *= 1.15
            
            factor = 1 + (gradient * base_increase)
            # Maksimum faktörü sınırla
            return min(factor, 2.5)
        
        # İniş
        else:
            # İnişte yakıt tasarrufu (motor freni)
            # Her %1 iniş için %1 tasarruf (maksimum %30)
            savings = min(abs(gradient) * 0.01, 0.3)
            return 1 - savings
    
    @staticmethod
    def assess_vehicle_capability(vehicle_specs, route_data):
        """
        Aracın rota için uygunluğunu değerlendir
        
        Args:
            vehicle_specs (dict): Araç özellikleri
            route_data (dict): Rota verileri
            
        Returns:
            dict: Yetenek değerlendirmesi
        """
        # Güç/ağırlık oranları
        power_to_weight = vehicle_specs['hp'] / vehicle_specs['weight_kg']
        torque_to_weight = vehicle_specs['torque_nm'] / vehicle_specs['weight_kg']
        
        # Maksimum eğimi bul
        max_gradient = 0
        for i in range(1, len(route_data['elevations'])):
            if route_data['distances'][i] != route_data['distances'][i-1]:
                gradient = (route_data['elevations'][i] - route_data['elevations'][i-1]) / \
                          ((route_data['distances'][i] - route_data['distances'][i-1]) * 1000) * 100
                max_gradient = max(max_gradient, abs(gradient))
        
        # Zorluk değerlendirmesi
        difficulty = 'KOLAY'
        warnings = []
        
        # Eğim bazlı değerlendirme
        if max_gradient > 15:
            if power_to_weight < 0.07:
                difficulty = 'ÇOK ZOR'
                warnings.append(f"⚠️ Maksimum %{max_gradient:.1f} eğim için motor gücü yetersiz olabilir")
            elif power_to_weight < 0.09:
                difficulty = 'ZOR'
                warnings.append(f"⚠️ Dik yokuşlarda (%{max_gradient:.1f}) zorlanabilir")
            else:
                difficulty = 'ORTA'
        elif max_gradient > 10:
            if power_to_weight < 0.08:
                difficulty = 'ORTA'
        
        # Tork değerlendirmesi
        if torque_to_weight < 0.15 and max_gradient > 10:
            warnings.append("⚠️ Düşük tork nedeniyle yokuşta çekiş sorunu yaşanabilir")
            if difficulty == 'KOLAY':
                difficulty = 'ORTA'
        
        # Toplam tırmanış değerlendirmesi
        if route_data['total_ascent_m'] > 500:
            if power_to_weight < 0.08:
                warnings.append(f"⚠️ Toplam {route_data['total_ascent_m']:.0f}m tırmanış yorucu olabilir")
                if difficulty in ['KOLAY', 'ORTA']:
                    difficulty = 'ZOR'
        
        return {
            'power_to_weight': power_to_weight,
            'torque_to_weight': torque_to_weight,
            'max_gradient': max_gradient,
            'difficulty': difficulty,
            'warnings': warnings
        }
    
    @staticmethod
    def calculate_emission(fuel_consumption, fuel_type, distance_km):
        """
        CO2 emisyonunu hesapla
        
        Args:
            fuel_consumption (float): Toplam yakıt tüketimi (litre)
            fuel_type (str): Yakıt tipi
            distance_km (float): Mesafe (km)
            
        Returns:
            dict: Emisyon verileri
        """
        # CO2 emisyon faktörleri (kg CO2 / litre)
        emission_factors = {
            'Benzin': 2.31,
            'Dizel': 2.68,
            'LPG': 1.51
        }
        
        factor = emission_factors.get(fuel_type, 2.5)
        total_emission = fuel_consumption * factor
        emission_per_km = (total_emission / distance_km * 1000) if distance_km > 0 else 0
        
        return {
            'total_co2_kg': total_emission,
            'co2_per_km_g': emission_per_km
        }