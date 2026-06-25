import tkinter as tk
from tkinter import ttk, messagebox
import random
import csv

class PingZeroGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ping Zero: El Simulador de Servidores")
        self.root.geometry("780x580")
        self.root.resizable(False, False)
        
        # --- Variables de Estado Internas (Mantienen el valor técnico) ---
        self.turno_actual = 1
        self.max_turnos = 10
        self.creditos = 600
        self.estabilidad_sistema = 3
        self.partida_activa = True
        self.limite_ping = 500
        
        self.infraestructura = {
            "servidores_fisicos": 1,       # Mapea a 'Más Espacio'
            "auto_scaling": False,         # Mapea a 'Servidores de Reserva'
            "balanceo_geografico": False,  # Mapea a 'Antenas Regionales'
            "analizador_ia": False,        # Mapea a 'Escudo Anti-Hackers'
            "ruteo_partidas": False        # Mapea a 'Servidores VIP'
        }
        
        self.historial_experimento = []
        
        # --- Estilo Visual Oscuro ---
        self.root.configure(bg="#1e1e2e")
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Estres.Horizontal.TProgressbar", troughcolor="#313244", background="#f38ba8", thickness=22)
        
        self.crear_componentes_gui()
        self.actualizar_interfaz_visual()
        
        # Mostrar las instrucciones entendibles apenas abre el juego
        self.root.after(500, self.mostrar_instrucciones_iniciales)

    def mostrar_instrucciones_iniciales(self):
        instrucciones = (
            "¡BIENVENIDO A PING ZERO! 🎮\n\n"
            "Eres el encargado de mantener estables los servidores de un videojuego.\n"
            "Tu objetivo es sobrevivir 10 turnos de un torneo sin que el sistema se caiga.\n\n"
            "💡 REGLAS DEL JUEGO:\n"
            "1. Mira la barra de carga: si llega al 100%, los servidores colapsan.\n"
            "2. Controla el LAG: a más carga, más lag tendrán los jugadores y ganarás menos dinero.\n"
            "3. Usa tu dinero en la TIENDA para comprar mejoras antes de presionar 'Procesar Siguiente Turno'.\n\n"
            "¡Buena suerte, evita los ataques cibernéticos y los picos de jugadores!"
        )
        messagebox.showinfo("Guía de Inicio Rápido", instrucciones)

    def crear_componentes_gui(self):
        # Encabezado
        header_frame = tk.Frame(self.root, bg="#11111b", height=50)
        header_frame.pack(fill="x", side="top")
        
        lbl_titulo = tk.Label(header_frame, text="🕹️ PING ZERO: SERVER MANAGER", font=("Helvetica", 13, "bold"), fg="#cdd6f4", bg="#11111b")
        lbl_titulo.pack(side="left", padx=15, pady=10)
        
        self.lbl_turno = tk.Label(header_frame, text="", font=("Helvetica", 11, "bold"), fg="#fab387", bg="#11111b")
        self.lbl_turno.pack(side="right", padx=15, pady=10)
        
        # Panel de Monitoreo Carga e Info
        self.status_frame = tk.LabelFrame(self.root, text=" 📊 Estado de los Servidores en Vivo ", font=("Helvetica", 10, "bold"), fg="#a6e3a1", bg="#1e1e2e", bd=2)
        self.status_frame.pack(fill="x", padx=15, pady=10)
        
        self.lbl_evento = tk.Label(self.status_frame, text="Evento: Preparando el torneo...", font=("Helvetica", 11, "bold"), fg="#cdd6f4", bg="#1e1e2e")
        self.lbl_evento.pack(anchor="w", padx=10, pady=5)
        
        lbl_bar = tk.Label(self.status_frame, text="Capacidad de Carga del Servidor (CPU/RAM):", font=("Helvetica", 10), fg="#a6adc8", bg="#1e1e2e")
        lbl_bar.pack(anchor="w", padx=10)
        
        self.progress_estres = ttk.Progressbar(self.status_frame, style="Estres.Horizontal.TProgressbar", orient="horizontal", mode="determinate")
        self.progress_estres.pack(fill="x", padx=10, pady=5)
        
        stats_frame = tk.Frame(self.status_frame, bg="#1e1e2e")
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        self.lbl_latencia = tk.Label(stats_frame, text="Lag (Ping): --/500 ms", font=("Helvetica", 11, "bold"), fg="#f38ba8", bg="#1e1e2e")
        self.lbl_latencia.pack(side="left", expand=True)
        
        self.lbl_jugadores = tk.Label(stats_frame, text="Jugadores Jugando: -- / --", font=("Helvetica", 11, "bold"), fg="#89b4fa", bg="#1e1e2e")
        self.lbl_jugadores.pack(side="left", expand=True)

        self.lbl_limite_usuarios = tk.Label(stats_frame, text="Límite de Usuarios: --", font=("Helvetica", 11, "bold"), fg="#fab387", bg="#1e1e2e")
        self.lbl_limite_usuarios.pack(side="left", expand=True)

        self.lbl_estabilidad = tk.Label(stats_frame, text="Estabilidad: 3/3", font=("Helvetica", 11, "bold"), fg="#a6e3a1", bg="#1e1e2e")
        self.lbl_estabilidad.pack(side="left", expand=True)
        
        # Indicador de recomendación: qué mejora conviene comprar este turno
        self.lbl_recomendacion = tk.Label(self.status_frame, text="💡 Compra mejoras en la tienda y presiona 'Avanzar de Turno'.", font=("Helvetica", 9, "bold"), fg="#f9e2af", bg="#1e1e2e", justify="left", anchor="w", wraplength=720)
        self.lbl_recomendacion.pack(anchor="w", padx=10, pady=(0, 8), fill="x")
        
        # Panel Inferior (Tienda y Bitácora)
        bottom_frame = tk.Frame(self.root, bg="#1e1e2e")
        bottom_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        # TIENDA SIMPLIFICADA
        self.shop_frame = tk.LabelFrame(bottom_frame, text=" 🛒 Tienda de Mejoras (Simplificada) ", font=("Helvetica", 10, "bold"), fg="#f9e2af", bg="#1e1e2e")
        self.shop_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.lbl_creditos = tk.Label(self.shop_frame, text="", font=("Helvetica", 11, "bold"), fg="#f9e2af", bg="#1e1e2e")
        self.lbl_creditos.pack(anchor="w", padx=10, pady=5)
        
        # Botones con nombres amigables
        self.btn_srv = tk.Button(self.shop_frame, text="🚀 Más Espacio en Servidor ($500)\n[Soporta más jugadores a la vez]", justify="left", command=lambda: self.comprar_mejora("servidores_fisicos", 500), bg="#313244", fg="#cdd6f4", relief="flat", font=("Helvetica", 9))
        self.btn_srv.pack(fill="x", padx=10, pady=4)
        
        self.btn_as = tk.Button(self.shop_frame, text="☁️ Servidores de Reserva / Nube ($1500)\n[Se activan solos si te vas a saturar]", justify="left", command=lambda: self.comprar_mejora("auto_scaling", 1500), bg="#313244", fg="#cdd6f4", relief="flat", font=("Helvetica", 9))
        self.btn_as.pack(fill="x", padx=10, pady=4)
        
        self.btn_geo = tk.Button(self.shop_frame, text="🌍 Antenas Regionales ($2000)\n[Elimina por completo el lag de otros países]", justify="left", command=lambda: self.comprar_mejora("balanceo_geografico", 2000), bg="#313244", fg="#cdd6f4", relief="flat", font=("Helvetica", 9))
        self.btn_geo.pack(fill="x", padx=10, pady=4)
        
        self.btn_ia = tk.Button(self.shop_frame, text="🛡️ Escudo Anti-Hackers / DDoS ($2500)\n[Bloquea ataques de tráfico falso]", justify="left", command=lambda: self.comprar_mejora("analizador_ia", 2500), bg="#313244", fg="#cdd6f4", relief="flat", font=("Helvetica", 9))
        self.btn_ia.pack(fill="x", padx=10, pady=4)
        
        self.btn_rut = tk.Button(self.shop_frame, text="🏆 Servidores VIP de Torneos ($3000)\n[Evita que partidas competitivas colapsen]", justify="left", command=lambda: self.comprar_mejora("ruteo_partidas", 3000), bg="#313244", fg="#cdd6f4", relief="flat", font=("Helvetica", 9))
        self.btn_rut.pack(fill="x", padx=10, pady=4)
        
        # Bitácora / Registro de eventos
        log_frame = tk.LabelFrame(bottom_frame, text=" 📝 Alertas y Reportes del Sistema ", font=("Helvetica", 10, "bold"), fg="#cba6f7", bg="#1e1e2e")
        log_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.txt_logs = tk.Text(log_frame, bg="#11111b", fg="#a6e3a1", font=("Consolas", 9), bd=0, state="disabled")
        self.txt_logs.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Botón de acción principal
        self.btn_turno = tk.Button(self.root, text="AVANZAR DE TURNO / VER QUÉ PASA >", font=("Helvetica", 11, "bold"), bg="#a6e3a1", fg="#11111b", activebackground="#89b4fa", command=self.procesar_turno, relief="raised", height=2)
        self.btn_turno.pack(fill="x", padx=15, pady=10)
        
        # Botón para reiniciar el juego (oculto hasta que termine el torneo)
        self.btn_reiniciar = tk.Button(self.root, text="🔄 VOLVER A JUGAR", font=("Helvetica", 11, "bold"), bg="#89b4fa", fg="#11111b", activebackground="#a6e3a1", command=self.reiniciar_juego, relief="raised", height=2)

    def log(self, mensaje):
        self.txt_logs.configure(state="normal")
        self.txt_logs.insert(tk.END, mensaje + "\n")
        self.txt_logs.see(tk.END)
        self.txt_logs.configure(state="disabled")

    def obtener_limite_usuarios(self):
        nivel_servidor = self.infraestructura["servidores_fisicos"]
        return 4000 + (nivel_servidor - 1) * 3000

    def terminar_partida(self, titulo, mensaje, es_victoria=False):
        self.partida_activa = False
        self.btn_turno.config(state="disabled")
        self.btn_turno.pack_forget()
        self.btn_reiniciar.pack(fill="x", padx=15, pady=10)

        if self.historial_experimento:
            self.exportar_datos_csv()

        if es_victoria:
            messagebox.showinfo(titulo, mensaje)
        else:
            messagebox.showerror(titulo, mensaje)

    def comprar_mejora(self, tipo, costo):
        if self.creditos >= costo:
            if tipo == "servidores_fisicos":
                self.infraestructura[tipo] += 1
                self.creditos -= costo
                self.log(f"[TIENDA] Mejorado: Capacidad base aumentada (Nivel {self.infraestructura[tipo]}).")
            elif not self.infraestructura[tipo]:
                self.infraestructura[tipo] = True
                self.creditos -= costo
                self.log(f"[TIENDA] Comprado con éxito: {tipo.replace('_', ' ').upper()}.")
            else:
                messagebox.showinfo("Tienda", "¡Ya tienes esta mejora instalada!")
                return
            self.actualizar_interfaz_visual()
        else:
            messagebox.showwarning("Sin dinero", "No tienes suficientes créditos para comprar esta mejora operativa.")

    def actualizar_interfaz_visual(self):
        self.lbl_creditos.config(text=f"Tu Dinero Disponible: ${self.creditos:,}")
        self.lbl_turno.config(text=f"Día del Torneo (Turno): {self.turno_actual}/{self.max_turnos}")
        self.lbl_estabilidad.config(text=f"Estabilidad: {self.estabilidad_sistema}/3")
        self.lbl_limite_usuarios.config(text=f"Límite de Usuarios: {self.obtener_limite_usuarios():,}")
        
        # Deshabilitar botones ya comprados para guiar al jugador
        if self.infraestructura["auto_scaling"]: self.btn_as.config(text="☁️ Servidores de Reserva [INSTALADO]", state="disabled", bg="#45475a")
        if self.infraestructura["balanceo_geografico"]: self.btn_geo.config(text="🌍 Antenas Regionales [INSTALADO]", state="disabled", bg="#45475a")
        if self.infraestructura["analizador_ia"]: self.btn_ia.config(text="🛡️ Escudo Anti-Hackers [INSTALADO]", state="disabled", bg="#45475a")
        if self.infraestructura["ruteo_partidas"]: self.btn_rut.config(text="🏆 Servidores VIP [INSTALADO]", state="disabled", bg="#45475a")

    def actualizar_recomendaciones(self, evento, estres, latencia, ddos):
        """Analiza la situación del turno y muestra en rojo qué mejoras faltantes
        conviene comprar, para que el jugador termine comprando todas."""
        avisos = []
        
        if estres > 60 and self.infraestructura["servidores_fisicos"] < 3:
            avisos.append("🔴 MÁS ESPACIO EN SERVIDOR: tu capacidad base ya no alcanza para el tráfico actual.")
        
        if not self.infraestructura["auto_scaling"] and estres > 65:
            avisos.append("🔴 SERVIDORES DE RESERVA / NUBE: necesitas escalado automático para picos de tráfico.")
        
        if not self.infraestructura["balanceo_geografico"] and latencia > 150:
            avisos.append("🔴 ANTENAS REGIONALES: el lag de jugadores de otros países está muy alto.")
        
        if not self.infraestructura["analizador_ia"] and ddos > 0:
            avisos.append("🔴 ESCUDO ANTI-HACKERS / DDoS: estás recibiendo tráfico falso sin filtrar.")
        
        if not self.infraestructura["ruteo_partidas"] and "Torneo" in evento:
            avisos.append("🔴 SERVIDORES VIP DE TORNEOS: las partidas competitivas necesitan rutas dedicadas.")
        
        if avisos:
            self.lbl_recomendacion.config(text="\n".join(avisos), fg="#f38ba8")
        else:
            self.lbl_recomendacion.config(text="✅ Tu infraestructura está bien preparada para este turno.", fg="#a6e3a1")

    def procesar_turno(self):
        if not self.partida_activa or self.turno_actual > self.max_turnos:
            return

        # Sucesos aleatorios traducidos a lenguaje común
        evento = random.choice(["Tráfico Común y Corriente", "🏆 ¡Gran Final del Torneo! (Mucho Tráfico)", "🚨 ¡Ataque Informático Masivo! (Hackers)"])
        self.lbl_evento.config(text=f"Suceso de hoy: {evento}")
        
        if evento == "Tráfico Común y Corriente":
            jugadores = random.randint(1500, 3500)
            ddos = 0
        elif evento == "🏆 ¡Gran Final del Torneo! (Mucho Tráfico)":
            jugadores = random.randint(7000, 11500)
            ddos = random.randint(500, 1500)
        else: # Ataque informático
            jugadores = random.randint(2000, 3500)
            ddos = random.randint(7500, 13000)
            
        # Cálculos de simulación
        limite_usuarios = self.obtener_limite_usuarios()
        capacidad_base = limite_usuarios
        
        if self.infraestructura["auto_scaling"] and (jugadores > capacidad_base * 0.8):
            capacidad_base += 4000
            self.creditos -= 100
            self.log("[SISTEMA] ¡Tráfico alto! Se activó la nube de reserva automáticamente (-$100 costo de mantenimiento).")
            
        if self.infraestructura["analizador_ia"] and ddos > 0:
            ddos = int(ddos * 0.5)
            self.log("[ESCUDO] Tu filtro de IA detectó el ataque hacker y neutralizó la mitad del tráfico falso.")
            
        carga_total = jugadores + ddos
        estres = min(100, int((carga_total / capacidad_base) * 100))
        
        # Calcular el Lag basándose en las mejoras
        latencia = 190 if not self.infraestructura["balanceo_geografico"] else 30
        if estres > 75:
            latencia += (estres - 75) * 5
        latencia = min(self.limite_ping, latencia)

        if jugadores > limite_usuarios:
            self.estabilidad_sistema -= 1
            self.log(f"[ALERTA] Excediste el límite de usuarios del nivel actual ({jugadores:,}/{limite_usuarios:,}).")

        if latencia >= 400:
            self.estabilidad_sistema -= 1
            self.log(f"[ALERTA] El ping ya está demasiado alto ({latencia}/500 ms).")

        if estres >= 95:
            self.estabilidad_sistema -= 2
            self.log("[ALERTA] Saturación crítica: el centro de datos perdió estabilidad.")
        elif estres >= 85:
            self.estabilidad_sistema -= 1

        self.estabilidad_sistema = max(0, self.estabilidad_sistema)
        if self.estabilidad_sistema <= 0:
            self.progress_estres["value"] = estres
            self.lbl_latencia.config(text=f"Lag (Ping): {latencia}/500 ms")
            self.lbl_jugadores.config(text=f"Jugadores Jugando: {jugadores:,} / {limite_usuarios:,}")
            self.actualizar_recomendaciones(evento, estres, latencia, ddos)
            self.historial_experimento.append({
                "Turno": self.turno_actual, "Evento": evento, "Jugadores": jugadores,
                "Trafico_DDoS_Filtrado": ddos, "Estres_Servidor_Porcentaje": estres,
                "Latencia_Ping_ms": latencia, "Creditos_Totales": self.creditos
            })
            self.terminar_partida(
                "Simulación Fallida",
                "La estabilidad del servidor llegó a 0. Perdiste la partida por saturación, latencia o exceso de usuarios.",
                es_victoria=False,
            )
            return
            
        # Balance Financiero
        if estres >= 95:
            self.log(f"[ALERTA] Los servidores colapsaron por saturación. Pérdida masiva de usuarios.")
            ganancias = int(jugadores * 0.05)
        else:
            bono = 1.3 if self.infraestructura["ruteo_partidas"] else 1.0
            ganancias = int(jugadores * 0.25 * bono)
            self.log(f"[ÉXITO] Turno superado de manera estable. Los servidores respondieron bien.")
            
        self.creditos += ganancias
        
        # Renderizar en la interfaz de usuario
        self.progress_estres["value"] = estres
        self.lbl_latencia.config(text=f"Lag (Ping): {latencia}/500 ms")
        self.lbl_jugadores.config(text=f"Jugadores Jugando: {jugadores:,} / {limite_usuarios:,}")
        
        # Indicador en rojo: qué mejora conviene comprar para el próximo turno
        self.actualizar_recomendaciones(evento, estres, latencia, ddos)
        
        # Registrar métricas bajo capó para el reporte académico .CSV
        self.historial_experimento.append({
            "Turno": self.turno_actual, "Evento": evento, "Jugadores": jugadores,
            "Trafico_DDoS_Filtrado": ddos, "Estres_Servidor_Porcentaje": estres, 
            "Latencia_Ping_ms": latencia, "Creditos_Totales": self.creditos
        })
        
        self.turno_actual += 1
        self.actualizar_interfaz_visual()
        
        if self.turno_actual > self.max_turnos:
            self.btn_turno.config(state="disabled", text="TORNEO COMPLETADO CON ÉXITO")
            self.terminar_partida(
                "Simulación Finalizada",
                f"¡Felicidades! Has manejado la infraestructura durante los 10 turnos.\n"
                "Los datos se han guardado en 'resultados_simulacion.csv' para tu reporte técnico.",
                es_victoria=True,
            )

    def reiniciar_juego(self):
        """Reinicia todas las variables del juego para empezar una nueva partida
        sin tener que cerrar y volver a abrir la aplicación."""
        self.turno_actual = 1
        self.creditos = 600
        self.estabilidad_sistema = 3
        self.partida_activa = True
        self.infraestructura = {
            "servidores_fisicos": 1,
            "auto_scaling": False,
            "balanceo_geografico": False,
            "analizador_ia": False,
            "ruteo_partidas": False
        }
        self.historial_experimento = []
        
        # Reiniciar visuales de estado
        self.lbl_evento.config(text="Evento: Preparando el torneo...")
        self.progress_estres["value"] = 0
        self.lbl_latencia.config(text="Lag (Ping): --/500 ms")
        self.lbl_jugadores.config(text="Jugadores Jugando: -- / --")
        self.lbl_limite_usuarios.config(text=f"Límite de Usuarios: {self.obtener_limite_usuarios():,}")
        self.lbl_estabilidad.config(text=f"Estabilidad: {self.estabilidad_sistema}/3")
        self.lbl_recomendacion.config(text="💡 Compra mejoras en la tienda y presiona 'Avanzar de Turno'.", fg="#f9e2af")
        
        # Limpiar la bitácora
        self.txt_logs.configure(state="normal")
        self.txt_logs.delete("1.0", tk.END)
        self.txt_logs.configure(state="disabled")
        
        # Reactivar los botones de la tienda
        self.btn_as.config(text="☁️ Servidores de Reserva / Nube ($1500)\n[Se activan solos si te vas a saturar]", state="normal", bg="#313244")
        self.btn_geo.config(text="🌍 Antenas Regionales ($2000)\n[Elimina por completo el lag de otros países]", state="normal", bg="#313244")
        self.btn_ia.config(text="🛡️ Escudo Anti-Hackers / DDoS ($2500)\n[Bloquea ataques de tráfico falso]", state="normal", bg="#313244")
        self.btn_rut.config(text="🏆 Servidores VIP de Torneos ($3000)\n[Evita que partidas competitivas colapsen]", state="normal", bg="#313244")
        
        # Restaurar botón de avanzar turno y ocultar el de reiniciar
        self.btn_reiniciar.pack_forget()
        self.btn_turno.config(state="normal", text="AVANZAR DE TURNO / VER QUÉ PASA >")
        self.btn_turno.pack(fill="x", padx=15, pady=10)
        
        self.actualizar_interfaz_visual()

    def exportar_datos_csv(self):
        if not self.historial_experimento:
            return
        with open('resultados_simulacion.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.historial_experimento[0].keys())
            writer.writeheader()
            writer.writerows(self.historial_experimento)
        self.log("[SISTEMA] Archivo Excel/CSV generado para la experimentación.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PingZeroGUI(root)
    root.mainloop()