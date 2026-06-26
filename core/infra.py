from config import BALANCING_CONFIG

class InfraManager:
    def __init__(self, engine):
        self.engine = engine
        self.cpu_stress = 0.0
        self.ram_stress = 0.0
        self.is_downtime = False
        
        # Inicializar Data Centers (Miami con 1 servidor al inicio)
        self.datacenters = {
            "Miami": {
                "servers_count": 1,
                "cpu_stress": 0.0,
                "ram_stress": 0.0
            }
        }

    def process_load(self):
        # Calcular Carga y Estrés por Sala de Servidores
        dc_capacities = {}
        for city, dc in self.datacenters.items():
            cap = dc["servers_count"] * BALANCING_CONFIG["CAPACITY_BASE"]
            dc_capacities[city] = cap

        for city, dc in self.datacenters.items():
            dc_capacity = dc_capacities[city]
            dc_capacity_eff = max(10.0, dc_capacity)
            
            # Tránsito total de esta sala (local + overflow enrutado aquí)
            dc_traffic = (
                self.engine.network.handled_local.get(city, 0) +
                sum(self.engine.network.handled_same_continent[src].get(city, 0) for src in self.engine.all_cities) +
                sum(self.engine.network.handled_other_continent[src].get(city, 0) for src in self.engine.all_cities)
            )
            
            dc_cpu = (dc_traffic / dc_capacity_eff) * 100.0
            if self.engine.party_routing_active:
                dc_cpu *= 0.75
            dc["cpu_stress"] = min(100.0, dc_cpu)
            
            dc_ram = (dc_traffic / (dc_capacity_eff * 1.15)) * 100.0
            if dc["cpu_stress"] > 85.0:
                dc_ram += 5.0
            dc["ram_stress"] = min(100.0, dc_ram)

        # Carga Global (Promedio de salas abiertas)
        total_traffic_handled = (
            sum(self.engine.network.handled_local.values()) +
            sum(sum(rem.values()) for rem in self.engine.network.handled_same_continent.values()) +
            sum(sum(rem.values()) for rem in self.engine.network.handled_other_continent.values())
        )
        total_capacity_global = sum(dc_capacities.values())
        total_capacity_eff = max(10.0, total_capacity_global)
        
        global_cpu = (total_traffic_handled / total_capacity_eff) * 100.0
        if self.engine.party_routing_active:
            global_cpu *= 0.75
        self.cpu_stress = min(100.0, global_cpu)
        
        global_ram = (total_traffic_handled / (total_capacity_eff * 1.15)) * 100.0
        if self.cpu_stress > 85.0:
            global_ram += 5.0
        self.ram_stress = min(100.0, global_ram)

        # Determinar downtime
        if self.cpu_stress >= 100.0 or self.ram_stress >= 100.0:
            self.is_downtime = True
        else:
            self.is_downtime = False
