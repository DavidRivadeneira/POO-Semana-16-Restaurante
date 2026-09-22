"""Vistas de consulta y gestión: los botones delegan las operaciones al servicio."""
import tkinter as tk
from tkinter import messagebox, ttk
from ui.recursos import cargar_imagen


class MainView(tk.Frame):
    def __init__(self, master, restaurante_servicio, usuario_actual, al_cerrar_sesion):
        super().__init__(master, bg="#f5f1eb")
        self.restaurante_servicio = restaurante_servicio
        self.usuario_actual = usuario_actual
        self.al_cerrar_sesion = al_cerrar_sesion
        self.botones_menu = {}
        self.iconos = {nombre: cargar_imagen(self, f"icons/{nombre}.png")
                       for nombre in ("inicio", "productos", "usuarios", "ventas",
                                      "salir", "registrar", "buscar", "actualizar",
                                      "eliminar", "limpiar")}
        self.logo = cargar_imagen(self, "logo/menu.png")
        self.definir_estilos()
        self.construir_interfaz()

    def definir_estilos(self):
        estilo = ttk.Style(self)
        estilo.configure("Menu.TButton", background="#624234", foreground="white",
                         font=("Arial", 10, "bold"), padding=(12, 10), anchor="w")
        estilo.map("Menu.TButton", background=[("active", "#78513e")])
        estilo.configure("Activo.TButton", background="#eadbc9", foreground="#472d23",
                         font=("Arial", 10, "bold"), padding=(12, 10), anchor="w")
        estilo.map("Activo.TButton", background=[("active", "#dcc5ac")])
        estilo.configure("Accion.TButton", background="#9a431f", foreground="white",
                         font=("Arial", 10, "bold"), padding=(10, 4))
        estilo.map("Accion.TButton", background=[("active", "#773318")])
        estilo.configure("Secundario.TButton", background="#eadbc9", foreground="#472d23",
                         font=("Arial", 10), padding=(10, 4))
        estilo.map("Secundario.TButton", background=[("active", "#dcc5ac")])
        estilo.configure("Eliminar.TButton", background="#fbe8e4", foreground="#9f2820",
                         font=("Arial", 10, "bold"), padding=(10, 4))
        estilo.map("Eliminar.TButton", background=[("active", "#f4cbc3")])
        estilo.configure("Restaurante.Treeview", font=("Arial", 10), rowheight=30,
                         background="white", fieldbackground="white", foreground="#472d23")
        estilo.configure("Restaurante.Treeview.Heading", font=("Arial", 10, "bold"),
                         background="#eadbc9", foreground="#472d23", padding=(6, 8))

    def construir_interfaz(self):
        # pack organiza zonas grandes; cada zona administra a sus propios hijos.
        lateral = tk.Frame(self, bg="#472d23", width=180, padx=14, pady=24)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        tk.Label(lateral, image=self.logo, bg="#472d23").pack(anchor="w", pady=(0, 10))
        tk.Label(lateral, text="RESTAURANTE\nAPP", bg="#472d23", fg="white",
                 justify="left", font=("Arial", 13, "bold")).pack(anchor="w")
        tk.Label(lateral, text=f"Sesión de {self.usuario_actual.nombre}", wraplength=146,
                 justify="left", bg="#472d23", fg="#eadbc9",
                 font=("Arial", 10)).pack(anchor="w", pady=(10, 26))
        self.boton_inicio = self.crear_boton_menu(lateral, "Inicio", self.mostrar_inicio)
        self.boton_productos = self.crear_boton_menu(lateral, "Productos", self.mostrar_productos)
        self.boton_usuarios = self.crear_boton_menu(lateral, "Usuarios", self.mostrar_usuarios)
        self.boton_ventas = self.crear_boton_menu(lateral, "Ventas", self.mostrar_ventas)
        self.boton_cerrar = ttk.Button(lateral, text="Cerrar sesión", style="Secundario.TButton",
                                       image=self.iconos["salir"], compound="left",
                                       command=self.cerrar_sesion)
        self.boton_cerrar.pack(side="bottom", fill="x")
        principal = tk.Frame(self, bg="#f5f1eb")
        principal.pack(side="left", fill="both", expand=True)
        # Reservar el pie antes del contenido mantiene visibles los conteos.
        barra = tk.Frame(principal, bg="#eadbc9", padx=20, pady=10)
        barra.pack(side="bottom", fill="x")
        self.etiqueta_estado = tk.Label(barra, bg="#eadbc9", fg="#472d23", font=("Arial", 10))
        self.etiqueta_estado.pack(anchor="w")
        self.contenido = tk.Frame(principal, bg="#f5f1eb", padx=20, pady=20)
        self.contenido.pack(fill="both", expand=True)
        self.mostrar_inicio()

    def crear_boton_menu(self, contenedor, texto, comando):
        boton = ttk.Button(contenedor, text=texto, command=comando, style="Menu.TButton",
                           image=self.iconos[texto.lower()], compound="left")
        boton.pack(fill="x", pady=(0, 8))
        self.botones_menu[texto] = boton
        return boton

    def preparar_seccion(self, nombre, titulo, ayuda):
        for texto, boton in self.botones_menu.items():
            boton.configure(style="Activo.TButton" if texto == nombre else "Menu.TButton")
        self.limpiar_contenido()
        self.crear_titulo_seccion(titulo)
        tk.Label(self.contenido, text=ayuda, bg="#f5f1eb", fg="#67594f",
                 font=("Arial", 10), anchor="w").pack(anchor="w", pady=(0, 18))
        self.actualizar_barra_estado()

    def limpiar_contenido(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()

    def crear_titulo_seccion(self, texto):
        tk.Label(self.contenido, text=texto, bg="#f5f1eb", fg="#472d23",
                 font=("Arial", 22, "bold")).pack(anchor="w", pady=(0, 8))

    def mostrar_inicio(self):
        self.preparar_seccion("Inicio", "Panel del restaurante",
                              "Gestiona productos, consulta usuarios y registra ventas desde el menú lateral.")
        resumen = tk.Frame(self.contenido, bg="#f5f1eb")
        resumen.pack(fill="x", pady=(6, 24))
        for titulo, cantidad in (("Productos", self.restaurante_servicio.cantidad_productos()),
                                 ("Usuarios", self.restaurante_servicio.cantidad_usuarios()),
                                 ("Ventas", self.restaurante_servicio.cantidad_ventas())):
            tarjeta = tk.Frame(resumen, bg="white", padx=20, pady=20)
            tarjeta.pack(side="left", fill="both", expand=True, padx=(0, 12))
            tk.Label(tarjeta, text=titulo, bg="white", fg="#67594f",
                     font=("Arial", 11)).pack(anchor="w")
            tk.Label(tarjeta, text=str(cantidad), bg="white", fg="#9a431f",
                     font=("Arial", 30, "bold")).pack(anchor="w", pady=(8, 0))
        instrucciones = tk.LabelFrame(self.contenido, text="Gestión de productos", bg="white",
                                      fg="#472d23", padx=20, pady=20, font=("Arial", 11, "bold"))
        instrucciones.pack(fill="x")
        tk.Label(instrucciones, text="1. Abre Productos.\n"
                 "2. Completa el formulario o carga un producto por su código.\n"
                 "3. Usa los botones para registrar, actualizar o eliminar.",
                 justify="left", bg="white", fg="#472d23",
                 font=("Arial", 11)).pack(anchor="w")
        ttk.Button(instrucciones, text="Gestionar productos", command=self.mostrar_productos,
                   style="Accion.TButton").pack(anchor="w", pady=(18, 0))
        ventas = self.crear_grupo(self.contenido, "Nueva venta")
        ventas.pack(fill="x", pady=(16, 0))
        tk.Label(ventas, text="Selecciona un usuario y un producto. Confirma con Registrar venta.",
                 bg="white", fg="#472d23", font=("Arial", 10)).pack(anchor="w")
        ttk.Button(ventas, text="Ir a Ventas", command=self.mostrar_ventas,
                   image=self.iconos["registrar"], compound="left",
                   style="Accion.TButton").pack(anchor="w", pady=(10, 0))

    def mostrar_usuarios(self):
        self.preparar_seccion("Usuarios", "Usuarios registrados",
                              "Consulta la identificación, el nombre y el usuario de acceso.")
        listado = self.crear_grupo(self.contenido, "Consulta de usuarios")
        listado.pack(fill="both", expand=True)
        self.tabla_usuarios = self.crear_tabla(listado,
            (("identificacion", "Identificación", 130), ("nombre", "Nombre", 220),
             ("usuario", "Usuario", 150)))
        usuarios = self.restaurante_servicio.listar_usuarios()
        for usuario in usuarios:
            self.tabla_usuarios.insert("", tk.END,
                values=(usuario.identificacion, usuario.nombre, usuario.usuario))
        if not usuarios:
            tk.Label(listado, text="No hay usuarios registrados.", bg="white",
                     fg="#67594f").pack(anchor="w", pady=(8, 0))

    def mostrar_productos(self):
        self.preparar_seccion("Productos", "Gestión de productos",
                              "Escribe un código y pulsa Cargar por código para consultar un producto.")
        cuerpo = tk.Frame(self.contenido, bg="#f5f1eb")
        cuerpo.pack(fill="both", expand=True)
        cuerpo.columnconfigure(1, weight=1)
        cuerpo.rowconfigure(0, weight=1)
        formulario = self.crear_grupo(cuerpo, "Datos del producto")
        formulario.grid(row=0, column=0, sticky="ns", padx=(0, 16))
        formulario.columnconfigure(1, weight=1)
        self.producto_codigo_entry = self.crear_campo(formulario, "Código", 0)
        self.producto_nombre_entry = self.crear_campo(formulario, "Nombre", 1)
        self.producto_precio_entry = self.crear_campo(formulario, "Precio ($)", 2)
        self.producto_stock_entry = self.crear_campo(formulario, "Stock", 3)
        self.producto_stock_entry.insert(0, "0")
        acciones = tk.Frame(formulario, bg="white")
        acciones.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        self.botones_accion = {}
        for texto, comando, estilo in (
            ("Registrar", self.registrar_producto, "Accion.TButton"),
            ("Cargar por código", self.cargar_producto_en_formulario, "Secundario.TButton"),
            ("Actualizar", self.actualizar_producto, "Accion.TButton"),
            ("Eliminar", self.eliminar_producto, "Eliminar.TButton"),
            ("Limpiar", self.limpiar_formulario_producto, "Secundario.TButton"),
        ):
            icono = "buscar" if texto == "Cargar por código" else texto.lower()
            boton = ttk.Button(acciones, text=texto, command=comando, style=estilo,
                               image=self.iconos[icono], compound="left")
            boton.pack(fill="x", pady=(0, 4))
            self.botones_accion[texto] = boton
        self.mensaje_producto = tk.StringVar(value="Los cambios se guardan al confirmar una operación.")
        self.etiqueta_mensaje = tk.Label(formulario, textvariable=self.mensaje_producto,
            wraplength=200, height=4, justify="left", anchor="nw", bg="white", fg="#67594f", font=("Arial", 10))
        self.etiqueta_mensaje.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        listado = self.crear_grupo(cuerpo, "Productos registrados")
        listado.grid(row=0, column=1, sticky="nsew")
        self.tabla_productos = self.crear_tabla(listado,
            (("codigo", "Código", 75), ("nombre", "Nombre", 150),
             ("precio", "Precio ($)", 80), ("stock", "Stock", 60)))
        self.etiqueta_total = tk.Label(listado, bg="white", fg="#67594f", font=("Arial", 10))
        self.etiqueta_total.pack(anchor="w", pady=(8, 0))
        self.refrescar_productos()
        self.producto_codigo_entry.focus_set()

    def crear_grupo(self, contenedor, titulo):
        return tk.LabelFrame(contenedor, text=titulo, bg="white", fg="#472d23",
                             font=("Arial", 10, "bold"), padx=12, pady=10)

    def crear_campo(self, contenedor, texto, fila):
        tk.Label(contenedor, text=texto, bg="white", fg="#472d23",
                 font=("Arial", 10)).grid(row=fila, column=0, sticky="w", padx=(0, 10), pady=(0, 8))
        entrada = ttk.Entry(contenedor, width=18, font=("Arial", 10))
        entrada.grid(row=fila, column=1, sticky="ew", pady=(0, 8), ipady=3)
        return entrada

    def crear_tabla(self, contenedor, columnas):
        region = tk.Frame(contenedor, bg="white")
        region.pack(fill="both", expand=True)
        region.columnconfigure(0, weight=1)
        region.rowconfigure(0, weight=1)
        tabla = ttk.Treeview(region, columns=tuple(c[0] for c in columnas), show="headings",
                             selectmode="none", height=10, style="Restaurante.Treeview")
        for clave, titulo, ancho in columnas:
            tabla.heading(clave, text=titulo)
            tabla.column(clave, width=ancho, minwidth=ancho,
                         stretch=clave == "nombre", anchor="e" if clave in ("precio", "stock") else "w")
        vertical = ttk.Scrollbar(region, orient="vertical", command=tabla.yview)
        horizontal = ttk.Scrollbar(region, orient="horizontal", command=tabla.xview)
        tabla.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        tabla.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        return tabla

    def obtener_datos_producto(self):
        return tuple(entrada.get() for entrada in self.entradas_producto())

    def entradas_producto(self):
        return (self.producto_codigo_entry, self.producto_nombre_entry,
                self.producto_precio_entry, self.producto_stock_entry)

    def mostrar_mensaje_producto(self, texto, error=False):
        self.mensaje_producto.set(texto)
        self.etiqueta_mensaje.configure(fg="#b42318" if error else "#23633c")

    def completar_formulario(self, producto):
        valores = (producto.codigo, producto.nombre, str(producto.precio), str(producto.stock))
        for entrada, valor in zip(self.entradas_producto(), valores):
            entrada.delete(0, tk.END)
            entrada.insert(0, valor)

    def registrar_producto(self):
        try:
            producto = self.restaurante_servicio.registrar_producto(*self.obtener_datos_producto())
        except ValueError as error:
            self.mostrar_mensaje_producto(str(error), error=True)
            return
        self.completar_formulario(producto)
        self.refrescar_productos()
        self.mostrar_mensaje_producto(f"Producto {producto.codigo} registrado y guardado.")

    def cargar_producto_en_formulario(self):
        try:
            producto = self.restaurante_servicio.buscar_producto_por_codigo(self.producto_codigo_entry.get())
        except ValueError as error:
            self.mostrar_mensaje_producto(str(error), error=True)
            return
        if producto is None:
            self.mostrar_mensaje_producto("No existe un producto con ese código.", error=True)
            return
        self.completar_formulario(producto)
        self.mostrar_mensaje_producto(f"Producto {producto.codigo} cargado. Puedes actualizar sus datos.")

    def actualizar_producto(self):
        try:
            producto = self.restaurante_servicio.actualizar_producto(*self.obtener_datos_producto())
        except ValueError as error:
            self.mostrar_mensaje_producto(str(error), error=True)
            return
        self.completar_formulario(producto)
        self.refrescar_productos()
        self.mostrar_mensaje_producto(f"Producto {producto.codigo} actualizado y guardado.")

    def eliminar_producto(self):
        try:
            producto = self.restaurante_servicio.buscar_producto_por_codigo(self.producto_codigo_entry.get())
            if producto is None:
                self.mostrar_mensaje_producto("No existe un producto con ese código.", error=True)
                return
            if not messagebox.askyesno("Eliminar producto",
                    f"¿Eliminar {producto.codigo} - {producto.nombre}?", parent=self):
                return
            self.restaurante_servicio.eliminar_producto(producto.codigo)
        except ValueError as error:
            self.mostrar_mensaje_producto(str(error), error=True)
            return
        self.limpiar_formulario_producto()
        self.refrescar_productos()
        self.mostrar_mensaje_producto(f"Producto {producto.codigo} eliminado. Cambio guardado.")

    def limpiar_formulario_producto(self):
        for entrada in self.entradas_producto():
            entrada.delete(0, tk.END)
        self.producto_stock_entry.insert(0, "0")
        self.mostrar_mensaje_producto("Formulario limpio. Escribe un código para comenzar.")
        self.producto_codigo_entry.focus_set()

    def refrescar_productos(self):
        for fila in self.tabla_productos.get_children():
            self.tabla_productos.delete(fila)
        productos = self.restaurante_servicio.listar_productos()
        for producto in productos:
            self.tabla_productos.insert("", tk.END, values=(producto.codigo, producto.nombre,
                                        f"{producto.precio:.2f}", producto.stock))
        self.etiqueta_total.configure(text=f"{len(productos)} producto(s) registrado(s)" if productos
                                      else "No hay productos registrados.")
        self.actualizar_barra_estado()

    def actualizar_barra_estado(self):
        self.etiqueta_estado.configure(text=f"Productos: {self.restaurante_servicio.cantidad_productos()}"
                                      f"  |  Usuarios: {self.restaurante_servicio.cantidad_usuarios()}"
                                      f"  |  Ventas: {self.restaurante_servicio.cantidad_ventas()}")

    def mostrar_ventas(self):
        self.preparar_seccion("Ventas", "Gestión de ventas",
                              "Selecciona un usuario y un producto para registrar una venta sencilla.")
        formulario = self.crear_grupo(self.contenido, "Registrar venta")
        formulario.pack(fill="x", pady=(0, 16))
        formulario.columnconfigure(0, weight=1)
        formulario.columnconfigure(1, weight=1)
        self.opciones_usuarios = {
            f"{u.identificacion} · {u.nombre}": u.identificacion
            for u in self.restaurante_servicio.listar_usuarios()}
        self.opciones_productos = {
            f"{p.codigo} · {p.nombre}": p.codigo
            for p in self.restaurante_servicio.listar_productos()}
        for columna, texto in enumerate(("Usuario", "Producto")):
            tk.Label(formulario, text=texto, bg="white", fg="#472d23",
                     font=("Arial", 10, "bold")).grid(row=0, column=columna, sticky="w", pady=(0, 6))
        self.usuario_venta_combo = ttk.Combobox(formulario, state="readonly", width=24,
                                                values=list(self.opciones_usuarios))
        self.usuario_venta_combo.grid(row=1, column=0, sticky="ew", padx=(0, 12), ipady=4)
        self.producto_venta_combo = ttk.Combobox(formulario, state="readonly", width=24,
                                                 values=list(self.opciones_productos))
        self.producto_venta_combo.grid(row=1, column=1, sticky="ew", ipady=4)
        # Se pasa el método sin paréntesis: Tkinter lo ejecuta al pulsar el botón.
        self.boton_registrar_venta = ttk.Button(formulario, text="Registrar venta",
            command=self.registrar_venta, style="Accion.TButton",
            image=self.iconos["registrar"], compound="left")
        self.boton_registrar_venta.grid(row=2, column=0, sticky="w", pady=(12, 0))
        self.mensaje_venta = tk.StringVar(value="Elige ambas opciones para comenzar.")
        self.etiqueta_mensaje_venta = tk.Label(formulario, textvariable=self.mensaje_venta,
            bg="white", fg="#67594f", font=("Arial", 10), anchor="w", justify="left", wraplength=640)
        self.etiqueta_mensaje_venta.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        if not self.opciones_usuarios or not self.opciones_productos:
            self.boton_registrar_venta.state(["disabled"])
            self.mensaje_venta.set("Se necesitan usuarios y productos registrados para realizar una venta.")
        listado = self.crear_grupo(self.contenido, "Ventas registradas")
        listado.pack(fill="both", expand=True)
        # Reserva el pie antes de la tabla para mantenerlo visible al reducir la ventana.
        self.etiqueta_total_ventas = tk.Label(listado, bg="white", fg="#67594f", font=("Arial", 10))
        self.etiqueta_total_ventas.pack(side="bottom", anchor="w", pady=(8, 0))
        self.tabla_ventas = self.crear_tabla(listado,
            (("venta", "Venta", 75), ("usuario", "Usuario", 165),
             ("nombre", "Producto", 240), ("fecha", "Fecha", 110)))
        self.refrescar_ventas()

    def registrar_venta(self):
        """Callback: recoge selecciones, delega al servicio y presenta el resultado."""
        usuario_id = self.opciones_usuarios.get(self.usuario_venta_combo.get(), "")
        producto_codigo = self.opciones_productos.get(self.producto_venta_combo.get(), "")
        try:
            venta = self.restaurante_servicio.registrar_venta(usuario_id, producto_codigo)
        except ValueError as error:
            self.mensaje_venta.set(str(error))
            self.etiqueta_mensaje_venta.configure(fg="#b42318")
            return
        self.usuario_venta_combo.set("")
        self.producto_venta_combo.set("")
        self.refrescar_ventas()
        self.tabla_ventas.see(venta.identificador)
        self.mensaje_venta.set(f"Venta {venta.identificador} registrada y guardada correctamente.")
        self.etiqueta_mensaje_venta.configure(fg="#23633c")

    def refrescar_ventas(self):
        for fila in self.tabla_ventas.get_children():
            self.tabla_ventas.delete(fila)
        ventas = self.restaurante_servicio.listar_ventas()
        for venta in ventas:
            self.tabla_ventas.insert("", tk.END, iid=venta.identificador,
                values=(venta.identificador, f"{venta.usuario_id} · {venta.usuario_nombre}",
                        f"{venta.producto_codigo} · {venta.producto_nombre}", venta.fecha))
        self.etiqueta_total_ventas.configure(text=f"{len(ventas)} venta(s) registrada(s)" if ventas
                                             else "Aún no hay ventas. Registra la primera desde el formulario.")
        self.actualizar_barra_estado()

    def cerrar_sesion(self):
        self.al_cerrar_sesion()
