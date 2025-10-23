"""
Hesaplama Modülü - Rota Analizi ve Yakıt Tüketimi Hesaplamaları
Bu modül tüm hesaplama algoritmalarını içerir.
"""

import numpy as np
from database import TRAFFIC_ZONES, FUEL_PRICES

class RouteSegmentAnalyzer:
    """Rota segmentlerini analiz eder ve trafik özelliklerini belirler"""
    
    @staticmethod
    def classify_route_segments(coordinates, elevations, distances):
        """
        Rotayı segmentlere ayırır ve her segmentin özelliklerini belirler
        
        Args:
            coordinates (list): Koordinat listesi [(lat, lng), ...]
            elevations (list): Yükseklik listesi
            distances (list): Mesafe listesi (kümülatif)
            
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
            
            # Segment tipini belirle (basit konum bazlı)
            segment_type = RouteSegmentAnalyzer.determine_segment_type(lat1, lng1, lat2, lng2)
            
            segments.append({
                'start_idx': i,
                'end_idx': i + 1,
                'distance_km': segment_distance,
                'gradient': gradient,
                'elevation_change': elevation_change,
                'type': segment_type,
                'traffic_zone': segment_type
            })
        
        return segments
    
    @staticmethod
    def determine_segment_type(lat1, lng1, lat2, lng2):
        """
        Koordinatlara göre segment tipini belirle
        
        Args:
            lat1, lng1, lat2, lng2: Başlangıç ve bitiş koordinatları
            
        Returns:
            str: Segment tipi
        """
        # Maltepe-Kartal arasında (E5 bölgesi)
        if 40.92 < lat1 < 40.94 and 29.14 < lng1 < 29.18:
            return 'Anadolu'
        # Aydos Ormanı civarı
        elif lat1 > 40.95 or lng1 > 29.19:
            return 'Suburban'
        # E5 yakını
        elif 40.93 < lat1 < 40.95:
            return 'E5'
        else:
            return 'Suburban'


class FuelConsumptionCalculator:
    """Yakıt tüketimi hesaplama motoru"""
    
    @staticmethod
    def calculate_fuel_consumption(vehicle_specs, route_data, time_of_day='peak'):
        """
        Segment bazlı gerçekçi yakıt tüketimi hesaplama
        
        Args:
            vehicle_specs (dict): Araç özellikleri
            route_data (dict): Rota verileri
            time_of_day (str): 'peak' veya 'offpeak'
            
        Returns:
            dict: Yakıt tüketimi sonuçları
        """
        # Rota segmentlerini al
        segments = RouteSegmentAnalyzer.classify_route_segments(
            route_data['coordinates'],
            route_data['elevations'],
            route_data['distances']
        )
        
        total_fuel = 0
        segment_stats = {zone: {'distance': 0, 'fuel': 0} for zone in TRAFFIC_ZONES}
        
        for segment in segments:
            # Temel yakıt tüketimi
            base_consumption = FuelConsumptionCalculator._calculate_base_consumption(
                vehicle_specs, 
                segment['traffic_zone'],
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
            zone = segment['traffic_zone']
            segment_stats[zone]['distance'] += segment['distance_km']
            segment_stats[zone]['fuel'] += segment_fuel
        
        # Yakıt maliyeti hesapla
        fuel_price = FUEL_PRICES.get(vehicle_specs['fuel_type'], 40)
        fuel_cost = total_fuel * fuel_price
        
        return {
            'total_fuel_liters': total_fuel,
            'fuel_per_100km': (total_fuel / route_data['total_distance_km']) * 100 if route_data['total_distance_km'] > 0 else 0,
            'fuel_cost_tl': fuel_cost,
            'fuel_price_per_liter': fuel_price,
            'segment_stats': segment_stats,
            'time_of_day': time_of_day
        }
    
    @staticmethod
    def _calculate_base_consumption(vehicle_specs, traffic_zone, time_of_day):
        """
        Baz yakıt tüketimini hesapla
        
        Args:
            vehicle_specs (dict): Araç özellikleri
            traffic_zone (str): Trafik bölgesi
            time_of_day (str): Zaman dilimi
            
        Returns:
            float: L/100km cinsinden baz tüketim
        """
        # Temel tüketim değeri
        city_consumption = vehicle_specs['fuel_consumption_city']
        highway_consumption = vehicle_specs['fuel_consumption_highway']
        
        # Trafik bölgesi verilerini al
        zone_info = TRAFFIC_ZONES.get(traffic_zone, TRAFFIC_ZONES['Suburban'])
        
        # Hıza göre tüketimi hesapla
        avg_speed = zone_info['avg_speed_peak'] if time_of_day == 'peak' else zone_info['avg_speed_offpeak']
        
        # Hız bazlı interpolasyon
        if avg_speed <= 30:
            base_consumption = city_consumption * 1.3  # Çok yavaş trafik
        elif avg_speed <= 50:
            base_consumption = city_consumption
        elif avg_speed <= 80:
            # Şehir içi ve şehir dışı arasında interpolasyon
            ratio = (avg_speed - 50) / 30
            base_consumption = city_consumption * (1 - ratio) + highway_consumption * ratio
        else:
            base_consumption = highway_consumption
        
        # Trafik çarpanını uygula
        base_consumption *= zone_info['traffic_multiplier']
        
        # Dur-kalk etkisi (yoğun saatlerde)
        if time_of_day == 'peak' and avg_speed < 40:
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
            'Dizel': 2.68
        }
        
        factor = emission_factors.get(fuel_type, 2.5)
        total_emission = fuel_consumption * factor
        emission_per_km = (total_emission / distance_km * 1000) if distance_km > 0 else 0
        
        return {
            'total_co2_kg': total_emission,
            'co2_per_km_g': emission_per_km
        }
