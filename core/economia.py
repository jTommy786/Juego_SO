from configuracion import CONFIG_BALANCEO

class GestorEconomia:
    def __init__(self, motor):
        self.motor = motor
        
        # Presupuesto y reputación
        self.creditos = CONFIG_BALANCEO.get("STARTING_CREDITS", 12000.0)
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

    def iniciar_jornada(self):
        self.daily_revenue = 0.0
        self.daily_penalty = 0.0
        self.daily_maintenance = 0.0
        self.daily_satisfied_users = 0

    def finalizar_jornada(self):
        # Calcular costos fijos diarios de mantenimiento
        mantenimiento = CONFIG_BALANCEO["DAILY_MAINTENANCE_BASE_SERVER"]
        
        for region, dc in self.motor.centros_datos.items():
            mantenimiento += dc["servers_count"] * CONFIG_BALANCEO["DAILY_MAINTENANCE_PER_PHYSICAL_SERVER"]
            mantenimiento += 150.0  # Costo fijo por cada datacenter abierto
            
        if self.auto_scale_purchased:
            mantenimiento += CONFIG_BALANCEO["DAILY_MAINTENANCE_AUTOSCALE"]
        if self.geo_balancer_active:
            mantenimiento += CONFIG_BALANCEO["DAILY_MAINTENANCE_GEO_BALANCER"]
        if self.ia_analyzer_purchased:
            mantenimiento += CONFIG_BALANCEO["DAILY_MAINTENANCE_IA_ANALYZER"]
        if self.party_routing_active:
            mantenimiento += CONFIG_BALANCEO["DAILY_MAINTENANCE_PARTY_ROUTING"]
        
        self.daily_maintenance = mantenimiento
        self.daily_base_budget = CONFIG_BALANCEO["DAILY_BASE_BUDGET"]
        self.daily_satisfied_bonus = self.daily_satisfied_users * CONFIG_BALANCEO["BONUS_PER_SATISFIED_USER"]
        self.daily_revenue = self.daily_base_budget + self.daily_satisfied_bonus
        
        self.creditos += self.daily_revenue
        self.creditos -= mantenimiento
        
        if self.creditos < CONFIG_BALANCEO["GAME_OVER_CREDITS_LIMIT"] or self.ceo_approval <= 0.0:
            self.motor.fin_del_juego = True
            self.motor.ultimo_mensaje_evento = "🚨 FIN DE LA JORNADA: Has sido despedido por mala gestión corporativa."
        else:
            self.motor.ultimo_mensaje_evento = f"Turno finalizado. Reporte disponible. Configura el Día {self.motor.dias_transcurridos+1}."
            self.motor.red.generate_forecast()

    def alternar_autoescalado(self):
        if self.auto_scale_purchased and not self.motor.fin_del_juego:
            self.auto_scale_enabled = not self.auto_scale_enabled
            self.motor.ultimo_mensaje_evento = f"Auto-Scaling {'ENCENDIDO' if self.auto_scale_enabled else 'APAGADO'}."

    def alternar_analizador_ia(self):
        if self.ia_analyzer_purchased and not self.motor.fin_del_juego:
            self.ia_analyzer_enabled = not self.ia_analyzer_enabled
            self.motor.ultimo_mensaje_evento = f"Filtro de Tráfico IA {'ENCENDIDO' if self.ia_analyzer_enabled else 'APAGADO'}."

    def comprar_continente(self, continente):
        if self.motor.jornada_activa:
            return False
        if continente in self.motor.continentes_comprados:
            self.motor.ultimo_mensaje_evento = f"El Enlace Continental con {continente} ya está activo."
            return False
        if not self.motor.is_continent_unlocked(continente):
            self.motor.ultimo_mensaje_evento = f"🚨 ERROR: El mercado de {continente} está bloqueado por días de supervivencia."
            return False
        costo = CONFIG_BALANCEO["CONTINENT_UNLOCK_COST"]
        if self.creditos >= costo:
            self.creditos -= costo
            self.motor.continentes_comprados.append(continente)
            self.motor.ultimo_mensaje_evento = f"¡Enlace Continental con {continente} activado con éxito!"
            return True
        else:
            self.motor.ultimo_mensaje_evento = f"🚨 Presupuesto insuficiente para Enlace Continental con {continente} (${costo:.0f})."
            return False

    def abrir_centro_datos(self, region):
        if self.motor.jornada_activa:
            return False
        if not self.motor.is_city_unlocked(region):
            self.motor.ultimo_mensaje_evento = f"🚨 ERROR: El mercado de {region} está bloqueado."
            return False
        if region in self.motor.centros_datos:
            self.motor.ultimo_mensaje_evento = f"El Data Center de {region} ya está abierto."
            return False
        costo = CONFIG_BALANCEO["OPEN_DATACENTER_COST"]
        if self.creditos >= costo:
            self.creditos -= costo
            self.motor.centros_datos[region] = {
                "servers_count": 0,
                "estres_cpu": 0.0,
                "estres_ram": 0.0
            }
            self.motor.ultimo_mensaje_evento = f"¡Data Center en {region} abierto con éxito!"
            return True
        else:
            self.motor.ultimo_mensaje_evento = f"🚨 Fondos insuficientes para abrir Data Center en {region} (${costo:.0f})."
            return False

    def comprar_servidor(self, region):
        if self.motor.jornada_activa:
            return False
        if region not in self.motor.centros_datos:
            self.motor.ultimo_mensaje_evento = f"🚨 ERROR: Abre el Data Center de {region} primero."
            return False
        costo = CONFIG_BALANCEO["UPGRADE_SERVER_COST"]
        if self.creditos >= costo:
            self.creditos -= costo
            self.motor.centros_datos[region]["servers_count"] += 1
            self.motor.ultimo_mensaje_evento = f"Servidor instalado con éxito en el Data Center de {region}."
            return True
        else:
            self.motor.ultimo_mensaje_evento = f"🚨 Presupuesto insuficiente para comprar servidor ($600)."
            return False

    def comprar_mejora(self, clave):
        if self.motor.jornada_activa and clave not in ["autoscale", "ia"]:
            return False
        
        if clave == "autoscale" and not self.auto_scale_purchased and self.creditos >= CONFIG_BALANCEO["UPGRADE_AUTOSCALE_COST"]:
            self.creditos -= CONFIG_BALANCEO["UPGRADE_AUTOSCALE_COST"]
            self.auto_scale_purchased = True
            self.motor.ultimo_mensaje_evento = "Auto-Scaling contratado. Panel de control activo."
            return True
        elif clave == "geo" and not self.geo_balancer_active and self.creditos >= CONFIG_BALANCEO["UPGRADE_GEO_BALANCER_COST"]:
            self.creditos -= CONFIG_BALANCEO["UPGRADE_GEO_BALANCER_COST"]
            self.geo_balancer_active = True
            self.motor.ultimo_mensaje_evento = "Router Geo DNS global activado (elimina penalizaciones de overflow)."
            return True
        elif clave == "ia" and not self.ia_analyzer_purchased and self.creditos >= CONFIG_BALANCEO["UPGRADE_IA_ANALYZER_COST"]:
            self.creditos -= CONFIG_BALANCEO["UPGRADE_IA_ANALYZER_COST"]
            self.ia_analyzer_purchased = True
            self.motor.ultimo_mensaje_evento = "Filtro de Tráfico IA contratado."
            return True
        elif clave == "party" and not self.party_routing_active and self.creditos >= CONFIG_BALANCEO["UPGRADE_PARTY_ROUTING_COST"]:
            self.creditos -= CONFIG_BALANCEO["UPGRADE_PARTY_ROUTING_COST"]
            self.party_routing_active = True
            self.motor.ultimo_mensaje_evento = "Ruteo lógico por Tipo de Partida configurado."
            return True
        return False

    def process_tick(self):
        todo_offline = self.motor.red.todo_offline
        estres_cpu = self.motor.estres_cpu
        estres_ram = self.motor.estres_ram
        latencia = self.motor.red.latencia
        
        # Tránsito total
        trafico_total_atendido = (
            sum(self.motor.red.atendido_local.values()) +
            sum(sum(rem.values()) for rem in self.motor.red.atendido_mismo_continente.values()) +
            sum(sum(rem.values()) for rem in self.motor.red.atendido_otro_continente.values())
        )
        
        if estres_cpu >= 100.0 or estres_ram >= 100.0 or todo_offline:
            self.motor.is_downtime = True
            self.creditos -= CONFIG_BALANCEO["DOWNTIME_PENALTY"]
            self.daily_penalty += CONFIG_BALANCEO["DOWNTIME_PENALTY"]
            self.ceo_approval = max(0.0, self.ceo_approval - 5.0)
        else:
            self.motor.is_downtime = False
            if latencia < 100.0:
                self.daily_satisfied_users += trafico_total_atendido
            
            if latencia > 100.0:
                penalizacion = CONFIG_BALANCEO["LATENCY_PENALTY"]
                self.creditos -= penalizacion
                self.daily_penalty += penalizacion
                self.ceo_approval = max(0.0, self.ceo_approval - 2.0)
                self.motor.ultimo_mensaje_evento = "SLA BREACH: Latencia elevada en la red global."
                
            if estres_cpu < 80.0 and latencia <= 50.0:
                self.ceo_approval = min(100.0, self.ceo_approval + 1.0)
                
            if self.auto_scale_purchased and self.auto_scale_enabled:
                self.creditos -= CONFIG_BALANCEO["AUTOSCALE_ACTIVE_TICK_COST"]
            if self.ia_analyzer_purchased and self.ia_analyzer_enabled:
                self.creditos -= CONFIG_BALANCEO["IA_ACTIVE_TICK_COST"]
