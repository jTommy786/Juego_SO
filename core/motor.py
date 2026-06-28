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
        self.europa_desbloqueada = False
        self.asia_desbloqueada = False
        
        # Continentes comprados/activos (América por defecto)
        self.continentes_comprados = ["América"]

        # Extraer lista de todas las ciudades (Sub-regiones)
        self.todas_las_ciudades = []
        for ciudades in CONFIG_BALANCEO["UBICACIONES"].values():
            self.todas_las_ciudades.extend(ciudades)

        # Instanciar los tres Managers de dominio (Facade)
        self.red = GestorRed(self)
        self.infraestructura = GestorInfraestructura(self)
        self.economia = GestorEconomia(self)

    def esta_continente_desbloqueado(self, continente):
        if continente == "América":
            return True
        elif continente == "Europa":
            return self.europa_desbloqueada
        elif continente == "Asia":
            return self.asia_desbloqueada
        return False

    def esta_ciudad_desbloqueada(self, ciudad):
        cont = self.obtener_continente_ciudad(ciudad)
        return cont in self.continentes_comprados

    def obtener_continente_ciudad(self, ciudad):
        for cont, ciudades in CONFIG_BALANCEO["UBICACIONES"].items():
            if ciudad in ciudades:
                return cont
        return None

    def generar_pronostico(self):
        self.red.generar_pronostico()

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
        if self.dias_transcurridos >= 5 and not self.europa_desbloqueada:
            self.europa_desbloqueada = True
            unlock_msg = "🌐 NUEVO MERCADO: ¡Europa ahora está disponible para expandir la red!"
        if self.dias_transcurridos >= 10 and not self.asia_desbloqueada:
            self.asia_desbloqueada = True
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
        self.economia.procesar_tick()

        return {"cpu": self.estres_cpu, "ram": self.estres_ram, "latencia": self.latencia, "creditos": self.creditos, "workday_done": False}

    # --- PROPIEDADES DE ECONOMÍA ---
    @property
    def creditos(self):
        return self.economia.creditos
    
    @creditos.setter
    def creditos(self, valor):
        self.economia.creditos = valor

    @property
    def aprobacion_ceo(self):
        return self.economia.aprobacion_ceo
    
    @aprobacion_ceo.setter
    def aprobacion_ceo(self, valor):
        self.economia.aprobacion_ceo = valor

    @property
    def balanceador_geo_activo(self):
        return self.economia.balanceador_geo_activo
    
    @balanceador_geo_activo.setter
    def balanceador_geo_activo(self, valor):
        self.economia.balanceador_geo_activo = valor

    @property
    def autoescalado_comprado(self):
        return self.economia.autoescalado_comprado
    
    @autoescalado_comprado.setter
    def autoescalado_comprado(self, valor):
        self.economia.autoescalado_comprado = valor

    @property
    def analizador_ia_comprado(self):
        return self.economia.analizador_ia_comprado
    
    @analizador_ia_comprado.setter
    def analizador_ia_comprado(self, valor):
        self.economia.analizador_ia_comprado = valor

    @property
    def ruteo_partidas_activo(self):
        return self.economia.ruteo_partidas_activo
    
    @ruteo_partidas_activo.setter
    def ruteo_partidas_activo(self, valor):
        self.economia.ruteo_partidas_activo = valor

    @property
    def autoescalado_habilitado(self):
        return self.economia.autoescalado_habilitado
    
    @autoescalado_habilitado.setter
    def autoescalado_habilitado(self, valor):
        self.economia.autoescalado_habilitado = valor

    @property
    def analizador_ia_habilitado(self):
        return self.economia.analizador_ia_habilitado
    
    @analizador_ia_habilitado.setter
    def analizador_ia_habilitado(self, valor):
        self.economia.analizador_ia_habilitado = valor

    @property
    def autoescalado_ejecutandose(self):
        return self.economia.autoescalado_ejecutandose
    
    @autoescalado_ejecutandose.setter
    def autoescalado_ejecutandose(self, valor):
        self.economia.autoescalado_ejecutandose = valor

    @property
    def ingresos_diarios(self):
        return self.economia.ingresos_diarios
    
    @ingresos_diarios.setter
    def ingresos_diarios(self, valor):
        self.economia.ingresos_diarios = valor

    @property
    def penalizacion_diaria(self):
        return self.economia.penalizacion_diaria
    
    @penalizacion_diaria.setter
    def penalizacion_diaria(self, valor):
        self.economia.penalizacion_diaria = valor

    @property
    def mantenimiento_diario(self):
        return self.economia.mantenimiento_diario
    
    @mantenimiento_diario.setter
    def mantenimiento_diario(self, valor):
        self.economia.mantenimiento_diario = valor

    @property
    def usuarios_satisfechos_diarios(self):
        return self.economia.usuarios_satisfechos_diarios
    
    @usuarios_satisfechos_diarios.setter
    def usuarios_satisfechos_diarios(self, valor):
        self.economia.usuarios_satisfechos_diarios = valor

    @property
    def presupuesto_base_diario(self):
        return self.economia.presupuesto_base_diario
    
    @presupuesto_base_diario.setter
    def presupuesto_base_diario(self, valor):
        self.economia.presupuesto_base_diario = valor

    @property
    def bono_satisfechos_diario(self):
        return self.economia.bono_satisfechos_diario
    
    @bono_satisfechos_diario.setter
    def bono_satisfechos_diario(self, valor):
        self.economia.bono_satisfechos_diario = valor

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
    def esta_caido(self):
        return self.infraestructura.esta_caido
    
    @esta_caido.setter
    def esta_caido(self, valor):
        self.infraestructura.esta_caido = valor

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
