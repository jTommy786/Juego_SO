from configuracion import CONFIG_BALANCEO

class GestorInfraestructura:
    def __init__(self, motor):
        self.motor = motor
        self.estres_cpu = 0.0
        self.estres_ram = 0.0
        self.esta_caido = False
        
        # Inicializar Data Centers (Miami con 1 servidor al inicio)
        self.centros_datos = {
            "Miami": {
                "cantidad_servidores": 1,
                "estres_cpu": 0.0,
                "estres_ram": 0.0
            }
        }

    def procesar_carga(self):
        # Calcular Carga y Estrés por Sala de Servidores
        capacidades_dc = {}
        for ciudad, dc in self.centros_datos.items():
            capacidad = dc["cantidad_servidores"] * CONFIG_BALANCEO["CAPACIDAD_BASE"]
            capacidades_dc[ciudad] = capacidad

        for ciudad, dc in self.centros_datos.items():
            capacidad_dc = capacidades_dc[ciudad]
            capacidad_dc_efectiva = max(10.0, capacidad_dc)
            
            # Tránsito total de esta sala (local + overflow enrutado aquí)
            trafico_dc = (
                self.motor.red.atendido_local.get(ciudad, 0) +
                sum(self.motor.red.atendido_mismo_continente[src].get(ciudad, 0) for src in self.motor.todas_las_ciudades) +
                sum(self.motor.red.atendido_otro_continente[src].get(ciudad, 0) for src in self.motor.todas_las_ciudades)
            )
            
            cpu_dc = (trafico_dc / capacidad_dc_efectiva) * 100.0
            if self.motor.ruteo_partidas_activo:
                cpu_dc *= 0.75
            dc["estres_cpu"] = min(100.0, cpu_dc)
            
            ram_dc = (trafico_dc / (capacidad_dc_efectiva * 1.15)) * 100.0
            if dc["estres_cpu"] > 85.0:
                ram_dc += 5.0
            dc["estres_ram"] = min(100.0, ram_dc)

        # Carga Global (Promedio de salas abiertas)
        trafico_total_atendido = (
            sum(self.motor.red.atendido_local.values()) +
            sum(sum(rem.values()) for rem in self.motor.red.atendido_mismo_continente.values()) +
            sum(sum(rem.values()) for rem in self.motor.red.atendido_otro_continente.values())
        )
        capacidad_global_total = sum(capacidades_dc.values())
        capacidad_global_efectiva = max(10.0, capacidad_global_total)
        
        cpu_global = (trafico_total_atendido / capacidad_global_efectiva) * 100.0
        if self.motor.ruteo_partidas_activo:
            cpu_global *= 0.75
        self.estres_cpu = min(100.0, cpu_global)
        
        ram_global = (trafico_total_atendido / (capacidad_global_efectiva * 1.15)) * 100.0
        if self.estres_cpu > 85.0:
            ram_global += 5.0
        self.estres_ram = min(100.0, ram_global)

        # Determinar downtime
        if self.estres_cpu >= 100.0 or self.estres_ram >= 100.0:
            self.esta_caido = True
        else:
            self.esta_caido = False
