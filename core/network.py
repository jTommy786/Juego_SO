import random
from config import BALANCING_CONFIG

class NetworkManager:
    def __init__(self, engine):
        self.engine = engine
        
        # Desglose de Tráfico y Pings por Ciudad (Sub-región)
        self.traffic_users_regional = {city: 0 for city in self.engine.all_cities}
        self.regional_pings = {city: 20.0 for city in self.engine.all_cities}
        self.ddos_region = "Miami"
        self.tournament_region = None
        
        self.traffic_users = 0
        self.traffic_ddos = 0
        self.ddos_timer = 0
        self.tick_counter = 0
        self.latency = BALANCING_CONFIG["BASE_LATENCY_MS"]
        
        # Pronóstico
        self.forecast_type = "NORMAL"
        self.generate_forecast()
        
        # Auxiliares de Ruteo
        self.handled_local = {}
        self.handled_same_continent = {city: {} for city in self.engine.all_cities}
        self.handled_other_continent = {city: {} for city in self.engine.all_cities}
        self.dropped = {}
        self.overflow_same_p = 30.0
        self.overflow_other_p = 150.0
        self.all_offline = True

    def generate_forecast(self):
        types = ["NORMAL", "TORNEO", "HACKERS"]
        self.forecast_type = random.choices(types, weights=[0.50, 0.25, 0.25])[0]

    def get_forecast_text(self):
        if self.forecast_type == "NORMAL":
            return "📈 PRONOSTICO: Tráfico normal y estable."
        elif self.forecast_type == "TORNEO":
            return "🔥 PRONOSTICO: Torneo Competitivo (Tráfico x3)."
        elif self.forecast_type == "HACKERS":
            return "🚨 PRONOSTICO: Alerta de Hackers (DDoS Inminente)."
        return ""

    def start_workday(self):
        unlocked_cities = [c for c in self.engine.all_cities if self.engine.is_city_unlocked(c)]
        self.ddos_region = random.choice(unlocked_cities)
        self.tournament_region = random.choice(unlocked_cities)
        
        if self.forecast_type == "HACKERS":
            day = self.engine.days_elapsed
            if day <= 10:
                self.ddos_timer = random.randint(4, 6)
            elif day >= 20:
                self.ddos_timer = random.randint(10, 15)
            else:
                self.ddos_timer = random.randint(7, 9)
            self.engine.last_event_msg = f"🚨 ¡ATAQUE DDoS MASIVO EN {self.ddos_region.upper()}!"
        else:
            self.ddos_timer = 0
            if self.forecast_type == "TORNEO":
                self.engine.last_event_msg = f"🔥 ¡TORNEO EN REGION {self.tournament_region.upper()}! Tráfico x3."
            else:
                self.engine.last_event_msg = "Jornada laboral iniciada. Analizando tráfico regional por ciudad."

    def end_workday(self):
        self.generate_forecast()

    def get_max_capacity(self):
        cap = 0.0
        for dc in self.engine.datacenters.values():
            for s in dc["servers"]:
                if s["offline_timer"] == 0:
                    cap += BALANCING_CONFIG["CAPACITY_BASE"] + ((s["hw_lvl"] - 1) * BALANCING_CONFIG["CAPACITY_PER_SERVER_LVL"])
        return max(10.0, cap)

    def process_traffic(self):
        # Generar Tráfico por Ciudad
        traffic_base = BALANCING_CONFIG["TRAFFIC_BASE"] * (BALANCING_CONFIG["TRAFFIC_GROWTH"] ** self.tick_counter)
        
        self.traffic_users_regional = {}
        for continent, cities in BALANCING_CONFIG["LOCATIONS"].items():
            if not self.engine.is_continent_unlocked(continent):
                for city in cities:
                    self.traffic_users_regional[city] = 0
                continue
            
            multiplier = 1.0 if continent == "América" else (0.7 if continent == "Europa" else 0.5)
            for city in cities:
                city_share = traffic_base * multiplier * (1.0 / len(cities))
                self.traffic_users_regional[city] = int(city_share * (1.0 + random.uniform(-0.15, 0.15)))
        
        # Multiplicador por Torneo Regional
        if self.forecast_type == "TORNEO" and self.tournament_region in self.traffic_users_regional:
            self.traffic_users_regional[self.tournament_region] = int(self.traffic_users_regional[self.tournament_region] * 3.0)
            
        # Simulación de DDoS focalizado
        ddos_in = 0
        if self.ddos_timer > 0:
            self.ddos_timer -= 1
            ddos_in = int(random.uniform(1500, 3000) * (0.10 if (self.engine.ia_analyzer_purchased and self.engine.ia_analyzer_enabled) else 1.0))
            if self.ddos_region in self.traffic_users_regional:
                self.traffic_users_regional[self.ddos_region] += ddos_in
            self.engine.last_event_msg = f"DDoS mitigado por IA en {self.ddos_region}." if self.engine.ia_analyzer_enabled else f"🚨 ¡ATAQUE DDoS MASIVO EN {self.ddos_region.upper()}!"

        self.traffic_users = sum(self.traffic_users_regional.values()) - (ddos_in if self.engine.ia_analyzer_enabled else 0)
        self.traffic_ddos = ddos_in

        # Ruteo y Capacidad por Sala de Servidores
        dc_capacities = {}
        for city, dc in self.engine.datacenters.items():
            cap = sum(
                BALANCING_CONFIG["CAPACITY_BASE"] + ((s["hw_lvl"] - 1) * BALANCING_CONFIG["CAPACITY_PER_SERVER_LVL"])
                for s in dc["servers"] if s["offline_timer"] == 0
            )
            dc_capacities[city] = cap

        # Ruteo local inicial
        handled_local = {}
        dc_avail_cap = {city: cap for city, cap in dc_capacities.items()}
        
        for city in self.engine.all_cities:
            reqs = self.traffic_users_regional.get(city, 0)
            if city in self.engine.datacenters:
                local_cap = dc_avail_cap[city]
                routed = min(reqs, local_cap)
                handled_local[city] = routed
                dc_avail_cap[city] -= routed
            else:
                handled_local[city] = 0.0

        # Ruteo de desbordamiento (Overflow en dos niveles)
        handled_same_continent = {city: {} for city in self.engine.all_cities}
        handled_other_continent = {city: {} for city in self.engine.all_cities}
        dropped = {city: 0.0 for city in self.engine.all_cities}

        self.overflow_same_p = 0.0 if self.engine.geo_balancer_active else 30.0
        self.overflow_other_p = 0.0 if self.engine.geo_balancer_active else 150.0

        for src_city in self.engine.all_cities:
            reqs = self.traffic_users_regional.get(src_city, 0) - handled_local.get(src_city, 0)
            if reqs <= 0:
                continue
            
            src_continent = self.engine.get_city_continent(src_city)
            
            # Nivel 1: Mismo continente
            same_continent_open_dcs = [
                c for c in self.engine.datacenters 
                if c in BALANCING_CONFIG["LOCATIONS"][src_continent] and c != src_city
            ]
            for target in same_continent_open_dcs:
                if reqs <= 0:
                    break
                if dc_avail_cap[target] > 0:
                    routed = min(reqs, dc_avail_cap[target])
                    handled_same_continent[src_city][target] = routed
                    dc_avail_cap[target] -= routed
                    reqs -= routed
            
            # Nivel 2: Otros continentes
            if reqs > 0:
                other_continent_open_dcs = [
                    c for c in self.engine.datacenters 
                    if c not in BALANCING_CONFIG["LOCATIONS"][src_continent]
                ]
                for target in other_continent_open_dcs:
                    if reqs <= 0:
                        break
                    if dc_avail_cap[target] > 0:
                        routed = min(reqs, dc_avail_cap[target])
                        handled_other_continent[src_city][target] = routed
                        dc_avail_cap[target] -= routed
                        reqs -= routed
            
            dropped[src_city] = reqs

        self.handled_local = handled_local
        self.handled_same_continent = handled_same_continent
        self.handled_other_continent = handled_other_continent
        self.dropped = dropped

    def calculate_pings(self):
        pings_sum = 0.0
        active_count = 0
        all_offline = True
        
        for city, dc in self.engine.datacenters.items():
            dc_cpu = dc["cpu_stress"]
            
            dc_traffic = (
                self.handled_local.get(city, 0) +
                sum(self.handled_same_continent[src].get(city, 0) for src in self.engine.all_cities) +
                sum(self.handled_other_continent[src].get(city, 0) for src in self.engine.all_cities)
            )
            
            if dc_traffic > 0:
                congestion = (dc_cpu - 80.0) * 4.0 if dc_cpu > 80.0 else 0.0
                ping_sum_dc = self.handled_local.get(city, 0) * (20.0 + congestion)
                
                for src in self.engine.all_cities:
                    t_same = self.handled_same_continent[src].get(city, 0)
                    if t_same > 0:
                        ping_sum_dc += t_same * (20.0 + self.overflow_same_p + congestion)
                
                for src in self.engine.all_cities:
                    t_other = self.handled_other_continent[src].get(city, 0)
                    if t_other > 0:
                        ping_sum_dc += t_other * (20.0 + self.overflow_other_p + congestion)
                        
                dc_ping = ping_sum_dc / dc_traffic
            else:
                dc_ping = 20.0
                
            for s in dc["servers"]:
                s["ping"] = dc_ping + random.uniform(-1.0, 1.0) if s["offline_timer"] == 0 else 0.0
                
                if s["offline_timer"] == 0:
                    all_offline = False
                    pings_sum += s["ping"]
                    active_count += 1

        for city in self.engine.all_cities:
            city_t = self.traffic_users_regional.get(city, 0)
            if city_t > 0:
                weighted_ping_sum = 0.0
                
                local_t = self.handled_local.get(city, 0)
                if local_t > 0:
                    dc_cpu = self.engine.datacenters[city]["cpu_stress"]
                    cong = (dc_cpu - 80.0) * 4.0 if dc_cpu > 80.0 else 0.0
                    weighted_ping_sum += local_t * (20.0 + cong)
                
                for target, t_same in self.handled_same_continent[city].items():
                    if t_same > 0:
                        dc_cpu = self.engine.datacenters[target]["cpu_stress"]
                        cong = (dc_cpu - 80.0) * 4.0 if dc_cpu > 80.0 else 0.0
                        weighted_ping_sum += t_same * (20.0 + self.overflow_same_p + cong)
                
                for target, t_other in self.handled_other_continent[city].items():
                    if t_other > 0:
                        dc_cpu = self.engine.datacenters[target]["cpu_stress"]
                        cong = (dc_cpu - 80.0) * 4.0 if dc_cpu > 80.0 else 0.0
                        weighted_ping_sum += t_other * (20.0 + self.overflow_other_p + cong)
                
                drop_t = self.dropped.get(city, 0)
                if drop_t > 0:
                    weighted_ping_sum += drop_t * 300.0
                    
                city_ping = weighted_ping_sum / city_t
            else:
                city_ping = 20.0
            self.regional_pings[city] = min(300.0, city_ping)

        if active_count > 0:
            self.latency = pings_sum / active_count
        else:
            self.latency = 300.0
        self.latency = min(300.0, self.latency)
        
        self.all_offline = all_offline
