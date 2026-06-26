# ==============================================================================
# DICCIONARIO DE BALANCEO (BALANCING_CONFIG)
# ==============================================================================
BALANCING_CONFIG = {
    # REGIONES DEL SISTEMA (Sub-regiones por ciudades)
    "LOCATIONS": {
        "América": ["Miami", "Bogotá", "São Paulo"],
        "Europa": ["Madrid", "Frankfurt", "Londres"],
        "Asia": ["Tokio", "Seúl", "Singapur"]
    },
    
    # Mejoras y Costes de Infraestructura (CAPEX)
    "STARTING_CREDITS": 12000.0,             # Presupuesto con el que inicia el jugador
    "CONTINENT_UNLOCK_COST": 2000.0,         # Coste para abrir enlaces de red continental
    "UPGRADE_SERVER_COST": 600.0,
    "UPGRADE_AUTOSCALE_COST": 2500.0,
    "UPGRADE_GEO_BALANCER_COST": 5000.0,
    "UPGRADE_IA_ANALYZER_COST": 7500.0,
    "UPGRADE_PARTY_ROUTING_COST": 10000.0,
    
    # NUEVAS MEJORAS DE SALA Y NODOS
    "OPEN_DATACENTER_COST": 3500.0,         # Abrir un nuevo Data Center regional
    
    # Límites Base
    "CAPACITY_BASE": 1500.0,                 # Capacidad inicial del Servidor 1 (req/s)
    "AUTOSCALE_MULTIPLIER": 1.35,            
    "AUTOSCALE_TICK_COST": 3.0,              
    
    # Red y Físicas
    "TRAFFIC_BASE": 100.0,              
    "TRAFFIC_GROWTH": 1.04,
    "REVENUE_PER_USER": 0.0,            
    "DAILY_BASE_BUDGET": 250.0,         
    "BONUS_PER_SATISFIED_USER": 0.12,   
    "DOWNTIME_PENALTY": 40.0,           
    "LATENCY_PENALTY": 10.0,            
    "BASE_LATENCY_MS": 25.0,
    
    # Tiempo y Game Over
    "DAYS_PER_TICK": 1,                 
    "GAME_OVER_CREDITS_LIMIT": -3000.0, 
    
    # Costos Operativos por Tick (OPEX)
    "IA_ACTIVE_TICK_COST": 15.0,        
    "AUTOSCALE_ACTIVE_TICK_COST": 5.0,  
    
    # Costos Fijos de Mantenimiento Diario (Descontados al finalizar la jornada)
    "DAILY_MAINTENANCE_BASE_SERVER": 50.0,
    "DAILY_MAINTENANCE_PER_PHYSICAL_SERVER": 80.0,
    "DAILY_MAINTENANCE_AUTOSCALE": 150.0,
    "DAILY_MAINTENANCE_GEO_BALANCER": 200.0,
    "DAILY_MAINTENANCE_IA_ANALYZER": 250.0,
    "DAILY_MAINTENANCE_PARTY_ROUTING": 300.0
}

