import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import platform
import random
try:
    import winsound
except ImportError:
    winsound = None
from config import BALANCING_CONFIG
from core.engine import GameEngine

class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  
        
        # Configurar la ventana principal (root) como anclaje de la barra de tareas
        self.root.title("Ping Zero: Server Manager")
        self.root.geometry("1x1+0+0")
        self.root.attributes("-alpha", 0.0)
        
        self.window = tk.Toplevel(self.root)
        self.window.title("Ping Zero: Server Manager")
        self.window.configure(bg="#0c0d12")
        
        # Eliminar decoración nativa del SO
        self.window.overrideredirect(True)
        
        self.root.deiconify()  # Mapear root para mostrar el icono en la barra de tareas
        
        # Vincular eventos de mapeo de root para Alt+Tab
        self.root.bind("<Map>", self.on_root_map)
        self.root.bind("<Unmap>", self.on_root_unmap)
        
        self.window.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.window.bind("<Destroy>", lambda e: self.root.destroy() if e.widget == self.window else None)
            
        self.engine = GameEngine()
        
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
        
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        normal_w = 1100
        normal_h = 700
        x = (screen_w - normal_w) // 2
        y = (screen_h - normal_h) // 2
        self.normal_geometry = f"{normal_w}x{normal_h}+{x}+{y}"
        
        # Iniciar en tamaño normal de ventana por defecto (1100x700)
        self.window.geometry(self.normal_geometry)
        
        # Variables de zoom y navegación del mapa
        self.zoom_factor = 1.0
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
        
        self.setup_ui()
        self.update_ui()
        self.window.after(150, self.center_camera)
        self.tick_loop()

    # --- Lógica de la Barra de Título Customizada ---
    def start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def drag_window(self, event):
        if not self.is_maximized:
            x = self.window.winfo_x() - self.drag_data["x"] + event.x
            y = self.window.winfo_y() - self.drag_data["y"] + event.y
            self.window.geometry(f"+{x}+{y}")

    def minimize_window(self):
        self.window.withdraw()
        self.root.iconify()

    def toggle_maximize(self, event=None):
        if self.is_maximized:
            self.window.geometry(self.normal_geometry)
            self.is_maximized = False
            self.btn_max.config(text="□")
        else:
            self.normal_geometry = self.window.geometry()
            screen_w = self.window.winfo_screenwidth()
            screen_h = self.window.winfo_screenheight()
            self.window.geometry(f"{screen_w}x{screen_h}+0+0")
            self.is_maximized = True
            self.btn_max.config(text="❐")

    def on_root_map(self, event):
        if event.widget == self.root:
            self.window.deiconify()
            self.window.lift()

    def on_root_unmap(self, event):
        if event.widget == self.root:
            self.window.withdraw()

    # --- Ayuda contextual al pasar el mouse ---
    def bind_hover(self, widget, text):
        pass

    # --- Construcción de la UI ---
    def setup_ui(self):
        # 0. Custom Title Bar (Orden de Windows estándar: Minimizar, Maximizar, Cerrar)
        self.title_bar = tk.Frame(self.window, bg=self.bg_panel, height=30)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)
        
        self.title_bar.bind("<ButtonPress-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.drag_window)
        self.title_bar.bind("<Double-Button-1>", self.toggle_maximize)
        
        title_label = tk.Label(self.title_bar, text=" ⚙️ PING ZERO: Server Manager", font=("Helvetica", 9, "bold"), fg=self.color_blue, bg=self.bg_panel)
        title_label.pack(side="left", padx=10)
        title_label.bind("<ButtonPress-1>", self.start_drag)
        title_label.bind("<B1-Motion>", self.drag_window)
        title_label.bind("<Double-Button-1>", self.toggle_maximize)

        # Botones discretos de persistencia
        btn_save_style = {"font": ("Helvetica", 8, "bold"), "bg": self.bg_panel, "fg": self.fg_light, "relief": "flat", "padx": 5}
        self.btn_save = tk.Button(self.title_bar, text="💾 Guardar", command=self.save_game_gui, **btn_save_style)
        self.btn_save.pack(side="left", padx=5)
        self.btn_save.bind("<Enter>", lambda e: self.btn_save.config(bg="#313244"))
        self.btn_save.bind("<Leave>", lambda e: self.btn_save.config(bg=self.bg_panel))

        self.btn_load = tk.Button(self.title_bar, text="📂 Cargar", command=self.load_game_gui, **btn_save_style)
        self.btn_load.pack(side="left", padx=5)
        self.btn_load.bind("<Enter>", lambda e: self.btn_load.config(bg="#313244"))
        self.btn_load.bind("<Leave>", lambda e: self.btn_load.config(bg=self.bg_panel))
        
        btn_style = {"font": ("Helvetica", 10, "bold"), "bg": self.bg_panel, "fg": self.fg_light, "relief": "flat", "width": 4, "height": 1}
        
        # Cerrar, Maximizar y Minimizar
        self.btn_close = tk.Button(self.title_bar, text="X", command=self.root.destroy, **btn_style)
        self.btn_close.pack(side="right")
        self.btn_close.bind("<Enter>", lambda e: self.btn_close.config(bg=self.color_red, fg="#11111b"))
        self.btn_close.bind("<Leave>", lambda e: self.btn_close.config(bg=self.bg_panel, fg=self.fg_light))
        
        self.btn_max = tk.Button(self.title_bar, text="❐" if self.is_maximized else "□", command=self.toggle_maximize, **btn_style)
        self.btn_max.pack(side="right")
        self.btn_max.bind("<Enter>", lambda e: self.btn_max.config(bg="#313244"))
        self.btn_max.bind("<Leave>", lambda e: self.btn_max.config(bg=self.bg_panel))
        
        self.btn_min = tk.Button(self.title_bar, text="_", command=self.minimize_window, **btn_style)
        self.btn_min.pack(side="right")
        self.btn_min.bind("<Enter>", lambda e: self.btn_min.config(bg="#313244"))
        self.btn_min.bind("<Leave>", lambda e: self.btn_min.config(bg=self.bg_panel))

        # 1. Header Frame
        header = tk.Frame(self.window, bg=self.bg_panel, height=45)
        header.pack(fill="x", side="top")
        
        tk.Label(header, text="⚙️ PING ZERO:", font=("Helvetica", 11, "bold"), fg=self.color_blue, bg=self.bg_panel).pack(side="left", padx=(20, 5), pady=8)
        self.lbl_time = tk.Label(header, text="📅 DIA: 1 [PLANIFICACION]", font=("Helvetica", 9, "bold"), fg=self.color_yellow, bg=self.bg_panel)
        self.lbl_time.pack(side="left", padx=10, pady=8)
        
        self.lbl_forecast = tk.Label(header, text="📈 PRONOSTICO: Carga normal", font=("Helvetica", 9, "bold"), fg=self.color_blue, bg=self.bg_panel)
        self.lbl_forecast.pack(side="left", padx=15, pady=8)
        
        self.lbl_rank = tk.Label(header, text="🏆 RANGO: SysAdmin Junior", font=("Helvetica", 9, "bold"), fg=self.color_yellow, bg=self.bg_panel)
        self.lbl_rank.pack(side="left", padx=15, pady=8)
        
        self.lbl_autoscale_banner = tk.Label(header, text="AUTO-SCALING: INACTIVO", font=("Helvetica", 8, "bold"), fg=self.fg_dim, bg=self.bg_panel)
        self.lbl_autoscale_banner.pack(side="right", padx=20, pady=8)

        # 2. Contenedor Principal (2 Columnas)
        main_container = tk.Frame(self.window, bg=self.bg_dark)
        main_container.pack(fill="both", expand=True, padx=15, pady=5)

        # Columna Izquierda (Área de Trabajo - 70% del ancho)
        left_col = tk.Frame(main_container, bg=self.bg_dark)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Columna Derecha (Panel de Control Fijo - 30% del ancho)
        right_col = tk.Frame(main_container, bg=self.bg_dark, width=330)
        right_col.pack(side="right", fill="both")
        right_col.pack_propagate(False)

        # --- Elementos de la Columna Izquierda ---

        # 2.1 Dashboard Superior (Métricas)
        dashboard = tk.Frame(left_col, bg=self.bg_dark)
        dashboard.pack(fill="x", pady=(0, 5))
        
        self.cards = {}
        metrics = [
            ("credits", "PRESUPUESTO", self.color_green, "$3,000.00"),
            ("traffic", "TRAFICO TOTAL", self.color_blue, "0 req/s"),
            ("latency", "PING PROMEDIO", self.color_green, "0 ms"),
            ("ceo", "APROBACION CEO", self.color_green, "100%"),
            ("room", "DATA CENTERS", self.color_yellow, "1/9 Salas")
        ]
        
        for key, title, color, val in metrics:
            card = tk.Frame(dashboard, bg=self.bg_card, bd=0)
            card.pack(side="left", expand=True, fill="both", padx=3, pady=2)
            lbl = tk.Label(card, text=title, font=("Helvetica", 7, "bold"), fg=self.fg_dim, bg=self.bg_card)
            lbl.pack(pady=(4, 1))
            v_lbl = tk.Label(card, text=val, font=("Helvetica", 11, "bold"), fg=color, bg=self.bg_card)
            v_lbl.pack(pady=(0, 4))
            self.cards[key] = v_lbl

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
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.pan_motion)
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.pan_motion)
        
        # Binds de Zoom
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Button-4>", self.zoom)
        self.canvas.bind("<Button-5>", self.zoom)
        
        # Deselección al hacer clic en el fondo del canvas
        self.canvas.bind("<Button-1>", self.on_canvas_bg_click)
        
        # HUD de Alertas Fijo (sobre el Canvas con coordenadas relativas)
        self.lbl_hud_alert = tk.Label(self.canvas_lf, text="Consola SysAdmin Lista.", font=("Helvetica", 9, "bold"),
                                      fg=self.color_blue, bg="#0c0d12", bd=0, relief="flat", padx=15, pady=8, wraplength=450)
        self.lbl_hud_alert.place(relx=0.5, y=20, anchor="n")

        # --- Elementos de la Columna Derecha ---

        # 3.1 Botón de Acción Principal (Iniciar Jornada)
        self.btn_start_shift = tk.Button(right_col, text="▶️ INICIAR JORNADA", font=("Helvetica", 14, "bold"),
                                         bg=self.color_green, fg="#11111b", height=3, width=25, relief="flat", command=self.start_shift_click)
        self.btn_start_shift.pack(fill="x", padx=15, pady=15)

        # 3.3 Telemetría en Vivo (Abajo de la Columna Derecha)
        log_lf = tk.Frame(right_col, bg=self.bg_dark, bd=0, height=220)
        log_lf.pack(side="bottom", fill="x", expand=False)
        log_lf.pack_propagate(False)
        
        self.frame_traffic_breakdown = tk.Frame(log_lf, bg="#0d0e15", bd=0)
        self.frame_traffic_breakdown.pack(fill="x", padx=5, pady=4)
        
        self.lbl_traffic_breakdown = tk.Label(self.frame_traffic_breakdown, text="📊 TRÁFICO POR CIUDAD:\n• Miami: 0 req/s\n• Bogotá: 0 req/s\n• São Paulo: 0 req/s",
                                              font=("Helvetica", 8, "bold"), fg=self.color_blue, bg="#0d0e15", justify="left")
        self.lbl_traffic_breakdown.pack(pady=4)
        
        self.txt_logs = tk.Text(log_lf, bg="#0d0e15", fg=self.color_blue, font=("Consolas", 8), bd=0, state="disabled")
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
        self.inspection_content.pack(fill="both", expand=True, padx=8, pady=8)

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

        for key, text in upgrades:
            btn = tk.Button(shop_container, text=text, font=("Helvetica", 8, "bold"), relief="flat", height=2,
                            bg=self.bg_card, fg=self.fg_light, activebackground=self.color_blue, justify="left", anchor="w", padx=8,
                            command=lambda k=key: self.buy_upgrade_click(k))
            btn.pack(side="top", fill="x", pady=3)
            self.buttons[key] = btn

        self.bind_hover(self.buttons["autoscale"], "☁️ LICENCIA CLOUD: Habilita el escalado automático en la nube cuando la carga del sistema sea extrema.")
        self.bind_hover(self.buttons["geo"], "🌍 ROUTER GEO DNS: Enruta a los clientes al servidor más cercano, eliminando por completo la penalización de ping por desbordamiento.")
        self.bind_hover(self.buttons["ia"], "🛡️ ESCUDO ANTIVIRUS: Analizador de antivirus y WAF inteligente para mitigar ataques cibernéticos maliciosos.")
        self.bind_hover(self.buttons["party"], "🏆 RUTEO PARTIDAS: Clasifica el tráfico según tipo de partida para mejorar la capacidad global de la infraestructura en un 25%.")

    # --- Sonidos ---
    def play_sound(self, sound_type):
        if winsound is None:
            try:
                self.window.bell()
            except Exception:
                pass
            return
        try:
            if sound_type == "success":
                winsound.Beep(800, 100)
            elif sound_type == "error":
                winsound.Beep(300, 300)
            elif sound_type == "alert":
                winsound.Beep(450, 150)
                winsound.Beep(450, 150)
        except Exception:
            try:
                self.window.bell()
            except Exception:
                pass

    # --- Logs ---
    def log(self, msg, is_alert=False):
        self.txt_logs.configure(state="normal")
        self.txt_logs.insert(tk.END, f"{'[ALERT] ' if is_alert else '[INFO] '}{msg}\n")
        self.txt_logs.see(tk.END)
        self.txt_logs.configure(state="disabled")
        if is_alert:
            if "CRASH" in msg or "DDoS" in msg or "SLA" in msg or "LATENCIA" in msg:
                self.play_sound("alert")
            else:
                self.play_sound("error")

    # --- Persistencia de Partida ---
    def save_game_gui(self):
        if self.engine.workday_active:
            self.log("No puedes guardar la partida durante la jornada laboral.", True)
            messagebox.showerror("Error", "No puedes guardar la partida mientras el turno esté en curso.", parent=self.window)
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json")],
            initialfile="savegame.json",
            title="Guardar Partida",
            parent=self.window
        )
        if filename:
            if self.engine.save_game(filename):
                self.log("Estado de la red guardado correctamente.", False)
                self.play_sound("success")
                messagebox.showinfo("Partida Guardada", "La partida se ha guardado correctamente.", parent=self.window)
            else:
                self.log("Error al guardar la partida.", True)
                messagebox.showerror("Error", "Hubo un error al intentar guardar la partida.", parent=self.window)

    def load_game_gui(self):
        if self.engine.workday_active:
            self.log("No puedes cargar una partida durante la jornada laboral.", True)
            messagebox.showerror("Error", "No puedes cargar una partida mientras el turno esté en curso.", parent=self.window)
            return
            
        filename = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json")],
            title="Cargar Partida",
            parent=self.window
        )
        if filename:
            if self.engine.load_game(filename):
                self.log("Partida cargada correctamente. Reanudando simulación...", False)
                self.play_sound("success")
                self.clear_selection()
                self.update_ui()
                self.center_camera()
                messagebox.showinfo("Partida Cargada", "La partida se ha cargado correctamente.", parent=self.window)
            else:
                self.log("Error al cargar la partida o archivo corrupto.", True)
                messagebox.showerror("Error", "No se pudo cargar la partida. El archivo podría estar corrupto o no existir.", parent=self.window)

    # --- Lógica de Paneo y Zoom ---
    def center_camera(self):
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
        
        target_x = 0.0 * self.zoom_factor
        target_y = -200.0 * self.zoom_factor
        
        frac_x = ((target_x - width / 2.0) - x1) / w_total
        frac_y = ((target_y - height / 2.0) - y1) / h_total
        
        frac_x = max(0.0, min(1.0, frac_x))
        frac_y = max(0.0, min(1.0, frac_y))
        
        self.canvas.xview_moveto(frac_x)
        self.canvas.yview_moveto(frac_y)

    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def pan_motion(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def zoom(self, event):
        mx = self.canvas.canvasx(event.x)
        my = self.canvas.canvasy(event.y)
        
        factor = 1.1 if (event.delta > 0 or event.num == 4) else 0.9
        new_zoom = self.zoom_factor * factor
        
        if 0.5 <= new_zoom <= 3.0:
            self.zoom_factor = new_zoom
            self.update_ui()
            
            # Paneo reactivo respecto a (0, 0)
            dx = mx * (factor - 1)
            dy = my * (factor - 1)
            self.canvas.scan_mark(0, 0)
            self.canvas.scan_dragto(int(-dx), int(-dy), gain=1)

    def on_canvas_bg_click(self, event):
        if not self.canvas.find_withtag("current"):
            self.clear_selection()

    # --- Clics en Nodos (Retornar "break" para evitar paneo accidental) ---
    def on_wan_click(self, event):
        self.select_item("wan")
        return "break"

    def on_continent_click(self, event, continent):
        self.select_item("continent", continent=continent)
        return "break"

    def on_dc_click(self, event, city):
        self.select_item("dc_open", region=city)
        return "break"

    def on_srv_click(self, event, city, idx):
        self.select_item("server", region=city, index=idx)
        return "break"

    # --- Lógica de Panel de Inspección Fijo ---
    def select_item(self, item_type, **kwargs):
        self.selected_item = {"type": item_type, "kwargs": kwargs}
        self.update_inspection_panel()

    def clear_selection(self):
        self.selected_item = None
        self.update_inspection_panel()

    def update_inspection_panel(self):
        for widget in self.inspection_content.winfo_children():
            widget.destroy()

        if self.selected_item is None:
            lbl = tk.Label(self.inspection_content, text="1. Haz clic en un Nodo para administrarlo.\n2. Compra enlaces e infraestructuras en el Canvas.\n3. Haz clic en Iniciar Jornada.",
                           font=("Helvetica", 8, "bold"), fg=self.fg_dim, bg=self.bg_dark, justify="center", wraplength=280)
            lbl.pack(expand=True, fill="both", pady=20)
            return

        item_type = self.selected_item["type"]
        kwargs = self.selected_item["kwargs"]
        is_active = self.engine.workday_active

        if item_type == "wan":
            lbl_title = tk.Label(self.inspection_content, text="🌐 INTERNET GLOBAL (WAN)",
                                 font=("Helvetica", 10, "bold"), fg=self.color_blue, bg=self.bg_dark)
            lbl_title.pack(anchor="w", pady=(2, 6))
            
            lbl_desc = tk.Label(self.inspection_content, text="Administra enlaces de red internacionales. Compra fibra transoceánica para conectar nuevos mercados continentales.",
                                font=("Helvetica", 8), fg=self.fg_light, bg=self.bg_dark, justify="left", wraplength=300)
            lbl_desc.pack(anchor="w", pady=(0, 10))
            
            continents_list = ["América", "Europa", "Asia"]
            for cont in continents_list:
                is_purchased = cont in self.engine.purchased_continents
                is_unlocked = self.engine.is_continent_unlocked(cont)
                
                # Marco para cada continente
                frame_cont = tk.Frame(self.inspection_content, bg=self.bg_card, padx=6, pady=4)
                frame_cont.pack(fill="x", pady=2)
                
                lbl_name = tk.Label(frame_cont, text=cont.upper(), font=("Helvetica", 8, "bold"), fg=self.fg_light, bg=self.bg_card)
                lbl_name.pack(side="left")
                
                if is_purchased:
                    lbl_status = tk.Label(frame_cont, text="✅ CONECTADO", font=("Helvetica", 8, "bold"), fg=self.color_green, bg=self.bg_card)
                    lbl_status.pack(side="right")
                else:
                    if is_unlocked:
                        cost_cont = BALANCING_CONFIG["CONTINENT_UNLOCK_COST"]
                        btn_buy = tk.Button(frame_cont, text=f"Conectar | ${cost_cont:.0f}", font=("Helvetica", 7, "bold"),
                                            bg=self.color_blue, fg="#11111b", relief="flat", padx=5,
                                            state="disabled" if (is_active or self.engine.credits < cost_cont) else "normal",
                                            command=lambda c=cont: self.buy_continent_action(c))
                        btn_buy.pack(side="right")
                    else:
                        unlock_day = 5 if cont == "Europa" else 10
                        lbl_status = tk.Label(frame_cont, text=f"🔒 Día {unlock_day}", font=("Helvetica", 7, "bold"), fg=self.fg_dim, bg=self.bg_card)
                        lbl_status.pack(side="right")

        elif item_type == "continent":
            continent = kwargs["continent"]
            lbl_title = tk.Label(self.inspection_content, text=f"🌐 REGION: {continent.upper()}",
                                 font=("Helvetica", 10, "bold"), fg=self.color_blue, bg=self.bg_dark)
            lbl_title.pack(anchor="w", pady=(2, 6))
            
            lbl_desc = tk.Label(self.inspection_content, text=f"Inaugura Data Centers en las ciudades de {continent} para enrutar el tráfico local de esta región.",
                                font=("Helvetica", 8), fg=self.fg_light, bg=self.bg_dark, justify="left", wraplength=300)
            lbl_desc.pack(anchor="w", pady=(0, 10))
            
            cities = BALANCING_CONFIG["LOCATIONS"][continent]
            cost = BALANCING_CONFIG["OPEN_DATACENTER_COST"]
            for city in cities:
                is_open = city in self.engine.datacenters
                
                frame_city = tk.Frame(self.inspection_content, bg=self.bg_card, padx=6, pady=4)
                frame_city.pack(fill="x", pady=2)
                
                lbl_city = tk.Label(frame_city, text=city, font=("Helvetica", 8, "bold"), fg=self.fg_light, bg=self.bg_card)
                lbl_city.pack(side="left")
                
                if is_open:
                    lbl_status = tk.Label(frame_city, text="✅ ACTIVO", font=("Helvetica", 8, "bold"), fg=self.color_green, bg=self.bg_card)
                    lbl_status.pack(side="right")
                else:
                    btn_buy = tk.Button(frame_city, text=f"Abrir DC | ${cost:.0f}", font=("Helvetica", 7, "bold"),
                                        bg=self.color_blue, fg="#11111b", relief="flat", padx=5,
                                        state="disabled" if (is_active or self.engine.credits < cost) else "normal",
                                        command=lambda r=city: self.open_dc_action(r))
                    btn_buy.pack(side="right")

        elif item_type == "dc_open":
            region = kwargs["region"]
            dc = self.engine.datacenters[region]
            
            lbl_title = tk.Label(self.inspection_content, text=f"🏢 DC: {region.upper()}",
                                 font=("Helvetica", 10, "bold"), fg=self.color_blue, bg=self.bg_dark)
            lbl_title.pack(anchor="w", pady=(2, 4))
            
            stats_text = (
                f"• Racks Ocupados: {len(dc['servers'])}/{dc['room_max_slots']}\n"
                f"• Climatización central: Nivel {dc['room_cooling_lvl']}\n"
                f"• Temperatura Central: {dc['room_temp']:.1f}°C\n"
                f"• Carga CPU: {dc['cpu_stress']:.1f}%\n"
                f"• Carga RAM: {dc['ram_stress']:.1f}%"
            )
            lbl_stats = tk.Label(self.inspection_content, text=stats_text,
                                 font=("Helvetica", 8, "bold"), fg=self.fg_light, bg=self.bg_dark, justify="left")
            lbl_stats.pack(anchor="w", pady=(2, 8))
            
            cost_racks = BALANCING_CONFIG["UPGRADE_ROOM_SLOTS_COST"]
            racks_state = "normal" if (not is_active and self.engine.credits >= cost_racks) else "disabled"
            btn_racks = tk.Button(self.inspection_content, text=f"🏢 Expandir Racks (+2 slots) | ${cost_racks:.0f}",
                                  font=("Helvetica", 8, "bold"), bg=self.bg_card, fg=self.fg_light, state=racks_state,
                                  relief="flat", command=lambda: self.upgrade_dc_slots_action(region))
            btn_racks.pack(fill="x", pady=2)
            
            cost_cool = BALANCING_CONFIG["UPGRADE_ROOM_COOLING_COST"]
            cool_state = "normal" if (not is_active and self.engine.credits >= cost_cool) else "disabled"
            btn_cool = tk.Button(self.inspection_content, text=f"❄️ Climatización (+1 Lvl) | ${cost_cool:.0f}",
                                 font=("Helvetica", 8, "bold"), bg=self.bg_card, fg=self.fg_light, state=cool_state,
                                 relief="flat", command=lambda: self.upgrade_dc_cooling_action(region))
            btn_cool.pack(fill="x", pady=2)
            
            cost_srv = BALANCING_CONFIG["UPGRADE_SERVER_COST"]
            has_slots = len(dc['servers']) < dc['room_max_slots']
            srv_state = "normal" if (not is_active and has_slots and self.engine.credits >= cost_srv) else "disabled"
            btn_srv = tk.Button(self.inspection_content, text=f"🚀 Instalar Servidor físico | ${cost_srv:.0f}",
                                font=("Helvetica", 8, "bold"), bg=self.bg_card, fg=self.fg_light, state=srv_state,
                                relief="flat", command=lambda: self.buy_server_action(region))
            btn_srv.pack(fill="x", pady=2)

        elif item_type == "server":
            region = kwargs["region"]
            idx = kwargs["index"]
            dc = self.engine.datacenters[region]
            
            if idx >= len(dc["servers"]):
                self.clear_selection()
                return
                
            srv = dc["servers"][idx]
            
            lbl_title = tk.Label(self.inspection_content, text=f"🖥️ {srv['name']} ({region.upper()})",
                                 font=("Helvetica", 10, "bold"), fg=self.color_blue, bg=self.bg_dark)
            lbl_title.pack(anchor="w", pady=(2, 4))
            
            status_str = f"REINICIANDO ({srv['offline_timer']}s)" if srv['offline_timer'] > 0 else "ONLINE"
            
            stats_text = (
                f"• Estado: {status_str}\n"
                f"• Temperatura: {srv['temp']:.1f}°C\n"
                f"• Computación (HW): Nivel {srv['hw_lvl']}\n"
                f"• Disipador (Cool): Nivel {srv['cool_lvl']}"
            )
            
            lbl_stats = tk.Label(self.inspection_content, text=stats_text,
                                 font=("Helvetica", 8, "bold"), fg=self.fg_light, bg=self.bg_dark, justify="left")
            lbl_stats.pack(anchor="w", pady=(2, 8))
            
            cost_hw = BALANCING_CONFIG["UPGRADE_SERVER_HW_COST"]
            hw_state = "normal" if (not is_active and self.engine.credits >= cost_hw) else "disabled"
            btn_hw = tk.Button(self.inspection_content, text=f"🚀 Mejorar Computación (+600 req/s) | ${cost_hw:.0f}",
                               font=("Helvetica", 8, "bold"), bg=self.bg_card, fg=self.fg_light, state=hw_state,
                               relief="flat", command=lambda: self.upgrade_srv_hw_action(region, idx))
            btn_hw.pack(fill="x", pady=2)
            
            cost_cool = BALANCING_CONFIG["UPGRADE_SERVER_COOLING_COST"]
            cool_state = "normal" if (not is_active and self.engine.credits >= cost_cool) else "disabled"
            btn_cool = tk.Button(self.inspection_content, text=f"❄️ Mejorar Disipador (Enfriar) | ${cost_cool:.0f}",
                                 font=("Helvetica", 8, "bold"), bg=self.bg_card, fg=self.fg_light, state=cool_state,
                                 relief="flat", command=lambda: self.upgrade_srv_cooling_action(region, idx))
            btn_cool.pack(fill="x", pady=2)
            
            reboot_state = "normal" if (is_active and not self.engine.is_paused and srv['offline_timer'] == 0) else "disabled"
            btn_reboot = tk.Button(self.inspection_content, text="🔄 Reiniciar Máquina (Flush caché)",
                                   font=("Helvetica", 8, "bold"), bg=self.bg_card, fg=self.color_yellow, state=reboot_state,
                                   relief="flat", command=lambda: self.reboot_srv_action(region, idx))
            btn_reboot.pack(fill="x", pady=2)

        # Botón de salir del panel
        btn_close = tk.Button(self.inspection_content, text="✖ Cerrar Panel / Cancelar", font=("Helvetica", 8, "bold"),
                              bg=self.bg_card, fg=self.color_red, relief="flat", command=self.clear_selection)
        btn_close.pack(fill="x", pady=(10, 2))

    # --- Acciones del Panel ---
    def buy_continent_action(self, continent):
        if self.engine.buy_continent(continent):
            self.log(self.engine.last_event_msg, False)
            self.play_sound("success")
            self.select_item("continent", continent=continent)
        else:
            self.log(self.engine.last_event_msg, True)
            self.play_sound("error")
        self.update_ui()

    def open_dc_action(self, region):
        if self.engine.open_datacenter(region):
            self.log(self.engine.last_event_msg, False)
            self.play_sound("success")
            self.select_item("dc_open", region=region)
        else:
            self.log(self.engine.last_event_msg, True)
            self.play_sound("error")
        self.update_ui()

    def upgrade_dc_slots_action(self, region):
        if self.engine.upgrade_room_slots(region):
            self.log(self.engine.last_event_msg, False)
            self.play_sound("success")
        else:
            self.log(self.engine.last_event_msg, True)
        self.update_ui()

    def upgrade_dc_cooling_action(self, region):
        if self.engine.upgrade_room_cooling(region):
            self.log(self.engine.last_event_msg, False)
            self.play_sound("success")
        else:
            self.log(self.engine.last_event_msg, True)
        self.update_ui()

    def buy_server_action(self, region):
        if self.engine.buy_server(region):
            self.log(self.engine.last_event_msg, False)
            self.play_sound("success")
            idx = len(self.engine.datacenters[region]["servers"]) - 1
            self.select_item("server", region=region, index=idx)
        else:
            self.log(self.engine.last_event_msg, True)
        self.update_ui()

    def upgrade_srv_hw_action(self, region, idx):
        if self.engine.upgrade_server_hardware(region, idx):
            self.log(self.engine.last_event_msg, False)
            self.play_sound("success")
        else:
            self.log(self.engine.last_event_msg, True)
        self.update_ui()

    def upgrade_srv_cooling_action(self, region, idx):
        if self.engine.upgrade_server_cooling(region, idx):
            self.log(self.engine.last_event_msg, False)
            self.play_sound("success")
        else:
            self.log(self.engine.last_event_msg, True)
        self.update_ui()

    def reboot_srv_action(self, region, idx):
        self.engine.reboot_server(region, idx)
        self.log(self.engine.last_event_msg, False)
        self.play_sound("success")
        self.update_ui()

    # --- Compras de Tienda ---
    def buy_upgrade_click(self, key):
        if key in ["autoscale", "ia"] and getattr(self.engine, f"{key}_purchased"):
            getattr(self.engine, f"toggle_{key}")()
            self.play_sound("success")
        else:
            if self.engine.buy_upgrade(key):
                self.log(self.engine.last_event_msg, False)
                self.play_sound("success")
            else:
                self.log(f"🚨 Fondos insuficientes o jornada activa para comprar mejora: {key}.", True)
        self.update_ui()

    def start_shift_click(self):
        if self.engine.start_workday():
            self.log(self.engine.last_event_msg)
            self.update_ui()

    def draw_nodes_map(self):
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
        self.canvas.create_text(internet_x, internet_y, text="WAN", font=("Helvetica", 8, "bold"), fill="#11111b", tags=(tag_id_wan, "text", "size_8"))
        
        # Enlazar clic y hover para la WAN
        self.canvas.tag_bind(tag_id_wan, "<Button-1>", self.on_wan_click)
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
            if cont not in self.engine.purchased_continents:
                continue
                
            cont_cities = BALANCING_CONFIG["LOCATIONS"][cont]
            cont_open = any(c in self.engine.datacenters for c in cont_cities)
            line_color = "#a6e3a1" if cont_open else "#89b4fa"
            
            # Conexión WAN -> Continente
            self.canvas.create_line(internet_x, internet_y + internet_radius, cont_x, cont_y - cont_radius, fill=line_color, width=2)
            
            tag_id_cont = f"cont_click_{cont}"
            # Círculo de Continente
            cont_oval_id = self.canvas.create_oval(cont_x - cont_radius, cont_y - cont_radius, cont_x + cont_radius, cont_y + cont_radius,
                                    fill="#1e1e2e", outline=line_color, width=2, tags=tag_id_cont)
            self.canvas.create_text(cont_x, cont_y, text=cont.upper(), font=("Helvetica", 7, "bold"), fill=self.fg_light, tags=(tag_id_cont, "text", "size_7"))
            
            # Enlazar clic y hover para el Continente
            self.canvas.tag_bind(tag_id_cont, "<Button-1>", lambda event, c=cont: self.on_continent_click(event, c))
            self.canvas.tag_bind(tag_id_cont, "<Enter>", lambda event, oid=cont_oval_id, oc=line_color: self.canvas.itemconfigure(oid, outline="#ffffff", width=4))
            self.canvas.tag_bind(tag_id_cont, "<Leave>", lambda event, oid=cont_oval_id, oc=line_color: self.canvas.itemconfigure(oid, outline=oc, width=2))

            # Conexiones Continente -> Ciudades
            for city in cont_cities:
                # Solo dibujar la ciudad si el Data Center está abierto
                if city not in self.engine.datacenters:
                    continue
                    
                cx, cy = city_coords[city]
                city_line_color = "#a6e3a1"
                
                # Línea desde el continente a la ciudad
                self.canvas.create_line(cont_x, cont_y + cont_radius, cx, cy - city_radius, fill=city_line_color, width=1.5)
                
                tag_id_dc = f"dc_click_{city}"
                
                dc = self.engine.datacenters[city]
                dc_color = "#1e1e2e"
                border_color = "#a6e3a1"
                text_color = self.fg_light
                dc_text = f"{city}\n{dc['room_temp']:.0f}°C\n{len(dc['servers'])}/{dc['room_max_slots']}"
                
                # Círculo de la Ciudad
                dc_oval_id = self.canvas.create_oval(cx - city_radius, cy - city_radius, cx + city_radius, cy + city_radius,
                                                     fill=dc_color, outline=border_color, width=2, tags=tag_id_dc)
                self.canvas.create_text(cx, cy, text=dc_text, font=("Helvetica", 6, "bold"), fill=text_color, justify="center", tags=(tag_id_dc, "text", "size_6"))
                
                # Enlazar clic y hover para el Data Center
                self.canvas.tag_bind(tag_id_dc, "<Button-1>", lambda event, c=city: self.on_dc_click(event, c))
                self.canvas.tag_bind(tag_id_dc, "<Enter>", lambda event, oid=dc_oval_id: self.canvas.itemconfigure(oid, outline="#ffffff", width=4))
                self.canvas.tag_bind(tag_id_dc, "<Leave>", lambda event, oid=dc_oval_id, oc=border_color: self.canvas.itemconfigure(oid, outline=oc, width=2))
                
                # 3. Dibujar Servidores de esta ciudad (Nivel 4)
                servers = dc["servers"]
                num_servers = len(servers)
                server_y = 70.0
                server_radius = 12
                
                if num_servers > 0:
                    dx = 30.0  # Separación
                    start_x = cx - (num_servers - 1) * dx / 2
                    
                    for j, s in enumerate(servers):
                        sx = start_x + j * dx
                        
                        # Cable ciudad -> servidor
                        self.canvas.create_line(cx, cy + city_radius, sx, server_y - server_radius, fill="#45475a", width=1.5)
                        
                        # Color por estado/temp
                        if s["offline_timer"] > 0:
                            srv_color = self.color_blue
                            label = f"OFF ({s['offline_timer']}s)"
                        elif s["temp"] >= 85.0:
                            srv_color = self.color_red
                            label = f"{s['temp']:.1f}°C"
                        elif s["temp"] >= 70.0:
                            srv_color = self.color_yellow
                            label = f"{s['temp']:.1f}°C"
                        else:
                            srv_color = self.color_green
                            label = f"{s['temp']:.1f}°C"
                            
                        tag_id_srv = f"srv_click_{city}_{j}"
                        
                        srv_oval_id = self.canvas.create_oval(sx - server_radius, server_y - server_radius,
                                                              sx + server_radius, server_y + server_radius,
                                                              fill=srv_color, outline="#ffffff", width=1.5, tags=tag_id_srv)
                        self.canvas.create_text(sx, server_y, text=f"S{j+1}", font=("Helvetica", 6, "bold"), fill="#11111b", tags=(tag_id_srv, "text", "size_6"))
                        
                        ping_text = "OFF" if s["offline_timer"] > 0 else f"{s['ping']:.0f}ms"
                        self.canvas.create_text(sx, server_y + server_radius + 8, text=ping_text, font=("Helvetica", 6, "bold"), fill=self.fg_light, tags=("text", "size_6"))
                        self.canvas.create_text(sx, server_y + server_radius + 16, text=label, font=("Helvetica", 5, "bold"), fill=self.fg_dim, tags=("text", "size_5"))
                        
                        # Enlazar clic y hover para el Servidor
                        self.canvas.tag_bind(tag_id_srv, "<Button-1>", lambda event, c=city, idx=j: self.on_srv_click(event, c, idx))
                        self.canvas.tag_bind(tag_id_srv, "<Enter>", lambda event, oid=srv_oval_id: self.canvas.itemconfigure(oid, outline="#f9e2af", width=4))
                        self.canvas.tag_bind(tag_id_srv, "<Leave>", lambda event, oid=srv_oval_id: self.canvas.itemconfigure(oid, outline="#ffffff", width=1.5))
                else:
                    self.canvas.create_text(cx, cy + city_radius + 15, text="Sin Servidores", font=("Helvetica", 6, "italic"), fill=self.fg_dim, tags=("text", "size_6", "style_italic"))

        # 4. Dibujar DDoS (Hacia la ciudad atacada)
        if self.engine.traffic_ddos > 0:
            target_city = getattr(self.engine, "ddos_region", "Miami")
            if target_city in self.engine.datacenters:
                tx, ty = city_coords.get(target_city, (0.0, city_y))
                for _ in range(5):
                    t = random.uniform(0.1, 0.9)
                    px = internet_x + t * (tx - internet_x) + random.uniform(-15, 15)
                    py = internet_y + t * (ty - internet_y) + random.uniform(-15, 15)
                    self.canvas.create_oval(px - 3, py - 3, px + 3, py + 3, fill="#11111b", outline=self.color_red, tags="ddos")

        # 5. Escalar todo el mapa respecto a (0, 0)
        self.canvas.scale("all", 0, 0, self.zoom_factor, self.zoom_factor)
        
        # Ajustar dinámicamente las fuentes del canvas
        for text_id in self.canvas.find_withtag("text"):
            tags = self.canvas.gettags(text_id)
            base_size = 8
            for tag in tags:
                if tag.startswith("size_"):
                    base_size = int(tag.split("_")[1])
                    break
            
            new_size = max(4, int(base_size * self.zoom_factor))
            font_style = "bold"
            if "style_italic" in tags:
                font_style = "italic"
            self.canvas.itemconfigure(text_id, font=("Helvetica", new_size, font_style))

    # --- Actualización y Redibujado general ---
    def update_ui(self):
        is_active = self.engine.workday_active
        
        # 1. Actualizar barra superior (Día / Estado / Pronóstico)
        if is_active:
            self.lbl_time.config(text=f"📅 DIA {self.engine.days_elapsed} [OPERACIONES]", fg=self.color_red)
            self.btn_start_shift.config(text=f"⏳ JORNADA EN CURSO... ({self.engine.workday_timer}s)", state="disabled", bg=self.color_red, fg="#45475a", disabledforeground="#45475a")
        else:
            self.lbl_time.config(text=f"📅 DIA {self.engine.days_elapsed + 1} [PLANIFICACION]", fg=self.color_yellow)
            self.btn_start_shift.config(text="▶️ INICIAR JORNADA", state="normal", bg=self.color_green, fg="#11111b")
            
        self.lbl_forecast.config(text=self.engine.get_forecast_text())
        self.lbl_rank.config(text=f"🏆 RANGO: {self.engine.it_title}")
        
        # 2. Métricas Dashboard
        self.cards["credits"].config(text=f"${self.engine.credits:,.2f}")
        self.cards["traffic"].config(text=f"{self.engine.traffic_users + self.engine.traffic_ddos} req/s")
        self.cards["latency"].config(text=f"{self.engine.latency:.1f} ms")
        self.cards["ceo"].config(text=f"{self.engine.ceo_approval:.0f}%")
        
        total_srv = sum(len(dc["servers"]) for dc in self.engine.datacenters.values())
        self.cards["room"].config(text=f"{len(self.engine.datacenters)}/9 DCs | {total_srv} Servs")
        
        # Latencia color
        if self.engine.latency > 100.0:
            self.cards["latency"].config(fg=self.color_red)
        elif self.engine.latency > 60.0:
            self.cards["latency"].config(fg=self.color_yellow)
        else:
            self.cards["latency"].config(fg=self.color_green)
            
        # Aprobación CEO color
        if self.engine.ceo_approval < 40.0:
            self.cards["ceo"].config(fg=self.color_red)
        elif self.engine.ceo_approval < 75.0:
            self.cards["ceo"].config(fg=self.color_yellow)
        else:
            self.cards["ceo"].config(fg=self.color_green)
            
        # 3. Desglose de Tráfico por Ciudad
        reg_text = "📊 TRÁFICO POR CIUDAD:\n"
        for city in self.engine.all_cities:
            t_city = self.engine.traffic_users_regional.get(city, 0)
            p_city = self.engine.regional_pings.get(city, 20.0)
            reg_text += f"• {city}: {t_city} req/s ({p_city:.0f} ms)\n"
        self.lbl_traffic_breakdown.config(text=reg_text.strip())
            
        # 4. Progressbars de Estrés
        if self.engine.is_downtime:
            self.lbl_cpu_text.config(text=f"ESTRES CPU: COLA DE CAIDA ({self.engine.cpu_stress:.1f}%)", fg=self.color_red)
            self.lbl_ram_text.config(text=f"ESTRES RAM: OVERFLOW MEMORIA ({self.engine.ram_stress:.1f}%)", fg=self.color_red)
            self.progress_cpu.config(style="Downtime.Horizontal.TProgressbar")
            self.progress_ram.config(style="Downtime.Horizontal.TProgressbar")
        else:
            self.lbl_cpu_text.config(text=f"CONSUMO CPU: {self.engine.cpu_stress:.1f}%", fg=self.fg_light)
            self.lbl_ram_text.config(text=f"CONSUMO RAM: {self.engine.ram_stress:.1f}%", fg=self.fg_light)
            self.progress_cpu.config(style="CPU.Horizontal.TProgressbar")
            self.progress_ram.config(style="RAM.Horizontal.TProgressbar")
            
        self.progress_cpu["value"] = self.engine.cpu_stress
        self.progress_ram["value"] = self.engine.ram_stress
        
        # Banner Auto-scale
        if self.engine.auto_scale_purchased:
            if self.engine.auto_scale_enabled:
                if self.engine.is_autoscale_running:
                    self.lbl_autoscale_banner.config(text="AUTO-SCALING: RUNNING (LOAD > 80%)", fg=self.color_green)
                else:
                    self.lbl_autoscale_banner.config(text="AUTO-SCALING: STANDBY (LOAD OK)", fg=self.color_yellow)
            else:
                self.lbl_autoscale_banner.config(text="AUTO-SCALING: APAGADO", fg=self.fg_dim)
        else:
            self.lbl_autoscale_banner.config(text="AUTO-SCALING: INACTIVO", fg=self.fg_dim)
            
        # 5. Botones de tienda (Los de servidor y datacenter ya se manejan desde el canvas)
            
        if self.engine.auto_scale_purchased:
            if self.engine.auto_scale_enabled:
                self.buttons["autoscale"].config(text="☁️ Licencia Cloud [ON] | -$5/t\nAuto-Scaling activo por carga.", state="normal", bg=self.color_green, fg="#11111b")
            else:
                self.buttons["autoscale"].config(text="☁️ Licencia Cloud [OFF] | -$0/t\nAuto-Scaling inactivo.", state="normal", bg=self.bg_card, fg=self.fg_light)
        elif is_active or self.engine.credits < BALANCING_CONFIG["UPGRADE_AUTOSCALE_COST"]:
            self.buttons["autoscale"].config(text=f"☁️ Compra Licencia Cloud | ${BALANCING_CONFIG['UPGRADE_AUTOSCALE_COST']:.0f}\nHabilita el escalado automático.", state="disabled", bg=self.bg_card, fg=self.fg_dim)
        else:
            self.buttons["autoscale"].config(text=f"☁️ Compra Licencia Cloud | ${BALANCING_CONFIG['UPGRADE_AUTOSCALE_COST']:.0f}\nHabilita el escalado automático.", state="normal", bg=self.bg_card, fg=self.fg_light)
            
        if self.engine.geo_balancer_active:
            self.buttons["geo"].config(text="🌍 Router Geo DNS [ACTIVO]\nElimina penalización por overflow.", state="disabled", bg="#313244", fg=self.fg_dim)
        elif is_active or self.engine.credits < BALANCING_CONFIG["UPGRADE_GEO_BALANCER_COST"]:
            self.buttons["geo"].config(text=f"🌍 Compra Router Geo DNS | ${BALANCING_CONFIG['UPGRADE_GEO_BALANCER_COST']:.0f}\nEnruta clientes a la ciudad más cercana.", state="disabled", bg=self.bg_card, fg=self.fg_dim)
        else:
            self.buttons["geo"].config(text=f"🌍 Compra Router Geo DNS | ${BALANCING_CONFIG['UPGRADE_GEO_BALANCER_COST']:.0f}\nEnruta clientes a la ciudad más cercana.", state="normal", bg=self.bg_card, fg=self.fg_light)
            
        if self.engine.ia_analyzer_purchased:
            if self.engine.ia_analyzer_enabled:
                self.buttons["ia"].config(text="🛡️ Escudo Antivirus [ON] | -$15/t\nMitigador DDoS activo.", state="normal", bg=self.color_green, fg="#11111b")
            else:
                self.buttons["ia"].config(text="🛡️ Escudo Antivirus [OFF] | -$0/t\nMitigador DDoS inactivo.", state="normal", bg=self.bg_card, fg=self.fg_light)
        elif is_active or self.engine.credits < BALANCING_CONFIG["UPGRADE_IA_ANALYZER_COST"]:
            self.buttons["ia"].config(text=f"🛡️ Compra Escudo Antivirus | ${BALANCING_CONFIG['UPGRADE_IA_ANALYZER_COST']:.0f}\nFiltra tráfico DDoS.", state="disabled", bg=self.bg_card, fg=self.fg_dim)
        else:
            self.buttons["ia"].config(text=f"🛡️ Compra Escudo Antivirus | ${BALANCING_CONFIG['UPGRADE_IA_ANALYZER_COST']:.0f}\nFiltra tráfico DDoS.", state="normal", bg=self.bg_card, fg=self.fg_light)
            
        if self.engine.party_routing_active:
            self.buttons["party"].config(text="🏆 Ruteo Partidas [ACTIVO]\nReduce carga CPU global en 25%.", state="disabled", bg="#313244", fg=self.fg_dim)
        elif is_active or self.engine.credits < BALANCING_CONFIG["UPGRADE_PARTY_ROUTING_COST"]:
            self.buttons["party"].config(text=f"🏆 Compra Ruteo Partidas | ${BALANCING_CONFIG['UPGRADE_PARTY_ROUTING_COST']:.0f}\nOptimiza tráfico por tipo de partida.", state="disabled", bg=self.bg_card, fg=self.fg_dim)
        else:
            self.buttons["party"].config(text=f"🏆 Compra Ruteo Partidas | ${BALANCING_CONFIG['UPGRADE_PARTY_ROUTING_COST']:.0f}\nOptimiza tráfico por tipo de partida.", state="normal", bg=self.bg_card, fg=self.fg_light)
            
        # 6. Actualizar Panel de Inspección
        self.update_inspection_panel()
        
        # 7. Actualizar HUD de Alertas
        msg = self.engine.last_event_msg
        self.lbl_hud_alert.config(text=msg)
        if "🚨" in msg or "CRASH" in msg:
            self.lbl_hud_alert.config(fg=self.color_red, bg="#1a0c0f")
        else:
            self.lbl_hud_alert.config(fg=self.color_blue, bg="#0c0d12")
        
        # 8. Redibujar mapa de red
        self.draw_nodes_map()

    # --- Bucle de ejecución ---
    def tick_loop(self):
        if self.engine.is_game_over:
            self.log(self.engine.last_event_msg, True)
            self.update_ui()
            messagebox.showerror("¡DESPEDIDO!", 
                                 f"¡HAS SIDO DESPEDIDO!\n\nLa junta directiva ha prescindido de tus servicios por mala gestión corporativa.\n\n"
                                 f"Días sobrevivientes: {self.engine.days_elapsed - 1}\n"
                                 f"Créditos finales: ${self.engine.credits:.2f}\n"
                                 f"Aprobación final del CEO: {self.engine.ceo_approval:.0f}%",
                                 parent=self.window)
            self.root.destroy()
            return

        workday_was_active = self.engine.workday_active
        self.engine.tick()
        
        if workday_was_active and not self.engine.workday_active:
            self.log("=========================================", False)
            self.log(f"📋 REPORTE DE FIN DE JORNADA - DIA {self.engine.days_elapsed}", False)
            self.log(f"Presupuesto Base Corporativo: +${self.engine.daily_base_budget:.2f}", False)
            self.log(f"Bono por Usuarios Satisfechos: +${self.engine.daily_satisfied_bonus:.2f} ({self.engine.daily_satisfied_users} usuarios)", False)
            self.log(f"Penalizaciones de hoy: -${self.engine.daily_penalty:.2f}", True if self.engine.daily_penalty > 0 else False)
            self.log(f"Costo de Infraestructura: -${self.engine.daily_maintenance:.2f}", False)
            self.log(f"Presupuesto Neto Final: ${self.engine.credits:.2f}", False)
            self.log(f"Aprobación CEO: {self.engine.ceo_approval:.0f}%", False)
            self.log("=========================================", False)
            
            if self.engine.new_certification_unlocked:
                self.play_sound("success")
                messagebox.showinfo(
                    "🎓 ¡NUEVA CERTIFICACIÓN DE TI!",
                    f"¡Felicitaciones! Has obtenido una nueva certificación de TI:\n\n🏆 Rango: {self.engine.it_title}\n\n¡Sigue gestionando la red con éxito para seguir ascendiendo!",
                    parent=self.window
                )
                self.engine.new_certification_unlocked = False
            
            if self.engine.is_game_over:
                self.log(self.engine.last_event_msg, True)
                self.update_ui()
                messagebox.showerror("¡DESPEDIDO!", 
                                     f"¡HAS SIDO DESPEDIDO!\n\nLa junta directiva ha prescindido de tus servicios por mala gestión corporativa.\n\n"
                                     f"Días sobrevivientes: {self.engine.days_elapsed}\n"
                                     f"Créditos finales: ${self.engine.credits:.2f}\n"
                                     f"Aprobación final del CEO: {self.engine.ceo_approval:.0f}%",
                                     parent=self.window)
                self.root.destroy()
                return

        if self.engine.workday_active and not self.engine.is_paused:
            if "🚨" in self.engine.last_event_msg:
                self.log(self.engine.last_event_msg, True)
            elif self.engine.tick_counter % 4 == 0:
                self.log(self.engine.last_event_msg, False)
                
            if self.engine.is_downtime:
                self.log(f"FALLO DE SLA: Servidores caídos por sobrecarga! Multa: -${BALANCING_CONFIG['DOWNTIME_PENALTY']:.1f}", True)
            elif self.engine.latency > 100.0:
                self.log(f"LATENCIA EXCESIVA: SLA Breach (>100ms)! Multa: -${BALANCING_CONFIG['LATENCY_PENALTY']:.1f}", True)

        self.update_ui()
        self.root.after(1000, self.tick_loop)
