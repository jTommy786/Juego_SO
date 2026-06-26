import random
from config import BALANCING_CONFIG

class ThermoManager:
    def __init__(self, engine):
        self.engine = engine
        
        # Estado de recursos globales
        self.cpu_stress = 0.0
        self.ram_stress = 0.0
        self.is_downtime = False
        
        # Inicializar Servidor 1 (Base en América - Ciudad Miami)
        self.datacenters = {
            "Miami": {
                "room_max_slots": BALANCING_CONFIG["ROOM_SLOTS_BASE"],
                "room_cooling_lvl": 1,
                "room_temp": 20.0,
                "cpu_stress": 0.0,
                "ram_stress": 0.0,
                "servers": [
                    {
                        "name": "Servidor 1",
                        "region": "Miami",
                        "hw_lvl": 1,
                        "cool_lvl": 1,
                        "temp": 35.0,
                        "offline_timer": 0,
                        "ping": 20.0
                    }
                ]
            }
        }

    def decrement_offline_timers(self):
        for dc in self.datacenters.values():
            for s in dc["servers"]:
                if s["offline_timer"] > 0:
                    s["offline_timer"] -= 1

    def reboot_server(self, region, idx):
        if not self.engine.is_game_over and not self.engine.is_paused and region in self.datacenters:
            dc = self.datacenters[region]
            if dc["servers"][idx]["offline_timer"] == 0:
                dc["servers"][idx]["offline_timer"] = 3
                self.engine.last_event_msg = f"{dc['servers'][idx]['name']} ({region}) reiniciado. Flush de caché por 3s."

    def process_heat(self):
        # 1. Calcular Carga y Estrés por Sala de Servidores
        dc_capacities = {}
        for city, dc in self.datacenters.items():
            cap = sum(
                BALANCING_CONFIG["CAPACITY_BASE"] + ((s["hw_lvl"] - 1) * BALANCING_CONFIG["CAPACITY_PER_SERVER_LVL"])
                for s in dc["servers"] if s["offline_timer"] == 0
            )
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

        # 2. Termodinámica Aislada de Servidores y Salas
        for city, dc in self.datacenters.items():
            dc["room_temp"] = 20.0 + (len(dc["servers"]) * 5.0) - (dc["room_cooling_lvl"] * 3.5)
            dc["room_temp"] = max(16.0, dc["room_temp"])
            
            dc_cpu = dc["cpu_stress"]
            
            for s in dc["servers"]:
                if s["offline_timer"] > 0:
                    s["temp"] = max(dc["room_temp"], s["temp"] - 20.0)
                else:
                    if dc_cpu > 80.0:
                        s["temp"] = min(100.0, s["temp"] + (random.uniform(3.0, 6.0) / s["cool_lvl"]))
                        if s["temp"] >= 100.0:
                            s["offline_timer"] = 10
                            s["temp"] = dc["room_temp"]
                            self.engine.last_event_msg = f"🚨 CRASH: ¡{s['name']} en {city} quemado por calor! Down 10s."
                    else:
                        if s["temp"] > dc["room_temp"]:
                            s["temp"] = max(dc["room_temp"], s["temp"] - random.uniform(1.5, 3.0))
