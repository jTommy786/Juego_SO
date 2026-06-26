from config import BALANCING_CONFIG
from core.network import NetworkManager
from core.infra import InfraManager
from core.economy import EconomyManager


class GameEngine:
    def __init__(self):
        # Estado principal del juego
        self.is_paused = True
        self.is_game_over = False
        self.days_elapsed = 0
        self.workday_active = False
        self.workday_timer = 20
        self.last_event_msg = "Consola de SysAdmin lista. Fase de Planificación activa."
        
        # Banderas de progresión regional (Europa Día 5, Asia Día 10)
        self.europe_unlocked = False
        self.asia_unlocked = False
        
        # Continentes comprados/activos (América por defecto)
        self.purchased_continents = ["América"]

        # Extraer lista de todas las ciudades (Sub-regiones)
        self.all_cities = []
        for cities in BALANCING_CONFIG["LOCATIONS"].values():
            self.all_cities.extend(cities)

        # Instanciar los tres Managers de dominio (Facade)
        self.network = NetworkManager(self)
        self.infra = InfraManager(self)
        self.economy = EconomyManager(self)

    def is_continent_unlocked(self, continent):
        if continent == "América":
            return True
        elif continent == "Europa":
            return self.europe_unlocked
        elif continent == "Asia":
            return self.asia_unlocked
        return False

    def is_city_unlocked(self, city):
        cont = self.get_city_continent(city)
        return cont in self.purchased_continents

    def get_city_continent(self, city):
        for cont, cities in BALANCING_CONFIG["LOCATIONS"].items():
            if city in cities:
                return cont
        return None

    def generate_forecast(self):
        self.network.generate_forecast()

    def get_forecast_text(self):
        return self.network.get_forecast_text()

    def start_workday(self):
        if self.is_game_over or self.workday_active:
            return False
        self.days_elapsed += 1
        self.workday_active = True
        self.is_paused = False
        self.workday_timer = 20
        
        self.economy.start_workday()
        self.network.start_workday()
        
        # Progresión por días: Desbloquear nuevos continentes
        unlock_msg = ""
        if self.days_elapsed >= 5 and not self.europe_unlocked:
            self.europe_unlocked = True
            unlock_msg = "🌐 NUEVO MERCADO: ¡Europa ahora está disponible para expandir la red!"
        if self.days_elapsed >= 10 and not self.asia_unlocked:
            self.asia_unlocked = True
            unlock_msg = "🌐 NUEVO MERCADO: ¡Asia ahora está disponible para expandir la red!"
            
        if unlock_msg:
            self.last_event_msg = unlock_msg
            
        return True

    def end_workday(self):
        self.workday_active = False
        self.is_paused = True
        self.economy.end_workday()

    def toggle_autoscale(self):
        self.economy.toggle_autoscale()

    def toggle_ia_analyzer(self):
        self.economy.toggle_ia_analyzer()

    def open_datacenter(self, region):
        return self.economy.open_datacenter(region)

    def buy_continent(self, continent):
        return self.economy.buy_continent(continent)

    def buy_server(self, region):
        return self.economy.buy_server(region)

    def buy_upgrade(self, key):
        return self.economy.buy_upgrade(key)

    def get_max_capacity(self):
        return self.network.get_max_capacity()

    def tick(self):
        if self.is_game_over or self.is_paused or not self.workday_active:
            return {"cpu": self.cpu_stress, "ram": self.ram_stress, "latency": self.latency, "credits": self.credits, "workday_done": False}

        self.workday_timer -= 1
        if self.workday_timer <= 0:
            self.end_workday()
            return {"cpu": self.cpu_stress, "ram": self.ram_stress, "latency": self.latency, "credits": self.credits, "workday_done": True}

        self.tick_counter += 1
        
        # Secuencia ordenada de ticks delegada a los gestores independientes
        self.network.process_traffic()
        self.infra.process_load()
        self.network.calculate_pings()
        self.economy.process_tick()

        return {"cpu": self.cpu_stress, "ram": self.ram_stress, "latency": self.latency, "credits": self.credits, "workday_done": False}

    # --- PROPIEDADES DE ECONOMÍA ---
    @property
    def credits(self):
        return self.economy.credits
    
    @credits.setter
    def credits(self, val):
        self.economy.credits = val

    @property
    def ceo_approval(self):
        return self.economy.ceo_approval
    
    @ceo_approval.setter
    def ceo_approval(self, val):
        self.economy.ceo_approval = val

    @property
    def geo_balancer_active(self):
        return self.economy.geo_balancer_active
    
    @geo_balancer_active.setter
    def geo_balancer_active(self, val):
        self.economy.geo_balancer_active = val

    @property
    def auto_scale_purchased(self):
        return self.economy.auto_scale_purchased
    
    @auto_scale_purchased.setter
    def auto_scale_purchased(self, val):
        self.economy.auto_scale_purchased = val

    @property
    def ia_analyzer_purchased(self):
        return self.economy.ia_analyzer_purchased
    
    @ia_analyzer_purchased.setter
    def ia_analyzer_purchased(self, val):
        self.economy.ia_analyzer_purchased = val

    @property
    def party_routing_active(self):
        return self.economy.party_routing_active
    
    @party_routing_active.setter
    def party_routing_active(self, val):
        self.economy.party_routing_active = val

    @property
    def auto_scale_enabled(self):
        return self.economy.auto_scale_enabled
    
    @auto_scale_enabled.setter
    def auto_scale_enabled(self, val):
        self.economy.auto_scale_enabled = val

    @property
    def ia_analyzer_enabled(self):
        return self.economy.ia_analyzer_enabled
    
    @ia_analyzer_enabled.setter
    def ia_analyzer_enabled(self, val):
        self.economy.ia_analyzer_enabled = val

    @property
    def is_autoscale_running(self):
        return self.economy.is_autoscale_running
    
    @is_autoscale_running.setter
    def is_autoscale_running(self, val):
        self.economy.is_autoscale_running = val

    @property
    def daily_revenue(self):
        return self.economy.daily_revenue
    
    @daily_revenue.setter
    def daily_revenue(self, val):
        self.economy.daily_revenue = val

    @property
    def daily_penalty(self):
        return self.economy.daily_penalty
    
    @daily_penalty.setter
    def daily_penalty(self, val):
        self.economy.daily_penalty = val

    @property
    def daily_maintenance(self):
        return self.economy.daily_maintenance
    
    @daily_maintenance.setter
    def daily_maintenance(self, val):
        self.economy.daily_maintenance = val

    @property
    def daily_satisfied_users(self):
        return self.economy.daily_satisfied_users
    
    @daily_satisfied_users.setter
    def daily_satisfied_users(self, val):
        self.economy.daily_satisfied_users = val

    @property
    def daily_base_budget(self):
        return self.economy.daily_base_budget
    
    @daily_base_budget.setter
    def daily_base_budget(self, val):
        self.economy.daily_base_budget = val

    @property
    def daily_satisfied_bonus(self):
        return self.economy.daily_satisfied_bonus
    
    @daily_satisfied_bonus.setter
    def daily_satisfied_bonus(self, val):
        self.economy.daily_satisfied_bonus = val

    # --- PROPIEDADES DE INFRAESTRUCTURA ---
    @property
    def datacenters(self):
        return self.infra.datacenters
    
    @datacenters.setter
    def datacenters(self, val):
        self.infra.datacenters = val

    @property
    def cpu_stress(self):
        return self.infra.cpu_stress
    
    @cpu_stress.setter
    def cpu_stress(self, val):
        self.infra.cpu_stress = val

    @property
    def ram_stress(self):
        return self.infra.ram_stress
    
    @ram_stress.setter
    def ram_stress(self, val):
        self.infra.ram_stress = val

    @property
    def is_downtime(self):
        return self.infra.is_downtime
    
    @is_downtime.setter
    def is_downtime(self, val):
        self.infra.is_downtime = val

    # --- PROPIEDADES DE RED ---
    @property
    def traffic_users(self):
        return self.network.traffic_users
    
    @traffic_users.setter
    def traffic_users(self, val):
        self.network.traffic_users = val

    @property
    def traffic_ddos(self):
        return self.network.traffic_ddos
    
    @traffic_ddos.setter
    def traffic_ddos(self, val):
        self.network.traffic_ddos = val

    @property
    def ddos_timer(self):
        return self.network.ddos_timer
    
    @ddos_timer.setter
    def ddos_timer(self, val):
        self.network.ddos_timer = val

    @property
    def tick_counter(self):
        return self.network.tick_counter
    
    @tick_counter.setter
    def tick_counter(self, val):
        self.network.tick_counter = val

    @property
    def latency(self):
        return self.network.latency
    
    @latency.setter
    def latency(self, val):
        self.network.latency = val

    @property
    def forecast_type(self):
        return self.network.forecast_type
    
    @forecast_type.setter
    def forecast_type(self, val):
        self.network.forecast_type = val

    @property
    def traffic_users_regional(self):
        return self.network.traffic_users_regional
    
    @traffic_users_regional.setter
    def traffic_users_regional(self, val):
        self.network.traffic_users_regional = val

    @property
    def regional_pings(self):
        return self.network.regional_pings
    
    @regional_pings.setter
    def regional_pings(self, val):
        self.network.regional_pings = val

    @property
    def ddos_region(self):
        return self.network.ddos_region
    
    @ddos_region.setter
    def ddos_region(self, val):
        self.network.ddos_region = val

    @property
    def tournament_region(self):
        return self.network.tournament_region
    
    @tournament_region.setter
    def tournament_region(self, val):
        self.network.tournament_region = val


