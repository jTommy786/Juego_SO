import tkinter as tk
from tkinter import ttk, messagebox
import random
from configuracion import CONFIG_BALANCEO
from core.motor import MotorJuego

class InterfazJuego:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.withdraw()  
        
        # Configurar la ventana principal (raiz) como anclaje de la barra de tareas
        self.raiz.title("Ping Zero: Server Manager")
        self.raiz.geometry("1x1+0+0")
        self.raiz.attributes("-alpha", 0.0)
        
        self.ventana = tk.Toplevel(self.raiz)
        self.ventana.title("Ping Zero: Server Manager")
        self.ventana.configure(bg="#0c0d12")
        
        # Eliminar decoración nativa del SO
        self.ventana.overrideredirect(True)
        
        self.raiz.deiconify()  # Mapear raiz para mostrar el icono en la barra de tareas
        
        # Vincular eventos de mapeo de raiz para Alt+Tab
        self.raiz.bind("<Map>", self.al_mapear_raiz)
        self.raiz.bind("<Unmap>", self.al_desmapear_raiz)
        
        self.ventana.protocol("WM_DELETE_WINDOW", self.raiz.destroy)
        self.ventana.bind("<Destroy>", lambda e: self.raiz.destroy() if e.widget == self.ventana else None)
            
        self.motor = MotorJuego()
        
        # Paleta de Colores
        self.bg_dark = "#0c0d12"
        self.bg_card = "#161722"
        self.bg_panel = "#1d1f2d"
        self.fg_light = "#cdd6f4"
        self.fg_dim = "#7f849c"
        self.color_blue = "#89b4fa"
        self.color_green = "#a6e3a1"
        self.color_red = "#f38ba8"
        self.color_yellow = "#f9e2af"
        
        # Configuración de Maximizado y Geometría Normal
        self.is_maximized = False
        self.drag_data = {"x": 0, "y": 0}
        
        screen_w = self.ventana.winfo_screenwidth()
        screen_h = self.ventana.winfo_screenheight()
        normal_w = int(screen_w * 0.95)
        normal_h = int(screen_h * 0.92)
        x = (screen_w - normal_w) // 2
        y = (screen_h - normal_h) // 2
        self.normal_geometry = f"{normal_w}x{normal_h}+{x}+{y}"
        
        # Iniciar en tamaño normal de ventana por defecto (1100x700)
        self.ventana.geometry(self.normal_geometry)
        
        # Variables de acercar y navegación del mapa
        self.factor_zoom = 1.0
        self.selected_item = None
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("CPU.Horizontal.TProgressbar", troughcolor="#313244", background=self.color_blue, thickness=16)
        self.style.configure("RAM.Horizontal.TProgressbar", troughcolor="#313244", background=self.color_yellow, thickness=16)
        self.style.configure("Downtime.Horizontal.TProgressbar", troughcolor="#313244", background=self.color_red, thickness=16)
        
        # Estilos premium para Pestañas (ttk.Notebook)
        self.style.configure("TNotebook", background=self.bg_dark, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.bg_card, foreground=self.fg_light, borderwidth=1, padding=(10, 4))
        self.style.map("TNotebook.Tab", background=[("selected", self.bg_panel)], foreground=[("selected", self.color_blue)])
        
        self.configurar_interfaz()
        self.actualizar_interfaz()
        self.ventana.after(150, self.centrar_camara)
        self.bucle_tick()

    # --- Lógica de la Barra de Título Customizada ---
    def iniciar_arrastre(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def arrastrar_ventana(self, event):
        if not self.is_maximized:
            x = self.ventana.winfo_x() - self.drag_data["x"] + event.x
            y = self.ventana.winfo_y() - self.drag_data["y"] + event.y
            self.ventana.geometry(f"+{x}+{y}")

    def minimizar_ventana(self):
        self.raiz.iconify()

    def alternar_maximizar(self):
        if self.is_maximized:
            self.ventana.geometry(self.normal_geometry)
            self.is_maximized = False
        else:
            self.normal_geometry = self.ventana.geometry()
            screen_w = self.ventana.winfo_screenwidth()
            screen_h = self.ventana.winfo_screenheight()
            self.ventana.geometry(f"{screen_w}x{screen_h}+0+0")
            self.is_maximized = True

    def al_mapear_raiz(self, event):
        if event.widget == self.raiz:
            self.ventana.deiconify()
            self.ventana.lift()

    def al_desmapear_raiz(self, event):
        if event.widget == self.raiz:
            self.ventana.withdraw()

    # --- Construcción de la UI ---
    def configurar_interfaz(self):
        # 0. Custom Title Bar simplificada
        self.title_bar = tk.Frame(self.ventana, bg=self.bg_panel, height=56)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)
        
        self.title_bar.bind("<ButtonPress-1>", self.iniciar_arrastre)
        self.title_bar.bind("<B1-Motion>", self.arrastrar_ventana)
        
        title_label = tk.Label(self.title_bar, text=" ⚙️ PING ZERO: Server Manager", font=("Helvetica", 9, "bold"), fg=self.color_blue, bg=self.bg_panel)
        title_label.pack(side="left", padx=20)
        title_label.bind("<ButtonPress-1>", self.iniciar_arrastre)
        title_label.bind("<B1-Motion>", self.arrastrar_ventana)
        
        btn_style = {"font": ("Helvetica", 9, "bold"), "bg": self.bg_panel, "fg": self.fg_light, "relief": "flat", "width": 4, "height": 1}
        
        self.btn_close = tk.Button(self.title_bar, text="X", command=self.raiz.destroy, **btn_style)
        self.btn_close.pack(side="right", padx=(2, 10))
        self.btn_close.bind("<Enter>", lambda e: self.btn_close.config(bg=self.color_red, fg="#11111b"))
        self.btn_close.bind("<Leave>", lambda e: self.btn_close.config(bg=self.bg_panel, fg=self.fg_light))

        self.btn_max = tk.Button(self.title_bar, text="□", command=self.alternar_maximizar, **btn_style)
        self.btn_max.pack(side="right", padx=2)
        self.btn_max.bind("<Enter>", lambda e: self.btn_max.config(bg=self.bg_card))
        self.btn_max.bind("<Leave>", lambda e: self.btn_max.config(bg=self.bg_panel))

        self.btn_min = tk.Button(self.title_bar, text="_", command=self.minimizar_ventana, **btn_style)
        self.btn_min.pack(side="right", padx=2)
        self.btn_min.bind("<Enter>", lambda e: self.btn_min.config(bg=self.bg_card))
        self.btn_min.bind("<Leave>", lambda e: self.btn_min.config(bg=self.bg_panel))

        # 1. Header Frame
        header = tk.Frame(self.ventana, bg=self.bg_panel, height=64)
        header.pack(fill="x", side="top")
        
        self.lbl_time = tk.Label(header, text="📅 DIA: 1 [PLANIFICACION]", font=("Helvetica", 11, "bold"), fg=self.color_yellow, bg=self.bg_panel)
        self.lbl_time.pack(side="left", padx=(20, 12), pady=11)
        
        self.lbl_forecast = tk.Label(header, text="📈 PRONOSTICO: Carga normal", font=("Helvetica", 11, "bold"), fg=self.color_blue, bg=self.bg_panel)
        self.lbl_forecast.pack(side="left", padx=12, pady=11)
        
        self.lbl_autoscale_banner = tk.Label(header, text="AUTO-SCALING: INACTIVO", font=("Helvetica", 10, "bold"), fg=self.fg_dim, bg=self.bg_panel)
        self.lbl_autoscale_banner.pack(side="right", padx=20, pady=11)

        # 2. Contenedor Principal (2 Columnas)
        main_container = tk.Frame(self.ventana, bg=self.bg_dark)
        main_container.pack(fill="both", expand=True, padx=15, pady=5)

        # Columna Izquierda (Área de Trabajo - 70% del ancho)
        left_col = tk.Frame(main_container, bg=self.bg_dark)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Columna Derecha (Panel de Control Fijo - 30% del ancho)
        right_col = tk.Frame(main_container, bg=self.bg_dark, width=420)
        right_col.pack(side="right", fill="both")
        right_col.pack_propagate(False)

        # --- Elementos de la Columna Izquierda ---

        # 2.1 Dashboard Superior (Métricas)
        dashboard = tk.Frame(left_col, bg=self.bg_dark)
        dashboard.pack(fill="x", pady=(0, 5))
        
        self.cards = {}
        metrics = [
            ("creditos", "PRESUPUESTO", self.color_green, "$3,000.00"),
            ("trafico", "TRAFICO TOTAL", self.color_blue, "0 req/s"),
            ("latencia", "PING PROMEDIO", self.color_green, "0 ms"),
            ("ceo", "APROBACION CEO", self.color_green, "100%"),
            ("room", "DATA CENTERS", self.color_yellow, "1/9 Salas")
        ]
        
        for clave, title, color, valor in metrics:
            card = tk.Frame(dashboard, bg=self.bg_card, bd=0)
            card.pack(side="left", expand=True, fill="both", padx=3, pady=2)
            lbl = tk.Label(card, text=title, font=("Helvetica", 7, "bold"), fg=self.fg_dim, bg=self.bg_card)
            lbl.pack(pady=(4, 1))
            v_lbl = tk.Label(card, text=valor, font=("Helvetica", 11, "bold"), fg=color, bg=self.bg_card)
            v_lbl.pack(pady=(0, 4))
            self.cards[clave] = v_lbl

        # 2.2 Panel de Estrés CPU / RAM
        resource_frame = tk.Frame(left_col, bg=self.bg_panel, bd=0)
        resource_frame.pack(fill="x", pady=5)
        
        self.lbl_cpu_text = tk.Label(resource_frame, text="CONSUMO CPU: 0.0%", font=("Helvetica", 8, "bold"), fg=self.fg_light, bg=self.bg_panel)
        self.lbl_cpu_text.pack(anchor="w", padx=10, pady=(2, 0))
        self.progress_cpu = ttk.Progressbar(resource_frame, style="CPU.Horizontal.TProgressbar", orient="horizontal", mode="determinate")
        self.progress_cpu.pack(fill="x", padx=10, pady=(1, 4))
 
        self.lbl_ram_text = tk.Label(resource_frame, text="CONSUMO RAM: 0.0%", font=("Helvetica", 8, "bold"), fg=self.fg_light, bg=self.bg_panel)
        self.lbl_ram_text.pack(anchor="w", padx=10, pady=(1, 0))
        self.progress_ram = ttk.Progressbar(resource_frame, style="RAM.Horizontal.TProgressbar", orient="horizontal", mode="determinate")
        self.progress_ram.pack(fill="x", padx=10, pady=(1, 5))

        # 2.3 Canvas de Red
        self.canvas_lf = tk.Frame(left_col, bg=self.bg_dark, bd=0)
        self.canvas_lf.pack(fill="both", expand=True, pady=(5, 0))
        
        self.canvas = tk.Canvas(self.canvas_lf, bg="#08080f", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=0, pady=0)

        # Configurar limites del Canvas
        self.canvas.config(scrollregion=(-800, -800, 800, 800))
        
        # Binds de Paneo (arrastre de mapa con clic derecho y central)
        self.canvas.bind("<ButtonPress-3>", self.iniciar_paneo)
        self.canvas.bind("<B3-Motion>", self.mover_paneo)
        self.canvas.bind("<ButtonPress-2>", self.iniciar_paneo)
        self.canvas.bind("<B2-Motion>", self.mover_paneo)
        
        # Binds de Zoom
        self.canvas.bind("<MouseWheel>", self.acercar)
        self.canvas.bind("<Button-4>", self.acercar)
        self.canvas.bind("<Button-5>", self.acercar)
        
        # Deselección al hacer clic en el fondo del canvas
        self.canvas.bind("<Button-1>", self.al_click_fondo_canvas)
        
        # HUD de Alertas Fijo (sobre el Canvas con coordenadas relativas)
        self.lbl_hud_alert = tk.Label(self.canvas_lf, text="Consola SysAdmin Lista.", font=("Helvetica", 9, "bold"),
                                      fg=self.color_blue, bg="#0c0d12", bd=0, relief="flat", padx=15, pady=8, wraplength=450)
        self.lbl_hud_alert.place(relx=0.5, y=20, anchor="n")

        # --- Elementos de la Columna Derecha ---

        # 3.1 Botón de Acción Principal (Iniciar Jornada)
        self.btn_start_shift = tk.Button(right_col, text="▶️ INICIAR JORNADA", font=("Helvetica", 14, "bold"),
                                         bg=self.color_green, fg="#11111b", height=3, width=25, relief="flat", command=self.iniciar_turno_click)
        self.btn_start_shift.pack(fill="x", padx=15, pady=15)

        # 3.3 Telemetría en Vivo (Abajo de la Columna Derecha)
        log_lf = tk.Frame(right_col, bg=self.bg_dark, bd=0, height=220)
        log_lf.pack(side="bottom", fill="x", expand=False)
        log_lf.pack_propagate(False)
        
        self.txt_logs = tk.Text(log_lf, bg="#0d0e15", fg=self.color_blue, font=("Consolas", 10), bd=0, state="disabled")
        self.txt_logs.pack(fill="both", expand=True, padx=5, pady=(0, 4))

        # 3.2 Sistema de Pestañas (ttk.Notebook)
        self.tab_control = ttk.Notebook(right_col)
        self.tab_control.pack(side="top", fill="both", expand=True, pady=(0, 10))

        tab_inspect = tk.Frame(self.tab_control, bg=self.bg_dark)
        tab_shop = tk.Frame(self.tab_control, bg=self.bg_dark)

        self.tab_control.add(tab_inspect, text="🛠️ Inspección")
        self.tab_control.add(tab_shop, text="🛒 Mercado Global")

        # Pestaña 1: Inspección
        self.inspection_lf = tk.Frame(tab_inspect, bg=self.bg_dark)
        self.inspection_lf.pack(fill="both", expand=True)
        
        self.inspection_content = tk.Frame(self.inspection_lf, bg=self.bg_dark)
        self.inspection_content.pack(fill="both", expand=True, padx=12, pady=12)

        # Pestaña 2: Mercado Global
        shop_container = tk.Frame(tab_shop, bg=self.bg_dark)
        shop_container.pack(fill="both", expand=True, padx=5, pady=5)

        self.buttons = {}
        upgrades = [
            ("autoscale", "☁️ Licencia Cloud ($2500)\nAuto-Scaling para mitigar picos de carga."),
            ("geo", "🌍 Router Geo DNS ($5000)\nElimina la penalización de overflow por ruteo."),
            ("ia", "🛡️ Escudo Antivirus ($7500)\nFiltro inteligente que reduce ataques DDoS."),
            ("party", "🏆 Ruteo Partidas ($10000)\nReduce la carga de CPU global en un 25%.")
        ]

        for clave, text in upgrades:
            btn = tk.Button(shop_container, text=text, font=("Helvetica", 16, "bold"), relief="flat", height=2,
                            bg=self.bg_card, fg=self.fg_light, activebackground=self.color_blue, justify="left", anchor="w", padx=8,
                            command=lambda k=clave: self.comprar_mejora_click(k))
            btn.pack(side="top", fill="x", pady=3)
            self.buttons[clave] = btn



    # --- Logs ---
    def registrar_mensaje(self, mensaje, is_alert=False):
        self.txt_logs.configure(state="normal")
        self.txt_logs.insert(tk.END, f"{'[ALERT] ' if is_alert else '[INFO] '}{mensaje}\n")
        self.txt_logs.see(tk.END)
        self.txt_logs.configure(state="disabled")



    # --- Lógica de Paneo y Zoom ---
    def centrar_camara(self):
        self.canvas.update_idletasks()
        width = self.canvas.winfo_width() or 900
        height = self.canvas.winfo_height() or 450
        
        try:
            scroll_region = self.canvas.cget("scrollregion")
            x1, y1, x2, y2 = map(float, scroll_region.split())
        except Exception:
            x1, y1, x2, y2 = -800.0, -800.0, 800.0, 800.0
            
        w_total = x2 - x1
        h_total = y2 - y1
        
        target_x = 0.0 * self.factor_zoom
        target_y = -200.0 * self.factor_zoom
        
        frac_x = ((target_x - width / 2.0) - x1) / w_total
        frac_y = ((target_y - height / 2.0) - y1) / h_total
        
        frac_x = max(0.0, min(1.0, frac_x))
        frac_y = max(0.0, min(1.0, frac_y))
        
        self.canvas.xview_moveto(frac_x)
        self.canvas.yview_moveto(frac_y)

    def iniciar_paneo(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def mover_paneo(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def acercar(self, event):
        mx = self.canvas.canvasx(event.x)
        my = self.canvas.canvasy(event.y)
        
        factor = 1.1 if (event.delta > 0 or event.num == 4) else 0.9
        new_zoom = self.factor_zoom * factor
        
        if 0.5 <= new_zoom <= 3.0:
            self.factor_zoom = new_zoom
            self.actualizar_interfaz()
            
            # Paneo reactivo respecto a (0, 0)
            dx = mx * (factor - 1)
            dy = my * (factor - 1)
            self.canvas.scan_mark(0, 0)
            self.canvas.scan_dragto(int(-dx), int(-dy), gain=1)

    def al_click_fondo_canvas(self, event):
        if not self.canvas.find_withtag("current"):
            self.limpiar_seleccion()

    # --- Clics en Nodos (Retornar "break" para evitar paneo accidental) ---
    def al_click_wan(self, event):
        self.seleccionar_elemento("wan")
        return "break"

    def al_click_continente(self, event, continente):
        self.seleccionar_elemento("continente", continente=continente)
        return "break"

    def al_click_centro_datos(self, event, ciudad):
        self.seleccionar_elemento("dc_open", region=ciudad)
        return "break"

    def al_click_servidor(self, event, ciudad, idx):
        self.seleccionar_elemento("server", region=ciudad, index=idx)
        return "break"

    # --- Lógica de Panel de Inspección Fijo ---
    def seleccionar_elemento(self, item_type, **kwargs):
        self.selected_item = {"type": item_type, "kwargs": kwargs}
        self.actualizar_panel_inspeccion()

    def limpiar_seleccion(self):
        self.selected_item = None
        self.actualizar_panel_inspeccion()

    def actualizar_panel_inspeccion(self):
        for widget in self.inspection_content.winfo_children():
            widget.destroy()

        if self.selected_item is None:
            lbl = tk.Label(self.inspection_content, text="1. Haz clic en un Nodo para administrarlo.\n2. Compra enlaces e infraestructuras en el Canvas.\n3. Haz clic en Iniciar Jornada.",
                           font=("Helvetica", 12, "bold"), fg=self.fg_dim, bg=self.bg_dark, justify="center", wraplength=350)
            lbl.pack(expand=True, fill="both", pady=20)
            return

        item_type = self.selected_item["type"]
        kwargs = self.selected_item["kwargs"]
        is_active = self.motor.jornada_activa

        if item_type == "wan":
            lbl_title = tk.Label(self.inspection_content, text="🌐 INTERNET GLOBAL (WAN)",
                                 font=("Helvetica", 14, "bold"), fg=self.color_blue, bg=self.bg_dark)
            lbl_title.pack(anchor="w", pady=(2, 8))
            
            lbl_desc = tk.Label(self.inspection_content, text="Administra enlaces de red internacionales. Compra fibra transoceánica para conectar nuevos mercados continentales.",
                                font=("Helvetica", 12), fg=self.fg_light, bg=self.bg_dark, justify="left", wraplength=360)
            lbl_desc.pack(anchor="w", pady=(0, 12))
            
            continents_list = ["América", "Europa", "Asia"]
            for cont in continents_list:
                is_purchased = cont in self.motor.continentes_comprados
                is_unlocked = self.motor.is_continent_unlocked(cont)
                
                # Marco para cada continente
                frame_cont = tk.Frame(self.inspection_content, bg=self.bg_card, padx=10, pady=6)
                frame_cont.pack(fill="x", pady=3)
                
                lbl_name = tk.Label(frame_cont, text=cont.upper(), font=("Helvetica", 12, "bold"), fg=self.fg_light, bg=self.bg_card)
                lbl_name.pack(side="left")
                
                if is_purchased:
                    lbl_status = tk.Label(frame_cont, text="✅ CONECTADO", font=("Helvetica", 12, "bold"), fg=self.color_green, bg=self.bg_card)
                    lbl_status.pack(side="right")
                else:
                    if is_unlocked:
                        cost_cont = CONFIG_BALANCEO["CONTINENT_UNLOCK_COST"]
                        btn_buy = tk.Button(frame_cont, text=f"Conectar | ${cost_cont:.0f}", font=("Helvetica", 11, "bold"),
                                            bg=self.color_blue, fg="#11111b", relief="flat", padx=8,
                                            state="disabled" if (is_active or self.motor.creditos < cost_cont) else "normal",
                                            command=lambda c=cont: self.comprar_continente_accion(c))
                        btn_buy.pack(side="right")
                    else:
                        unlock_day = 5 if cont == "Europa" else 10
                        lbl_status = tk.Label(frame_cont, text=f"🔒 Día {unlock_day}", font=("Helvetica", 11, "bold"), fg=self.fg_dim, bg=self.bg_card)
                        lbl_status.pack(side="right")

        elif item_type == "continente":
            continente = kwargs["continente"]
            lbl_title = tk.Label(self.inspection_content, text=f"🌐 REGION: {continente.upper()}",
                                 font=("Helvetica", 14, "bold"), fg=self.color_blue, bg=self.bg_dark)
            lbl_title.pack(anchor="w", pady=(2, 8))
            
            lbl_desc = tk.Label(self.inspection_content, text=f"Inaugura Data Centers en las ciudades de {continente} para enrutar el tráfico local de esta región.",
                                font=("Helvetica", 12), fg=self.fg_light, bg=self.bg_dark, justify="left", wraplength=360)
            lbl_desc.pack(anchor="w", pady=(0, 12))
            
            cities = CONFIG_BALANCEO["LOCATIONS"][continente]
            costo = CONFIG_BALANCEO["OPEN_DATACENTER_COST"]
            for ciudad in cities:
                is_open = ciudad in self.motor.centros_datos
                
                frame_city = tk.Frame(self.inspection_content, bg=self.bg_card, padx=10, pady=6)
                frame_city.pack(fill="x", pady=3)
                
                lbl_city = tk.Label(frame_city, text=ciudad, font=("Helvetica", 12, "bold"), fg=self.fg_light, bg=self.bg_card)
                lbl_city.pack(side="left")
                
                if is_open:
                    lbl_status = tk.Label(frame_city, text="✅ ACTIVO", font=("Helvetica", 12, "bold"), fg=self.color_green, bg=self.bg_card)
                    lbl_status.pack(side="right")
                else:
                    btn_buy = tk.Button(frame_city, text=f"Abrir DC | ${costo:.0f}", font=("Helvetica", 11, "bold"),
                                        bg=self.color_blue, fg="#11111b", relief="flat", padx=8,
                                        state="disabled" if (is_active or self.motor.creditos < costo) else "normal",
                                        command=lambda r=ciudad: self.abrir_centro_datos_accion(r))
                    btn_buy.pack(side="right")

        elif item_type == "dc_open":
            region = kwargs["region"]
            dc = self.motor.centros_datos[region]
            
            lbl_title = tk.Label(self.inspection_content, text=f"🏢 DC: {region.upper()}",
                                 font=("Helvetica", 14, "bold"), fg=self.color_blue, bg=self.bg_dark)
            lbl_title.pack(anchor="w", pady=(2, 6))
            
            desc_text = (
                f"Data Center regional ubicado en {region}.\n"
                f"Procesa el tráfico de la red local para mejorar los tiempos de respuesta.\n\n"
                f"• Servidores Instalados: {dc.get('servers_count', 0)}\n"
                f"• Carga CPU: {dc.get('estres_cpu', 0.0):.1f}%\n"
                f"• Carga RAM: {dc.get('estres_ram', 0.0):.1f}%"
            )
            lbl_desc = tk.Label(self.inspection_content, text=desc_text,
                                font=("Helvetica", 12), fg=self.fg_light, bg=self.bg_dark, justify="left", wraplength=360)
            lbl_desc.pack(anchor="w", pady=(2, 12))
            
            cost_srv = CONFIG_BALANCEO["UPGRADE_SERVER_COST"]
            srv_state = "normal" if (not is_active and self.motor.creditos >= cost_srv) else "disabled"
            btn_srv = tk.Button(self.inspection_content, text=f"🚀 Instalar Servidor | ${cost_srv:.0f}",
                                font=("Helvetica", 11, "bold"), bg=self.bg_card, fg=self.fg_light, state=srv_state,
                                relief="flat", command=lambda: self.comprar_servidor_accion(region))
            btn_srv.pack(fill="x", pady=2)

        # Botón de salir del panel
        btn_close = tk.Button(self.inspection_content, text="✖ Cerrar Panel / Cancelar", font=("Helvetica", 12, "bold"),
                      bg=self.bg_card, fg=self.color_red, relief="flat", command=self.limpiar_seleccion)
        btn_close.pack(fill="x", pady=(12, 2))

    # --- Acciones del Panel ---
    def comprar_continente_accion(self, continente):
        if self.motor.comprar_continente(continente):
            self.registrar_mensaje(self.motor.ultimo_mensaje_evento, False)
            self.seleccionar_elemento("continente", continente=continente)
        else:
            self.registrar_mensaje(self.motor.ultimo_mensaje_evento, True)
        self.actualizar_interfaz()

    def abrir_centro_datos_accion(self, region):
        if self.motor.abrir_centro_datos(region):
            self.registrar_mensaje(self.motor.ultimo_mensaje_evento, False)
            self.seleccionar_elemento("dc_open", region=region)
        else:
            self.registrar_mensaje(self.motor.ultimo_mensaje_evento, True)
        self.actualizar_interfaz()

    def comprar_servidor_accion(self, region):
        if self.motor.comprar_servidor(region):
            self.registrar_mensaje(self.motor.ultimo_mensaje_evento, False)
            self.seleccionar_elemento("dc_open", region=region)
        else:
            self.registrar_mensaje(self.motor.ultimo_mensaje_evento, True)
        self.actualizar_interfaz()

    # --- Compras de Tienda ---
    def comprar_mejora_click(self, clave):
        engine_key = "auto_scale" if clave == "autoscale" else ("ia_analyzer" if clave == "ia" else clave)
        if clave in ["autoscale", "ia"] and getattr(self.motor, f"{engine_key}_purchased"):
            getattr(self.motor, f"toggle_{clave if clave == 'autoscale' else 'ia_analyzer'}")()
        else:
            if self.motor.comprar_mejora(clave):
                self.registrar_mensaje(self.motor.ultimo_mensaje_evento, False)
            else:
                self.registrar_mensaje(f"🚨 Fondos insuficientes o jornada activa para comprar mejora: {clave}.", True)
        self.actualizar_interfaz()

    def iniciar_turno_click(self):
        if self.motor.iniciar_jornada():
            self.registrar_mensaje(self.motor.ultimo_mensaje_evento)
            self.actualizar_interfaz()

    def dibujar_mapa_nodos(self):
        self.canvas.delete("all")
        
        # Dimensiones del canvas base
        width = self.canvas.winfo_width() or 900
        height = self.canvas.winfo_height() or 450
        base_w = max(900, width)
        base_h = max(450, height)
        
        # Coordenadas relativas centradas en (0, 0)
        # 1. Dibujar Internet Global (Core / WAN - Nivel 1)
        internet_x = 0
        internet_y = -200.0
        internet_radius = 20
        tag_id_wan = "wan_click"
        
        # Círculo de la WAN
        wan_oval_id = self.canvas.create_oval(internet_x - internet_radius, internet_y - internet_radius,
                                internet_x + internet_radius, internet_y + internet_radius,
                                fill="#89b4fa", outline="#ffffff", width=2, tags=tag_id_wan)
        self.canvas.create_text(internet_x, internet_y, text="WAN", font=("Helvetica", 12, "bold"), fill="#11111b", tags=(tag_id_wan, "text", "size_8"))
        
        # Enlazar clic y hover para la WAN
        self.canvas.tag_bind(tag_id_wan, "<Button-1>", self.al_click_wan)
        self.canvas.tag_bind(tag_id_wan, "<Enter>", lambda event: self.canvas.itemconfigure(wan_oval_id, outline="#f9e2af", width=4))
        self.canvas.tag_bind(tag_id_wan, "<Leave>", lambda event: self.canvas.itemconfigure(wan_oval_id, outline="#ffffff", width=2))

        # Coordenadas de los 3 Continentes (Nivel 2)
        cont_y = -110.0
        cont_radius = 22
        continents = {
            "América": -250.0,
            "Europa": 0.0,
            "Asia": 250.0
        }
        
        # Coordenadas de las 9 Ciudades (Sub-regiones - Nivel 3)
        city_y = -20.0
        city_radius = 16
        city_coords = {
            "Miami": (-330.0, city_y),
            "Bogotá": (-250.0, city_y),
            "São Paulo": (-170.0, city_y),
            "Madrid": (-80.0, city_y),
            "Frankfurt": (0.0, city_y),
            "Londres": (80.0, city_y),
            "Tokio": (170.0, city_y),
            "Seúl": (250.0, city_y),
            "Singapur": (330.0, city_y)
        }
        
        # 2. Dibujar Continentes y Conexiones a Internet
        for cont, cont_x in continents.items():
            # Solo dibujar si el continente ha sido comprado/activado
            if cont not in self.motor.continentes_comprados:
                continue
                
            cont_cities = CONFIG_BALANCEO["LOCATIONS"][cont]
            cont_open = any(c in self.motor.centros_datos for c in cont_cities)
            line_color = "#a6e3a1" if cont_open else "#89b4fa"
            
            # Conexión WAN -> Continente
            self.canvas.create_line(internet_x, internet_y + internet_radius, cont_x, cont_y - cont_radius, fill=line_color, width=2)
            
            tag_id_cont = f"cont_click_{cont}"
            # Círculo de Continente
            cont_oval_id = self.canvas.create_oval(cont_x - cont_radius, cont_y - cont_radius, cont_x + cont_radius, cont_y + cont_radius,
                                    fill="#1e1e2e", outline=line_color, width=2, tags=tag_id_cont)
            self.canvas.create_text(cont_x, cont_y, text=cont.upper(), font=("Helvetica", 11, "bold"), fill=self.fg_light, tags=(tag_id_cont, "text", "size_7"))
            
            # Enlazar clic y hover para el Continente
            self.canvas.tag_bind(tag_id_cont, "<Button-1>", lambda event, c=cont: self.al_click_continente(event, c))
            self.canvas.tag_bind(tag_id_cont, "<Enter>", lambda event, oid=cont_oval_id, oc=line_color: self.canvas.itemconfigure(oid, outline="#ffffff", width=4))
            self.canvas.tag_bind(tag_id_cont, "<Leave>", lambda event, oid=cont_oval_id, oc=line_color: self.canvas.itemconfigure(oid, outline=oc, width=2))

            # Conexiones Continente -> Ciudades
            for ciudad in cont_cities:
                # Solo dibujar la ciudad si el Data Center está abierto
                if ciudad not in self.motor.centros_datos:
                    continue
                    
                cx, cy = city_coords[ciudad]
                city_line_color = "#a6e3a1"
                
                # Línea desde el continente a la ciudad
                self.canvas.create_line(cont_x, cont_y + cont_radius, cx, cy - city_radius, fill=city_line_color, width=1.5)
                
                tag_id_dc = f"dc_click_{ciudad}"
                
                dc = self.motor.centros_datos[ciudad]
                dc_color = "#1e1e2e"
                border_color = "#a6e3a1"
                text_color = self.fg_light
                ping = int(self.motor.pings_regionales.get(ciudad, 20.0))
                dc_text = f"{ciudad}\nServidores: {dc.get('servers_count', 0)}\n{ping} ms"
                
                # Círculo de la Ciudad
                dc_oval_id = self.canvas.create_oval(cx - city_radius, cy - city_radius, cx + city_radius, cy + city_radius,
                                                     fill=dc_color, outline=border_color, width=2, tags=tag_id_dc)
                self.canvas.create_text(cx, cy, text=dc_text, font=("Helvetica", 10, "bold"), fill=text_color, justify="center", tags=(tag_id_dc, "text", "size_6"))
                
                # Enlazar clic y hover para el Data Center
                self.canvas.tag_bind(tag_id_dc, "<Button-1>", lambda event, c=ciudad: self.al_click_centro_datos(event, c))
                self.canvas.tag_bind(tag_id_dc, "<Enter>", lambda event, oid=dc_oval_id: self.canvas.itemconfigure(oid, outline="#ffffff", width=4))
                self.canvas.tag_bind(tag_id_dc, "<Leave>", lambda event, oid=dc_oval_id, oc=border_color: self.canvas.itemconfigure(oid, outline=oc, width=2))

        # 4. Dibujar DDoS (Hacia la ciudad atacada)
        if self.motor.trafico_ddos > 0:
            target_city = getattr(self.motor, "region_ddos", "Miami")
            if target_city in self.motor.centros_datos:
                tx, ty = city_coords.get(target_city, (0.0, city_y))
                for _ in range(5):
                    t = random.uniform(0.1, 0.9)
                    px = internet_x + t * (tx - internet_x) + random.uniform(-15, 15)
                    py = internet_y + t * (ty - internet_y) + random.uniform(-15, 15)
                    self.canvas.create_oval(px - 3, py - 3, px + 3, py + 3, fill="#11111b", outline=self.color_red, tags="ddos")

        # 5. Escalar todo el mapa respecto a (0, 0)
        self.canvas.scale("all", 0, 0, self.factor_zoom, self.factor_zoom)
        
        # Ajustar dinámicamente las fuentes del canvas
        for text_id in self.canvas.find_withtag("text"):
            tags = self.canvas.gettags(text_id)
            base_size = 8
            for tag in tags:
                if tag.startswith("size_"):
                    base_size = int(tag.split("_")[1])
                    break
            
            new_size = max(4, int(base_size * self.factor_zoom))
            font_style = "bold"
            if "style_italic" in tags:
                font_style = "italic"
            self.canvas.itemconfigure(text_id, font=("Helvetica", new_size, font_style))

    # --- Actualización y Redibujado general ---
    def actualizar_interfaz(self):
        is_active = self.motor.jornada_activa
        
        # 1. Actualizar barra superior (Día / Estado / Pronóstico)
        if is_active:
            self.lbl_time.config(text=f"📅 DIA {self.motor.dias_transcurridos} [OPERACIONES]", fg=self.color_red)
            self.btn_start_shift.config(text=f"⏳ JORNADA EN CURSO... ({self.motor.temporizador_jornada}s)", state="disabled", bg=self.color_red, fg="#45475a", disabledforeground="#45475a")
        else:
            self.lbl_time.config(text=f"📅 DIA {self.motor.dias_transcurridos + 1} [PLANIFICACION]", fg=self.color_yellow)
            self.btn_start_shift.config(text="▶️ INICIAR JORNADA", state="normal", bg=self.color_green, fg="#11111b")
            
        self.lbl_forecast.config(text=self.motor.obtener_texto_pronostico())
        
        # 2. Métricas Dashboard
        self.cards["creditos"].config(text=f"${self.motor.creditos:,.2f}")
        self.cards["trafico"].config(text=f"{self.motor.usuarios_trafico + self.motor.trafico_ddos} req/s")
        self.cards["latencia"].config(text=f"{self.motor.latencia:.1f} ms")
        self.cards["ceo"].config(text=f"{self.motor.ceo_approval:.0f}%")
        
        total_srv = sum(dc.get("servers_count", 0) for dc in self.motor.centros_datos.values())
        self.cards["room"].config(text=f"{len(self.motor.centros_datos)}/9 DCs | {total_srv} Servs")
        
        # Latencia color
        if self.motor.latencia > 100.0:
            self.cards["latencia"].config(fg=self.color_red)
        elif self.motor.latencia > 60.0:
            self.cards["latencia"].config(fg=self.color_yellow)
        else:
            self.cards["latencia"].config(fg=self.color_green)
            
        # Aprobación CEO color
        if self.motor.ceo_approval < 40.0:
            self.cards["ceo"].config(fg=self.color_red)
        elif self.motor.ceo_approval < 75.0:
            self.cards["ceo"].config(fg=self.color_yellow)
        else:
            self.cards["ceo"].config(fg=self.color_green)
            
        # 4. Progressbars de Estrés
        if self.motor.is_downtime:
            self.lbl_cpu_text.config(text=f"ESTRES CPU: COLA DE CAIDA ({self.motor.estres_cpu:.1f}%)", fg=self.color_red)
            self.lbl_ram_text.config(text=f"ESTRES RAM: OVERFLOW MEMORIA ({self.motor.estres_ram:.1f}%)", fg=self.color_red)
            self.progress_cpu.config(style="Downtime.Horizontal.TProgressbar")
            self.progress_ram.config(style="Downtime.Horizontal.TProgressbar")
        else:
            self.lbl_cpu_text.config(text=f"CONSUMO CPU: {self.motor.estres_cpu:.1f}%", fg=self.fg_light)
            self.lbl_ram_text.config(text=f"CONSUMO RAM: {self.motor.estres_ram:.1f}%", fg=self.fg_light)
            self.progress_cpu.config(style="CPU.Horizontal.TProgressbar")
            self.progress_ram.config(style="RAM.Horizontal.TProgressbar")
            
        self.progress_cpu["value"] = self.motor.estres_cpu
        self.progress_ram["value"] = self.motor.estres_ram
        
        # Banner Auto-scale
        if self.motor.auto_scale_purchased:
            if self.motor.auto_scale_enabled:
                if self.motor.is_autoscale_running:
                    self.lbl_autoscale_banner.config(text="AUTO-SCALING: RUNNING (LOAD > 80%)", fg=self.color_green)
                else:
                    self.lbl_autoscale_banner.config(text="AUTO-SCALING: STANDBY (LOAD OK)", fg=self.color_yellow)
            else:
                self.lbl_autoscale_banner.config(text="AUTO-SCALING: APAGADO", fg=self.fg_dim)
        else:
            self.lbl_autoscale_banner.config(text="AUTO-SCALING: INACTIVO", fg=self.fg_dim)
            
        # 5. Botones de tienda (Los de servidor y datacenter ya se manejan desde el canvas)
            
        if self.motor.auto_scale_purchased:
            if self.motor.auto_scale_enabled:
                self.buttons["autoscale"].config(text="☁️ Licencia Cloud [ON] | -$5/t\nAuto-Scaling activo por carga.", state="normal", bg=self.color_green, fg="#11111b")
            else:
                self.buttons["autoscale"].config(text="☁️ Licencia Cloud [OFF] | -$0/t\nAuto-Scaling inactivo.", state="normal", bg=self.bg_card, fg=self.fg_light)
        elif self.motor.creditos < CONFIG_BALANCEO["UPGRADE_AUTOSCALE_COST"]:
            self.buttons["autoscale"].config(text=f"☁️ Compra Licencia Cloud | ${CONFIG_BALANCEO['UPGRADE_AUTOSCALE_COST']:.0f}\nHabilita el escalado automático.", state="disabled", bg=self.bg_card, fg=self.fg_dim)
        else:
            self.buttons["autoscale"].config(text=f"☁️ Compra Licencia Cloud | ${CONFIG_BALANCEO['UPGRADE_AUTOSCALE_COST']:.0f}\nHabilita el escalado automático.", state="normal", bg=self.bg_card, fg=self.fg_light)
            
        if self.motor.geo_balancer_active:
            self.buttons["geo"].config(text="🌍 Router Geo DNS [ACTIVO]\nElimina penalización por overflow.", state="disabled", bg="#313244", fg=self.fg_dim)
        elif is_active or self.motor.creditos < CONFIG_BALANCEO["UPGRADE_GEO_BALANCER_COST"]:
            self.buttons["geo"].config(text=f"🌍 Compra Router Geo DNS | ${CONFIG_BALANCEO['UPGRADE_GEO_BALANCER_COST']:.0f}\nEnruta clientes a la ciudad más cercana.", state="disabled", bg=self.bg_card, fg=self.fg_dim)
        else:
            self.buttons["geo"].config(text=f"🌍 Compra Router Geo DNS | ${CONFIG_BALANCEO['UPGRADE_GEO_BALANCER_COST']:.0f}\nEnruta clientes a la ciudad más cercana.", state="normal", bg=self.bg_card, fg=self.fg_light)
            
        if self.motor.ia_analyzer_purchased:
            if self.motor.ia_analyzer_enabled:
                self.buttons["ia"].config(text="🛡️ Escudo Antivirus [ON] | -$15/t\nMitigador DDoS activo.", state="normal", bg=self.color_green, fg="#11111b")
            else:
                self.buttons["ia"].config(text="🛡️ Escudo Antivirus [OFF] | -$0/t\nMitigador DDoS inactivo.", state="normal", bg=self.bg_card, fg=self.fg_light)
        elif self.motor.creditos < CONFIG_BALANCEO["UPGRADE_IA_ANALYZER_COST"]:
            self.buttons["ia"].config(text=f"🛡️ Compra Escudo Antivirus | ${CONFIG_BALANCEO['UPGRADE_IA_ANALYZER_COST']:.0f}\nFiltra tráfico DDoS.", state="disabled", bg=self.bg_card, fg=self.fg_dim)
        else:
            self.buttons["ia"].config(text=f"🛡️ Compra Escudo Antivirus | ${CONFIG_BALANCEO['UPGRADE_IA_ANALYZER_COST']:.0f}\nFiltra tráfico DDoS.", state="normal", bg=self.bg_card, fg=self.fg_light)
            
        if self.motor.party_routing_active:
            self.buttons["party"].config(text="🏆 Ruteo Partidas [ACTIVO]\nReduce carga CPU global en 25%.", state="disabled", bg="#313244", fg=self.fg_dim)
        elif is_active or self.motor.creditos < CONFIG_BALANCEO["UPGRADE_PARTY_ROUTING_COST"]:
            self.buttons["party"].config(text=f"🏆 Compra Ruteo Partidas | ${CONFIG_BALANCEO['UPGRADE_PARTY_ROUTING_COST']:.0f}\nOptimiza tráfico por tipo de partida.", state="disabled", bg=self.bg_card, fg=self.fg_dim)
        else:
            self.buttons["party"].config(text=f"🏆 Compra Ruteo Partidas | ${CONFIG_BALANCEO['UPGRADE_PARTY_ROUTING_COST']:.0f}\nOptimiza tráfico por tipo de partida.", state="normal", bg=self.bg_card, fg=self.fg_light)
            
        # 6. Actualizar Panel de Inspección
        self.actualizar_panel_inspeccion()
        
        # 7. Actualizar HUD de Alertas
        mensaje = self.motor.ultimo_mensaje_evento
        self.lbl_hud_alert.config(text=mensaje)
        if "🚨" in mensaje or "CRASH" in mensaje:
            self.lbl_hud_alert.config(fg=self.color_red, bg="#1a0c0f")
        else:
            self.lbl_hud_alert.config(fg=self.color_blue, bg="#0c0d12")
        
        # 8. Redibujar mapa de red
        self.dibujar_mapa_nodos()

    # --- Bucle de ejecución ---
    def bucle_tick(self):
        if self.motor.fin_del_juego:
            self.registrar_mensaje(self.motor.ultimo_mensaje_evento, True)
            self.actualizar_interfaz()
            messagebox.showerror("¡DESPEDIDO!", 
                                 f"¡HAS SIDO DESPEDIDO!\n\nLa junta directiva ha prescindido de tus servicios por mala gestión corporativa.\n\n"
                                 f"Días sobrevivientes: {self.motor.dias_transcurridos - 1}\n"
                                 f"Créditos finales: ${self.motor.creditos:.2f}\n"
                                 f"Aprobación final del CEO: {self.motor.ceo_approval:.0f}%",
                                 parent=self.ventana)
            self.raiz.destroy()
            return

        workday_was_active = self.motor.jornada_activa
        self.motor.tick()
        
        if workday_was_active and not self.motor.jornada_activa:
            self.registrar_mensaje("=========================================", False)
            self.registrar_mensaje(f"📋 REPORTE DE FIN DE JORNADA - DIA {self.motor.dias_transcurridos}", False)
            self.registrar_mensaje(f"Presupuesto Base Corporativo: +${self.motor.daily_base_budget:.2f}", False)
            self.registrar_mensaje(f"Bono por Usuarios Satisfechos: +${self.motor.daily_satisfied_bonus:.2f} ({self.motor.daily_satisfied_users} usuarios)", False)
            self.registrar_mensaje(f"Penalizaciones de hoy: -${self.motor.daily_penalty:.2f}", True if self.motor.daily_penalty > 0 else False)
            self.registrar_mensaje(f"Costo de Infraestructura: -${self.motor.daily_maintenance:.2f}", False)
            self.registrar_mensaje(f"Presupuesto Neto Final: ${self.motor.creditos:.2f}", False)
            self.registrar_mensaje(f"Aprobación CEO: {self.motor.ceo_approval:.0f}%", False)
            self.registrar_mensaje("=========================================", False)
            
            if self.motor.fin_del_juego:
                self.registrar_mensaje(self.motor.ultimo_mensaje_evento, True)
                self.actualizar_interfaz()
                messagebox.showerror("¡DESPEDIDO!", 
                                     f"¡HAS SIDO DESPEDIDO!\n\nLa junta directiva ha prescindido de tus servicios por mala gestión corporativa.\n\n"
                                     f"Días sobrevivientes: {self.motor.dias_transcurridos}\n"
                                     f"Créditos finales: ${self.motor.creditos:.2f}\n"
                                     f"Aprobación final del CEO: {self.motor.ceo_approval:.0f}%",
                                     parent=self.ventana)
                self.raiz.destroy()
                return

        if self.motor.jornada_activa and not self.motor.pausado:
            if "🚨" in self.motor.ultimo_mensaje_evento:
                self.registrar_mensaje(self.motor.ultimo_mensaje_evento, True)
            elif self.motor.contador_ticks % 4 == 0:
                self.registrar_mensaje(self.motor.ultimo_mensaje_evento, False)
                
            if self.motor.is_downtime:
                self.registrar_mensaje(f"FALLO DE SLA: Servidores caídos por sobrecarga! Multa: -${CONFIG_BALANCEO['DOWNTIME_PENALTY']:.1f}", True)
            elif self.motor.latencia > 100.0:
                self.registrar_mensaje(f"LATENCIA EXCESIVA: SLA Breach (>100ms)! Multa: -${CONFIG_BALANCEO['LATENCY_PENALTY']:.1f}", True)

        self.actualizar_interfaz()
        self.raiz.after(1000, self.bucle_tick)
