from configuracion import CONFIG_BALANCEO

class GestorEconomia:
    def __init__(self, motor):
        self.motor = motor
        
        # Presupuesto y reputación
        self.creditos = CONFIG_BALANCEO.get("CREDITOS_INICIALES", 12000.0)
        self.aprobacion_ceo = 100.0
        
        # Upgrades contratados (CAPEX global)
        self.balanceador_geo_activo = False
        self.autoescalado_comprado = False
        self.analizador_ia_comprado = False
        self.ruteo_partidas_activo = False
        
        # Toggles activos (OPEX)
        self.autoescalado_habilitado = False
        self.analizador_ia_habilitado = False
        self.autoescalado_ejecutandose = False
        
        # Historial de finanzas diarias
        self.ingresos_diarios = 0.0
        self.penalizacion_diaria = 0.0
        self.mantenimiento_diario = 0.0
        self.usuarios_satisfechos_diarios = 0
        self.presupuesto_base_diario = 0.0
        self.bono_satisfechos_diario = 0.0

    def iniciar_jornada(self):
        self.ingresos_diarios = 0.0
        self.penalizacion_diaria = 0.0
        self.mantenimiento_diario = 0.0
        self.usuarios_satisfechos_diarios = 0

    def finalizar_jornada(self):
        # Calcular costos fijos diarios de mantenimiento
        mantenimiento = CONFIG_BALANCEO["MANTENIMIENTO_DIARIO_SERVIDOR_BASE"]
        
        for region, dc in self.motor.centros_datos.items():
            mantenimiento += dc["cantidad_servidores"] * CONFIG_BALANCEO["MANTENIMIENTO_DIARIO_POR_SERVIDOR_FISICO"]
            mantenimiento += 150.0  # Costo fijo por cada datacenter abierto
            
        if self.autoescalado_comprado:
            mantenimiento += CONFIG_BALANCEO["MANTENIMIENTO_DIARIO_AUTOESCALADO"]
        if self.balanceador_geo_activo:
            mantenimiento += CONFIG_BALANCEO["MANTENIMIENTO_DIARIO_BALANCEADOR_GEO"]
        if self.analizador_ia_comprado:
            mantenimiento += CONFIG_BALANCEO["MANTENIMIENTO_DIARIO_ANALIZADOR_IA"]
        if self.ruteo_partidas_activo:
            mantenimiento += CONFIG_BALANCEO["MANTENIMIENTO_DIARIO_RUTEO_PARTIDAS"]
        
        self.mantenimiento_diario = mantenimiento
        self.presupuesto_base_diario = CONFIG_BALANCEO["PRESUPUESTO_BASE_DIARIO"]
        self.bono_satisfechos_diario = self.usuarios_satisfechos_diarios * CONFIG_BALANCEO["BONO_POR_USUARIO_SATISFECHO"]
        self.ingresos_diarios = self.presupuesto_base_diario + self.bono_satisfechos_diario
        
        self.creditos += self.ingresos_diarios
        self.creditos -= mantenimiento
        
        if self.creditos < CONFIG_BALANCEO["LIMITE_CREDITOS_FIN_JUEGO"] or self.aprobacion_ceo <= 0.0:
            self.motor.fin_del_juego = True
            self.motor.ultimo_mensaje_evento = "🚨 FIN DE LA JORNADA: Has sido despedido por mala gestión corporativa."
        else:
            self.motor.ultimo_mensaje_evento = f"Turno finalizado. Reporte disponible. Configura el Día {self.motor.dias_transcurridos+1}."
            self.motor.red.generar_pronostico()

    def alternar_autoescalado(self):
        if self.autoescalado_comprado and not self.motor.fin_del_juego:
            self.autoescalado_habilitado = not self.autoescalado_habilitado
            self.motor.ultimo_mensaje_evento = f"Auto-Scaling {'ENCENDIDO' if self.autoescalado_habilitado else 'APAGADO'}."

    def alternar_analizador_ia(self):
        if self.analizador_ia_comprado and not self.motor.fin_del_juego:
            self.analizador_ia_habilitado = not self.analizador_ia_habilitado
            self.motor.ultimo_mensaje_evento = f"Filtro de Tráfico IA {'ENCENDIDO' if self.analizador_ia_habilitado else 'APAGADO'}."

    def comprar_continente(self, continente):
        if self.motor.jornada_activa:
            return False
        if continente in self.motor.continentes_comprados:
            self.motor.ultimo_mensaje_evento = f"El Enlace Continental con {continente} ya está activo."
            return False
        if not self.motor.esta_continente_desbloqueado(continente):
            self.motor.ultimo_mensaje_evento = f"🚨 ERROR: El mercado de {continente} está bloqueado por días de supervivencia."
            return False
        costo = CONFIG_BALANCEO["COSTO_DESBLOQUEO_CONTINENTE"]
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
        if not self.motor.esta_ciudad_desbloqueada(region):
            self.motor.ultimo_mensaje_evento = f"🚨 ERROR: El mercado de {region} está bloqueado."
            return False
        if region in self.motor.centros_datos:
            self.motor.ultimo_mensaje_evento = f"El Data Center de {region} ya está abierto."
            return False
        costo = CONFIG_BALANCEO["COSTO_ABRIR_DATACENTER"]
        if self.creditos >= costo:
            self.creditos -= costo
            self.motor.centros_datos[region] = {
                "cantidad_servidores": 0,
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
        costo = CONFIG_BALANCEO["COSTO_MEJORA_SERVIDOR"]
        if self.creditos >= costo:
            self.creditos -= costo
            self.motor.centros_datos[region]["cantidad_servidores"] += 1
            self.motor.ultimo_mensaje_evento = f"Servidor instalado con éxito en el Data Center de {region}."
            return True
        else:
            self.motor.ultimo_mensaje_evento = f"🚨 Presupuesto insuficiente para comprar servidor ($600)."
            return False

    def comprar_mejora(self, clave):
        if self.motor.jornada_activa and clave not in ["autoscale", "ia"]:
            return False
        
        if clave == "autoscale" and not self.autoescalado_comprado and self.creditos >= CONFIG_BALANCEO["COSTO_MEJORA_AUTOESCALADO"]:
            self.creditos -= CONFIG_BALANCEO["COSTO_MEJORA_AUTOESCALADO"]
            self.autoescalado_comprado = True
            self.motor.ultimo_mensaje_evento = "Auto-Scaling contratado. Panel de control activo."
            return True
        elif clave == "geo" and not self.balanceador_geo_activo and self.creditos >= CONFIG_BALANCEO["COSTO_MEJORA_BALANCEADOR_GEO"]:
            self.creditos -= CONFIG_BALANCEO["COSTO_MEJORA_BALANCEADOR_GEO"]
            self.balanceador_geo_activo = True
            self.motor.ultimo_mensaje_evento = "Router Geo DNS global activado (elimina penalizaciones de overflow)."
            return True
        elif clave == "ia" and not self.analizador_ia_comprado and self.creditos >= CONFIG_BALANCEO["COSTO_MEJORA_ANALIZADOR_IA"]:
            self.creditos -= CONFIG_BALANCEO["COSTO_MEJORA_ANALIZADOR_IA"]
            self.analizador_ia_comprado = True
            self.motor.ultimo_mensaje_evento = "Filtro de Tráfico IA contratado."
            return True
        elif clave == "party" and not self.ruteo_partidas_activo and self.creditos >= CONFIG_BALANCEO["COSTO_MEJORA_RUTEO_PARTIDAS"]:
            self.creditos -= CONFIG_BALANCEO["COSTO_MEJORA_RUTEO_PARTIDAS"]
            self.ruteo_partidas_activo = True
            self.motor.ultimo_mensaje_evento = "Ruteo lógico por Tipo de Partida configurado."
            return True
        return False

    def procesar_tick(self):
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
            self.motor.esta_caido = True
            self.creditos -= CONFIG_BALANCEO["PENALIZACION_CAIDA"]
            self.penalizacion_diaria += CONFIG_BALANCEO["PENALIZACION_CAIDA"]
            self.aprobacion_ceo = max(0.0, self.aprobacion_ceo - 5.0)
        else:
            self.motor.esta_caido = False
            if latencia < 100.0:
                self.usuarios_satisfechos_diarios += trafico_total_atendido
            
            if latencia > 100.0:
                penalizacion = CONFIG_BALANCEO["PENALIZACION_LATENCIA"]
                self.creditos -= penalizacion
                self.penalizacion_diaria += penalizacion
                self.aprobacion_ceo = max(0.0, self.aprobacion_ceo - 2.0)
                self.motor.ultimo_mensaje_evento = "SLA BREACH: Latencia elevada en la red global."
                
            if estres_cpu < 80.0 and latencia <= 50.0:
                self.aprobacion_ceo = min(100.0, self.aprobacion_ceo + 1.0)
                
            if self.autoescalado_comprado and self.autoescalado_habilitado:
                self.creditos -= CONFIG_BALANCEO["COSTO_TICK_AUTOESCALADO_ACTIVO"]
            if self.analizador_ia_comprado and self.analizador_ia_habilitado:
                self.creditos -= CONFIG_BALANCEO["COSTO_TICK_IA_ACTIVA"]
