import random
from configuracion import CONFIG_BALANCEO

class GestorRed:
    def __init__(self, motor):
        self.motor = motor
        
        # Desglose de Tráfico y Pings por Ciudad (Sub-región)
        self.usuarios_trafico_regional = {ciudad: 0 for ciudad in self.motor.todas_las_ciudades}
        self.pings_regionales = {ciudad: 20.0 for ciudad in self.motor.todas_las_ciudades}
        self.region_ddos = "Miami"
        self.region_torneo = None
        
        self.usuarios_trafico = 0
        self.trafico_ddos = 0
        self.temporizador_ddos = 0
        self.contador_ticks = 0
        self.latencia = CONFIG_BALANCEO["BASE_LATENCY_MS"]
        
        # Pronóstico
        self.tipo_pronostico = "NORMAL"
        self.generate_forecast()
        
        # Auxiliares de Ruteo
        self.atendido_local = {}
        self.atendido_mismo_continente = {ciudad: {} for ciudad in self.motor.todas_las_ciudades}
        self.atendido_otro_continente = {ciudad: {} for ciudad in self.motor.todas_las_ciudades}
        self.dropped = {}
        self.penalizacion_mismo_continente = 30.0
        self.penalizacion_otro_continente = 150.0
        self.todo_offline = True

    def generate_forecast(self):
        tipos = ["NORMAL", "TORNEO", "HACKERS"]
        self.tipo_pronostico = random.choices(tipos, weights=[0.50, 0.25, 0.25])[0]

    def obtener_texto_pronostico(self):
        if self.tipo_pronostico == "NORMAL":
            return "📈 PRONOSTICO: Tráfico normal y estable."
        elif self.tipo_pronostico == "TORNEO":
            return "🔥 PRONOSTICO: Torneo Competitivo (Tráfico x3)."
        elif self.tipo_pronostico == "HACKERS":
            return "🚨 PRONOSTICO: Alerta de Hackers (DDoS Inminente)."
        return ""

    def iniciar_jornada(self):
        ciudades_abiertas = list(self.motor.centros_datos.keys())
        if not ciudades_abiertas:
            ciudades_abiertas = ["Miami"]
        self.region_ddos = random.choice(ciudades_abiertas)
        self.region_torneo = random.choice(ciudades_abiertas)
        
        if self.tipo_pronostico == "HACKERS":
            dia = self.motor.dias_transcurridos
            if dia <= 10:
                self.temporizador_ddos = random.randint(4, 6)
            elif dia >= 20:
                self.temporizador_ddos = random.randint(10, 15)
            else:
                self.temporizador_ddos = random.randint(7, 9)
            self.motor.ultimo_mensaje_evento = f"🚨 ¡ATAQUE DDoS MASIVO EN {self.region_ddos.upper()}!"
        else:
            self.temporizador_ddos = 0
            if self.tipo_pronostico == "TORNEO":
                self.motor.ultimo_mensaje_evento = f"🔥 ¡TORNEO EN REGION {self.region_torneo.upper()}! Tráfico x3."
            else:
                self.motor.ultimo_mensaje_evento = "Jornada laboral iniciada. Analizando tráfico regional por ciudad."

    def finalizar_jornada(self):
        self.generate_forecast()

    def obtener_capacidad_maxima(self):
        capacidad = 0.0
        for dc in self.motor.centros_datos.values():
            capacidad += dc["servers_count"] * CONFIG_BALANCEO["CAPACITY_BASE"]
        return max(10.0, capacidad)

    def procesar_trafico(self):
        # Generar Tráfico por Ciudad
        trafico_base = CONFIG_BALANCEO["TRAFFIC_BASE"] * (CONFIG_BALANCEO["TRAFFIC_GROWTH"] ** self.contador_ticks)
        
        self.usuarios_trafico_regional = {}
        for continente, cities in CONFIG_BALANCEO["LOCATIONS"].items():
            if not self.motor.is_continent_unlocked(continente):
                for ciudad in cities:
                    self.usuarios_trafico_regional[ciudad] = 0
                continue
            
            multiplicador = 1.0 if continente == "América" else (0.7 if continente == "Europa" else 0.5)
            for ciudad in cities:
                parte_ciudad = trafico_base * multiplicador * (1.0 / len(cities))
                self.usuarios_trafico_regional[ciudad] = int(parte_ciudad * (1.0 + random.uniform(-0.15, 0.15)))
        
        # Multiplicador por Torneo Regional
        if self.tipo_pronostico == "TORNEO" and self.region_torneo in self.usuarios_trafico_regional:
            self.usuarios_trafico_regional[self.region_torneo] = int(self.usuarios_trafico_regional[self.region_torneo] * 3.0)
            
        # Simulación de DDoS focalizado
        ddos_in = 0
        if self.temporizador_ddos > 0:
            self.temporizador_ddos -= 1
            ddos_in = int(random.uniform(1500, 3000) * (0.10 if (self.motor.ia_analyzer_purchased and self.motor.ia_analyzer_enabled) else 1.0))
            if self.region_ddos in self.usuarios_trafico_regional:
                self.usuarios_trafico_regional[self.region_ddos] += ddos_in
            self.motor.ultimo_mensaje_evento = f"DDoS mitigado por IA en {self.region_ddos}." if self.motor.ia_analyzer_enabled else f"🚨 ¡ATAQUE DDoS MASIVO EN {self.region_ddos.upper()}!"

        self.usuarios_trafico = sum(self.usuarios_trafico_regional.values()) - (ddos_in if self.motor.ia_analyzer_enabled else 0)
        self.trafico_ddos = ddos_in

        # Ruteo y Capacidad por Sala de Servidores
        capacidades_dc = {}
        for ciudad, dc in self.motor.centros_datos.items():
            capacidad = dc["servers_count"] * CONFIG_BALANCEO["CAPACITY_BASE"]
            capacidades_dc[ciudad] = capacidad

        # Ruteo local inicial
        atendido_local = {}
        capacidad_disponible_dc = {ciudad: capacidad for ciudad, capacidad in capacidades_dc.items()}
        
        for ciudad in self.motor.todas_las_ciudades:
            peticiones = self.usuarios_trafico_regional.get(ciudad, 0)
            if ciudad in self.motor.centros_datos:
                local_cap = capacidad_disponible_dc[ciudad]
                routed = min(peticiones, local_cap)
                atendido_local[ciudad] = routed
                capacidad_disponible_dc[ciudad] -= routed
            else:
                atendido_local[ciudad] = 0.0

        # Ruteo de desbordamiento (Overflow en dos niveles)
        atendido_mismo_continente = {ciudad: {} for ciudad in self.motor.todas_las_ciudades}
        atendido_otro_continente = {ciudad: {} for ciudad in self.motor.todas_las_ciudades}
        dropped = {ciudad: 0.0 for ciudad in self.motor.todas_las_ciudades}

        self.penalizacion_mismo_continente = 0.0 if self.motor.geo_balancer_active else 30.0
        self.penalizacion_otro_continente = 0.0 if self.motor.geo_balancer_active else 150.0

        for ciudad_origen in self.motor.todas_las_ciudades:
            peticiones = self.usuarios_trafico_regional.get(ciudad_origen, 0) - atendido_local.get(ciudad_origen, 0)
            if peticiones <= 0:
                continue
            
            continente_origen = self.motor.get_city_continent(ciudad_origen)
            
            # Nivel 1: Mismo continente
            dcs_mismo_continente_abiertos = [
                c for c in self.motor.centros_datos 
                if c in CONFIG_BALANCEO["LOCATIONS"][continente_origen] and c != ciudad_origen
            ]
            for destino in dcs_mismo_continente_abiertos:
                if peticiones <= 0:
                    break
                if capacidad_disponible_dc[destino] > 0:
                    routed = min(peticiones, capacidad_disponible_dc[destino])
                    atendido_mismo_continente[ciudad_origen][destino] = routed
                    capacidad_disponible_dc[destino] -= routed
                    peticiones -= routed
            
            # Nivel 2: Otros continentes
            if peticiones > 0:
                dcs_otro_continente_abiertos = [
                    c for c in self.motor.centros_datos 
                    if c not in CONFIG_BALANCEO["LOCATIONS"][continente_origen]
                ]
                for destino in dcs_otro_continente_abiertos:
                    if peticiones <= 0:
                        break
                    if capacidad_disponible_dc[destino] > 0:
                        routed = min(peticiones, capacidad_disponible_dc[destino])
                        atendido_otro_continente[ciudad_origen][destino] = routed
                        capacidad_disponible_dc[destino] -= routed
                        peticiones -= routed
            
            dropped[ciudad_origen] = peticiones

        self.atendido_local = atendido_local
        self.atendido_mismo_continente = atendido_mismo_continente
        self.atendido_otro_continente = atendido_otro_continente
        self.dropped = dropped

    def calcular_pings(self):
        suma_pings = 0.0
        contador_activo = 0
        todo_offline = True
        
        for ciudad, dc in self.motor.centros_datos.items():
            cpu_dc = dc["estres_cpu"]
            
            trafico_dc = (
                self.atendido_local.get(ciudad, 0) +
                sum(self.atendido_mismo_continente[src].get(ciudad, 0) for src in self.motor.todas_las_ciudades) +
                sum(self.atendido_otro_continente[src].get(ciudad, 0) for src in self.motor.todas_las_ciudades)
            )
            
            if trafico_dc > 0:
                congestion = (cpu_dc - 80.0) * 4.0 if cpu_dc > 80.0 else 0.0
                suma_ping_dc = self.atendido_local.get(ciudad, 0) * (20.0 + congestion)
                
                for src in self.motor.todas_las_ciudades:
                    trafico_mismo = self.atendido_mismo_continente[src].get(ciudad, 0)
                    if trafico_mismo > 0:
                        suma_ping_dc += trafico_mismo * (20.0 + self.penalizacion_mismo_continente + congestion)
                
                for src in self.motor.todas_las_ciudades:
                    trafico_otro = self.atendido_otro_continente[src].get(ciudad, 0)
                    if trafico_otro > 0:
                        suma_ping_dc += trafico_otro * (20.0 + self.penalizacion_otro_continente + congestion)
                        
                dc_ping = suma_ping_dc / trafico_dc
            else:
                dc_ping = 20.0
                
            servers_count = dc.get("servers_count", 0)
            if servers_count > 0:
                todo_offline = False
                suma_pings += dc_ping * servers_count
                contador_activo += servers_count

        for ciudad in self.motor.todas_las_ciudades:
            city_t = self.usuarios_trafico_regional.get(ciudad, 0)
            if city_t > 0:
                weighted_ping_sum = 0.0
                
                local_t = self.atendido_local.get(ciudad, 0)
                if local_t > 0:
                    cpu_dc = self.motor.centros_datos[ciudad]["estres_cpu"]
                    cong = (cpu_dc - 80.0) * 4.0 if cpu_dc > 80.0 else 0.0
                    weighted_ping_sum += local_t * (20.0 + cong)
                
                for destino, trafico_mismo in self.atendido_mismo_continente[ciudad].items():
                    if trafico_mismo > 0:
                        cpu_dc = self.motor.centros_datos[destino]["estres_cpu"]
                        cong = (cpu_dc - 80.0) * 4.0 if cpu_dc > 80.0 else 0.0
                        weighted_ping_sum += trafico_mismo * (20.0 + self.penalizacion_mismo_continente + cong)
                
                for destino, trafico_otro in self.atendido_otro_continente[ciudad].items():
                    if trafico_otro > 0:
                        cpu_dc = self.motor.centros_datos[destino]["estres_cpu"]
                        cong = (cpu_dc - 80.0) * 4.0 if cpu_dc > 80.0 else 0.0
                        weighted_ping_sum += trafico_otro * (20.0 + self.penalizacion_otro_continente + cong)
                
                trafico_caido = self.dropped.get(ciudad, 0)
                if trafico_caido > 0:
                    weighted_ping_sum += trafico_caido * 300.0
                    
                ping_ciudad = weighted_ping_sum / city_t
            else:
                ping_ciudad = 20.0
            self.pings_regionales[ciudad] = min(300.0, ping_ciudad)

        self.todo_offline = todo_offline

        if contador_activo > 0:
            self.latencia = suma_pings / contador_activo
        else:
            self.latencia = 300.0
        self.latencia = min(300.0, self.latencia)
