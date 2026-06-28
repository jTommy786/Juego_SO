from configuracion import CONFIG_BALANCEO
from core.red import GestorRed
from core.infraestructura import GestorInfraestructura
from core.economia import GestorEconomia


class MotorJuego:
    def __init__(self):
        # Estado principal del juego
        self.pausado = True
        self.fin_del_juego = False
        self.dias_transcurridos = 0
        self.jornada_activa = False
        self.temporizador_jornada = 20
        self.ultimo_mensaje_evento = "Consola de SysAdmin lista. Fase de Planificación activa."
        
        # Banderas de progresión regional (Europa Día 5, Asia Día 10)
        self.europe_unlocked = False
        self.asia_unlocked = False
        
        # Continentes comprados/activos (América por defecto)
        self.continentes_comprados = ["América"]

        # Extraer lista de todas las ciudades (Sub-regiones)
        self.todas_las_ciudades = []
        for cities in CONFIG_BALANCEO["LOCATIONS"].values():
            self.todas_las_ciudades.extend(cities)

        # Instanciar los tres Managers de dominio (Facade)
        self.red = GestorRed(self)
        self.infraestructura = GestorInfraestructura(self)
        self.economia = GestorEconomia(self)

    def is_continent_unlocked(self, continente):
        if continente == "América":
            return True
        elif continente == "Europa":
            return self.europe_unlocked
        elif continente == "Asia":
            return self.asia_unlocked
        return False

    def is_city_unlocked(self, ciudad):
        cont = self.get_city_continent(ciudad)
        return cont in self.continentes_comprados

    def get_city_continent(self, ciudad):
        for cont, cities in CONFIG_BALANCEO["LOCATIONS"].items():
            if ciudad in cities:
                return cont
        return None

    def generate_forecast(self):
        self.red.generate_forecast()

    def obtener_texto_pronostico(self):
        return self.red.obtener_texto_pronostico()

    def iniciar_jornada(self):
        if self.fin_del_juego or self.jornada_activa:
            return False
        self.dias_transcurridos += 1
        self.jornada_activa = True
        self.pausado = False
        self.temporizador_jornada = 20
        
        self.economia.iniciar_jornada()
        self.red.iniciar_jornada()
        
        # Progresión por días: Desbloquear nuevos continentes
        unlock_msg = ""
        if self.dias_transcurridos >= 5 and not self.europe_unlocked:
            self.europe_unlocked = True
            unlock_msg = "🌐 NUEVO MERCADO: ¡Europa ahora está disponible para expandir la red!"
        if self.dias_transcurridos >= 10 and not self.asia_unlocked:
            self.asia_unlocked = True
            unlock_msg = "🌐 NUEVO MERCADO: ¡Asia ahora está disponible para expandir la red!"
            
        if unlock_msg:
            self.ultimo_mensaje_evento = unlock_msg
            
        return True

    def finalizar_jornada(self):
        self.jornada_activa = False
        self.pausado = True
        self.economia.finalizar_jornada()

    def alternar_autoescalado(self):
        self.economia.alternar_autoescalado()

    def alternar_analizador_ia(self):
        self.economia.alternar_analizador_ia()

    def abrir_centro_datos(self, region):
        return self.economia.abrir_centro_datos(region)

    def comprar_continente(self, continente):
        return self.economia.comprar_continente(continente)

    def comprar_servidor(self, region):
        return self.economia.comprar_servidor(region)

    def comprar_mejora(self, clave):
        return self.economia.comprar_mejora(clave)

    def obtener_capacidad_maxima(self):
        return self.red.obtener_capacidad_maxima()

    def tick(self):
        if self.fin_del_juego or self.pausado or not self.jornada_activa:
            return {"cpu": self.estres_cpu, "ram": self.estres_ram, "latencia": self.latencia, "creditos": self.creditos, "workday_done": False}

        self.temporizador_jornada -= 1
        if self.temporizador_jornada <= 0:
            self.finalizar_jornada()
            return {"cpu": self.estres_cpu, "ram": self.estres_ram, "latencia": self.latencia, "creditos": self.creditos, "workday_done": True}

        self.contador_ticks += 1
        
        # Secuencia ordenada de ticks delegada a los gestores independientes
        self.red.procesar_trafico()
        self.infraestructura.procesar_carga()
        self.red.calcular_pings()
        self.economia.process_tick()

        return {"cpu": self.estres_cpu, "ram": self.estres_ram, "latencia": self.latencia, "creditos": self.creditos, "workday_done": False}

    # --- PROPIEDADES DE ECONOMÍA ---
    @property
    def creditos(self):
        return self.economia.creditos
    
    @creditos.setter
    def creditos(self, valor):
        self.economia.creditos = valor

    @property
    def ceo_approval(self):
        return self.economia.ceo_approval
    
    @ceo_approval.setter
    def ceo_approval(self, valor):
        self.economia.ceo_approval = valor

    @property
    def geo_balancer_active(self):
        return self.economia.geo_balancer_active
    
    @geo_balancer_active.setter
    def geo_balancer_active(self, valor):
        self.economia.geo_balancer_active = valor

    @property
    def auto_scale_purchased(self):
        return self.economia.auto_scale_purchased
    
    @auto_scale_purchased.setter
    def auto_scale_purchased(self, valor):
        self.economia.auto_scale_purchased = valor

    @property
    def ia_analyzer_purchased(self):
        return self.economia.ia_analyzer_purchased
    
    @ia_analyzer_purchased.setter
    def ia_analyzer_purchased(self, valor):
        self.economia.ia_analyzer_purchased = valor

    @property
    def party_routing_active(self):
        return self.economia.party_routing_active
    
    @party_routing_active.setter
    def party_routing_active(self, valor):
        self.economia.party_routing_active = valor

    @property
    def auto_scale_enabled(self):
        return self.economia.auto_scale_enabled
    
    @auto_scale_enabled.setter
    def auto_scale_enabled(self, valor):
        self.economia.auto_scale_enabled = valor

    @property
    def ia_analyzer_enabled(self):
        return self.economia.ia_analyzer_enabled
    
    @ia_analyzer_enabled.setter
    def ia_analyzer_enabled(self, valor):
        self.economia.ia_analyzer_enabled = valor

    @property
    def is_autoscale_running(self):
        return self.economia.is_autoscale_running
    
    @is_autoscale_running.setter
    def is_autoscale_running(self, valor):
        self.economia.is_autoscale_running = valor

    @property
    def daily_revenue(self):
        return self.economia.daily_revenue
    
    @daily_revenue.setter
    def daily_revenue(self, valor):
        self.economia.daily_revenue = valor

    @property
    def daily_penalty(self):
        return self.economia.daily_penalty
    
    @daily_penalty.setter
    def daily_penalty(self, valor):
        self.economia.daily_penalty = valor

    @property
    def daily_maintenance(self):
        return self.economia.daily_maintenance
    
    @daily_maintenance.setter
    def daily_maintenance(self, valor):
        self.economia.daily_maintenance = valor

    @property
    def daily_satisfied_users(self):
        return self.economia.daily_satisfied_users
    
    @daily_satisfied_users.setter
    def daily_satisfied_users(self, valor):
        self.economia.daily_satisfied_users = valor

    @property
    def daily_base_budget(self):
        return self.economia.daily_base_budget
    
    @daily_base_budget.setter
    def daily_base_budget(self, valor):
        self.economia.daily_base_budget = valor

    @property
    def daily_satisfied_bonus(self):
        return self.economia.daily_satisfied_bonus
    
    @daily_satisfied_bonus.setter
    def daily_satisfied_bonus(self, valor):
        self.economia.daily_satisfied_bonus = valor

    # --- PROPIEDADES DE INFRAESTRUCTURA ---
    @property
    def centros_datos(self):
        return self.infraestructura.centros_datos
    
    @centros_datos.setter
    def centros_datos(self, valor):
        self.infraestructura.centros_datos = valor

    @property
    def estres_cpu(self):
        return self.infraestructura.estres_cpu
    
    @estres_cpu.setter
    def estres_cpu(self, valor):
        self.infraestructura.estres_cpu = valor

    @property
    def estres_ram(self):
        return self.infraestructura.estres_ram
    
    @estres_ram.setter
    def estres_ram(self, valor):
        self.infraestructura.estres_ram = valor

    @property
    def is_downtime(self):
        return self.infraestructura.is_downtime
    
    @is_downtime.setter
    def is_downtime(self, valor):
        self.infraestructura.is_downtime = valor

    # --- PROPIEDADES DE RED ---
    @property
    def usuarios_trafico(self):
        return self.red.usuarios_trafico
    
    @usuarios_trafico.setter
    def usuarios_trafico(self, valor):
        self.red.usuarios_trafico = valor

    @property
    def trafico_ddos(self):
        return self.red.trafico_ddos
    
    @trafico_ddos.setter
    def trafico_ddos(self, valor):
        self.red.trafico_ddos = valor

    @property
    def temporizador_ddos(self):
        return self.red.temporizador_ddos
    
    @temporizador_ddos.setter
    def temporizador_ddos(self, valor):
        self.red.temporizador_ddos = valor

    @property
    def contador_ticks(self):
        return self.red.contador_ticks
    
    @contador_ticks.setter
    def contador_ticks(self, valor):
        self.red.contador_ticks = valor

    @property
    def latencia(self):
        return self.red.latencia
    
    @latencia.setter
    def latencia(self, valor):
        self.red.latencia = valor

    @property
    def tipo_pronostico(self):
        return self.red.tipo_pronostico
    
    @tipo_pronostico.setter
    def tipo_pronostico(self, valor):
        self.red.tipo_pronostico = valor

    @property
    def usuarios_trafico_regional(self):
        return self.red.usuarios_trafico_regional
    
    @usuarios_trafico_regional.setter
    def usuarios_trafico_regional(self, valor):
        self.red.usuarios_trafico_regional = valor

    @property
    def pings_regionales(self):
        return self.red.pings_regionales
    
    @pings_regionales.setter
    def pings_regionales(self, valor):
        self.red.pings_regionales = valor

    @property
    def region_ddos(self):
        return self.red.region_ddos
    
    @region_ddos.setter
    def region_ddos(self, valor):
        self.red.region_ddos = valor

    @property
    def region_torneo(self):
        return self.red.region_torneo
    
    @region_torneo.setter
    def region_torneo(self, valor):
        self.red.region_torneo = valor


