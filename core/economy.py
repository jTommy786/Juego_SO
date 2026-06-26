from config import BALANCING_CONFIG

class EconomyManager:
    def __init__(self, engine):
        self.engine = engine
        
        # Presupuesto y reputación
        self.credits = BALANCING_CONFIG.get("STARTING_CREDITS", 12000.0)
        self.ceo_approval = 100.0
        
        # Upgrades contratados (CAPEX global)
        self.geo_balancer_active = False
        self.auto_scale_purchased = False
        self.ia_analyzer_purchased = False
        self.party_routing_active = False
        
        # Toggles activos (OPEX)
        self.auto_scale_enabled = False
        self.ia_analyzer_enabled = False
        self.is_autoscale_running = False
        
        # Historial de finanzas diarias
        self.daily_revenue = 0.0
        self.daily_penalty = 0.0
        self.daily_maintenance = 0.0
        self.daily_satisfied_users = 0
        self.daily_base_budget = 0.0
        self.daily_satisfied_bonus = 0.0

    def start_workday(self):
        self.daily_revenue = 0.0
        self.daily_penalty = 0.0
        self.daily_maintenance = 0.0
        self.daily_satisfied_users = 0

    def end_workday(self):
        # Calcular costos fijos diarios de mantenimiento
        maint = BALANCING_CONFIG["DAILY_MAINTENANCE_BASE_SERVER"]
        
        for reg, dc in self.engine.datacenters.items():
            maint += len(dc["servers"]) * BALANCING_CONFIG["DAILY_MAINTENANCE_PER_PHYSICAL_SERVER"]
            maint += (dc["room_cooling_lvl"] - 1) * BALANCING_CONFIG["DAILY_MAINTENANCE_ROOM_COOLING"]
            maint += 150.0  # Costo fijo por cada datacenter abierto
            
        if self.auto_scale_purchased:
            maint += BALANCING_CONFIG["DAILY_MAINTENANCE_AUTOSCALE"]
        if self.geo_balancer_active:
            maint += BALANCING_CONFIG["DAILY_MAINTENANCE_GEO_BALANCER"]
        if self.ia_analyzer_purchased:
            maint += BALANCING_CONFIG["DAILY_MAINTENANCE_IA_ANALYZER"]
        if self.party_routing_active:
            maint += BALANCING_CONFIG["DAILY_MAINTENANCE_PARTY_ROUTING"]
        
        self.daily_maintenance = maint
        self.daily_base_budget = BALANCING_CONFIG["DAILY_BASE_BUDGET"]
        self.daily_satisfied_bonus = self.daily_satisfied_users * BALANCING_CONFIG["BONUS_PER_SATISFIED_USER"]
        self.daily_revenue = self.daily_base_budget + self.daily_satisfied_bonus
        
        self.credits += self.daily_revenue
        self.credits -= maint
        
        if self.credits < BALANCING_CONFIG["GAME_OVER_CREDITS_LIMIT"] or self.ceo_approval <= 0.0:
            self.engine.is_game_over = True
            self.engine.last_event_msg = "🚨 FIN DE LA JORNADA: Has sido despedido por mala gestión corporativa."
        else:
            self.engine.last_event_msg = f"Turno finalizado. Reporte disponible. Configura el Día {self.engine.days_elapsed+1}."
            self.engine.network.generate_forecast()

    def toggle_autoscale(self):
        if self.auto_scale_purchased and not self.engine.is_game_over:
            self.auto_scale_enabled = not self.auto_scale_enabled
            self.engine.last_event_msg = f"Auto-Scaling {'ENCENDIDO' if self.auto_scale_enabled else 'APAGADO'}."

    def toggle_ia_analyzer(self):
        if self.ia_analyzer_purchased and not self.engine.is_game_over:
            self.ia_analyzer_enabled = not self.ia_analyzer_enabled
            self.engine.last_event_msg = f"Filtro de Tráfico IA {'ENCENDIDO' if self.ia_analyzer_enabled else 'APAGADO'}."

    def buy_continent(self, continent):
        if self.engine.workday_active:
            return False
        if continent in self.engine.purchased_continents:
            self.engine.last_event_msg = f"El Enlace Continental con {continent} ya está activo."
            return False
        if not self.engine.is_continent_unlocked(continent):
            self.engine.last_event_msg = f"🚨 ERROR: El mercado de {continent} está bloqueado por días de supervivencia."
            return False
        cost = BALANCING_CONFIG["CONTINENT_UNLOCK_COST"]
        if self.credits >= cost:
            self.credits -= cost
            self.engine.purchased_continents.append(continent)
            self.engine.last_event_msg = f"¡Enlace Continental con {continent} activado con éxito!"
            return True
        else:
            self.engine.last_event_msg = f"🚨 Presupuesto insuficiente para Enlace Continental con {continent} (${cost:.0f})."
            return False

    def open_datacenter(self, region):
        if self.engine.workday_active:
            return False
        if not self.engine.is_city_unlocked(region):
            self.engine.last_event_msg = f"🚨 ERROR: El mercado de {region} está bloqueado."
            return False
        if region in self.engine.datacenters:
            self.engine.last_event_msg = f"El Data Center de {region} ya está abierto."
            return False
        cost = BALANCING_CONFIG["OPEN_DATACENTER_COST"]
        if self.credits >= cost:
            self.credits -= cost
            self.engine.datacenters[region] = {
                "room_max_slots": BALANCING_CONFIG["ROOM_SLOTS_BASE"],
                "room_cooling_lvl": 1,
                "room_temp": 20.0,
                "cpu_stress": 0.0,
                "ram_stress": 0.0,
                "servers": []
            }
            self.engine.last_event_msg = f"¡Data Center en {region} abierto con éxito!"
            return True
        else:
            self.engine.last_event_msg = f"🚨 Fondos insuficientes para abrir Data Center en {region} (${cost:.0f})."
            return False

    def buy_server(self, region):
        if self.engine.workday_active:
            return False
        if region not in self.engine.datacenters:
            self.engine.last_event_msg = f"🚨 ERROR: Abre el Data Center de {region} primero."
            return False
        dc = self.engine.datacenters[region]
        if len(dc["servers"]) >= dc["room_max_slots"]:
            self.engine.last_event_msg = f"🚨 SIN ESPACIO en {region}: Expande los racks primero."
            return False
        cost = BALANCING_CONFIG["UPGRADE_SERVER_COST"]
        if self.credits >= cost:
            self.credits -= cost
            total_srv_count = sum(len(d["servers"]) for d in self.engine.datacenters.values())
            dc["servers"].append({
                "name": f"Servidor {total_srv_count + 1}",
                "region": region,
                "hw_lvl": 1,
                "cool_lvl": 1,
                "temp": 35.0,
                "offline_timer": 0,
                "ping": 0.0
            })
            self.engine.last_event_msg = f"Servidor instalado con éxito en el Data Center de {region}."
            return True
        else:
            self.engine.last_event_msg = f"🚨 Presupuesto insuficiente para comprar servidor ($600)."
            return False

    def upgrade_room_slots(self, region):
        if not self.engine.workday_active and region in self.engine.datacenters and self.credits >= BALANCING_CONFIG["UPGRADE_ROOM_SLOTS_COST"]:
            self.credits -= BALANCING_CONFIG["UPGRADE_ROOM_SLOTS_COST"]
            self.engine.datacenters[region]["room_max_slots"] += 2
            self.engine.last_event_msg = f"DC {region}: Racks ampliados a {self.engine.datacenters[region]['room_max_slots']} slots."
            return True
        return False

    def upgrade_room_cooling(self, region):
        if not self.engine.workday_active and region in self.engine.datacenters and self.credits >= BALANCING_CONFIG["UPGRADE_ROOM_COOLING_COST"]:
            self.credits -= BALANCING_CONFIG["UPGRADE_ROOM_COOLING_COST"]
            self.engine.datacenters[region]["room_cooling_lvl"] += 1
            self.engine.last_event_msg = f"DC {region}: Climatización mejorada a Nivel {self.engine.datacenters[region]['room_cooling_lvl']}."
            return True
        return False

    def upgrade_server_hardware(self, region, idx):
        if not self.engine.workday_active and region in self.engine.datacenters and self.credits >= BALANCING_CONFIG["UPGRADE_SERVER_HW_COST"]:
            dc = self.engine.datacenters[region]
            self.credits -= BALANCING_CONFIG["UPGRADE_SERVER_HW_COST"]
            dc["servers"][idx]["hw_lvl"] += 1
            self.engine.last_event_msg = f"{dc['servers'][idx]['name']} ({region}): Hardware mejorado a Nivel {dc['servers'][idx]['hw_lvl']}."
            return True
        return False

    def upgrade_server_cooling(self, region, idx):
        if not self.engine.workday_active and region in self.engine.datacenters and self.credits >= BALANCING_CONFIG["UPGRADE_SERVER_COOLING_COST"]:
            dc = self.engine.datacenters[region]
            self.credits -= BALANCING_CONFIG["UPGRADE_SERVER_COOLING_COST"]
            dc["servers"][idx]["cool_lvl"] += 1
            self.engine.last_event_msg = f"{dc['servers'][idx]['name']} ({region}): Disipación mejorada a Nivel {dc['servers'][idx]['cool_lvl']}."
            return True
        return False

    def buy_upgrade(self, key):
        if self.engine.workday_active and key not in ["autoscale", "ia"]:
            return False
        
        if key == "autoscale" and not self.auto_scale_purchased and self.credits >= BALANCING_CONFIG["UPGRADE_AUTOSCALE_COST"]:
            self.credits -= BALANCING_CONFIG["UPGRADE_AUTOSCALE_COST"]
            self.auto_scale_purchased = True
            self.engine.last_event_msg = "Auto-Scaling contratado. Panel de control activo."
            return True
        elif key == "geo" and not self.geo_balancer_active and self.credits >= BALANCING_CONFIG["UPGRADE_GEO_BALANCER_COST"]:
            self.credits -= BALANCING_CONFIG["UPGRADE_GEO_BALANCER_COST"]
            self.geo_balancer_active = True
            self.engine.last_event_msg = "Router Geo DNS global activado (elimina penalizaciones de overflow)."
            return True
        elif key == "ia" and not self.ia_analyzer_purchased and self.credits >= BALANCING_CONFIG["UPGRADE_IA_ANALYZER_COST"]:
            self.credits -= BALANCING_CONFIG["UPGRADE_IA_ANALYZER_COST"]
            self.ia_analyzer_purchased = True
            self.engine.last_event_msg = "Filtro de Tráfico IA contratado."
            return True
        elif key == "party" and not self.party_routing_active and self.credits >= BALANCING_CONFIG["UPGRADE_PARTY_ROUTING_COST"]:
            self.credits -= BALANCING_CONFIG["UPGRADE_PARTY_ROUTING_COST"]
            self.party_routing_active = True
            self.engine.last_event_msg = "Ruteo lógico por Tipo de Partida configurado."
            return True
        return False

    def process_tick(self):
        all_offline = self.engine.network.all_offline
        cpu_stress = self.engine.thermo.cpu_stress
        ram_stress = self.engine.thermo.ram_stress
        latency = self.engine.network.latency
        
        # Tránsito total
        total_traffic_handled = (
            sum(self.engine.network.handled_local.values()) +
            sum(sum(rem.values()) for rem in self.engine.network.handled_same_continent.values()) +
            sum(sum(rem.values()) for rem in self.engine.network.handled_other_continent.values())
        )
        
        if cpu_stress >= 100.0 or ram_stress >= 100.0 or all_offline:
            self.engine.thermo.is_downtime = True
            self.credits -= BALANCING_CONFIG["DOWNTIME_PENALTY"]
            self.daily_penalty += BALANCING_CONFIG["DOWNTIME_PENALTY"]
            self.ceo_approval = max(0.0, self.ceo_approval - 5.0)
        else:
            self.engine.thermo.is_downtime = False
            if latency < 100.0:
                self.daily_satisfied_users += total_traffic_handled
            
            if latency > 100.0:
                penalty = BALANCING_CONFIG["LATENCY_PENALTY"]
                self.credits -= penalty
                self.daily_penalty += penalty
                self.ceo_approval = max(0.0, self.ceo_approval - 2.0)
                self.engine.last_event_msg = "SLA BREACH: Latencia elevada en la red global."
                
            if cpu_stress < 80.0 and latency <= 50.0:
                self.ceo_approval = min(100.0, self.ceo_approval + 1.0)
                
            if self.auto_scale_purchased and self.auto_scale_enabled:
                self.credits -= BALANCING_CONFIG["AUTOSCALE_ACTIVE_TICK_COST"]
            if self.ia_analyzer_purchased and self.ia_analyzer_enabled:
                self.credits -= BALANCING_CONFIG["IA_ACTIVE_TICK_COST"]
