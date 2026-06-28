# ==============================================================================
# DICCIONARIO DE BALANCEO (CONFIG_BALANCEO)
# ==============================================================================
CONFIG_BALANCEO = {
    # REGIONES DEL SISTEMA (Sub-regiones por ciudades)
    "UBICACIONES": {
        "América": ["Miami", "Bogotá", "São Paulo"],
        "Europa": ["Madrid", "Frankfurt", "Londres"],
        "Asia": ["Tokio", "Seúl", "Singapur"]
    },
    
    # Mejoras y Costes de Infraestructura (CAPEX)
    "CREDITOS_INICIALES": 12000.0,             # Presupuesto con el que inicia el jugador
    "COSTO_DESBLOQUEO_CONTINENTE": 2000.0,     # Coste para abrir enlaces de red continental
    "COSTO_MEJORA_SERVIDOR": 600.0,
    "COSTO_MEJORA_AUTOESCALADO": 2500.0,
    "COSTO_MEJORA_BALANCEADOR_GEO": 5000.0,
    "COSTO_MEJORA_ANALIZADOR_IA": 7500.0,
    "COSTO_MEJORA_RUTEO_PARTIDAS": 10000.0,
    
    # NUEVAS MEJORAS DE SALA Y NODOS
    "COSTO_ABRIR_DATACENTER": 3500.0,         # Abrir un nuevo Data Center regional
    
    # Límites Base
    "CAPACIDAD_BASE": 1500.0,                 # Capacidad inicial del Servidor 1 (req/s)
    "MULTIPLICADOR_AUTOESCALADO": 1.35,            
    "COSTO_TICK_AUTOESCALADO": 3.0,              
    
    # Red y Físicas
    "TRAFICO_BASE": 100.0,              
    "CRECIMIENTO_TRAFICO": 1.04,
    "INGRESOS_POR_USUARIO": 0.0,            
    "PRESUPUESTO_BASE_DIARIO": 250.0,         
    "BONO_POR_USUARIO_SATISFECHO": 0.12,   
    "PENALIZACION_CAIDA": 40.0,           
    "PENALIZACION_LATENCIA": 10.0,            
    "LATENCIA_BASE_MS": 25.0,
    
    # Tiempo y Game Over
    "DIAS_POR_TICK": 1,                 
    "LIMITE_CREDITOS_FIN_JUEGO": -3000.0, 
    
    # Costos Operativos por Tick (OPEX)
    "COSTO_TICK_IA_ACTIVA": 15.0,        
    "COSTO_TICK_AUTOESCALADO_ACTIVO": 5.0,  
    
    # Costos Fijos de Mantenimiento Diario (Descontados al finalizar la jornada)
    "MANTENIMIENTO_DIARIO_SERVIDOR_BASE": 50.0,
    "MANTENIMIENTO_DIARIO_POR_SERVIDOR_FISICO": 80.0,
    "MANTENIMIENTO_DIARIO_AUTOESCALADO": 150.0,
    "MANTENIMIENTO_DIARIO_BALANCEADOR_GEO": 200.0,
    "MANTENIMIENTO_DIARIO_ANALIZADOR_IA": 250.0,
    "MANTENIMIENTO_DIARIO_RUTEO_PARTIDAS": 300.0
}
