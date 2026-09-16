"""Vistas de consulta y gestión: los botones delegan las operaciones al servicio."""
import tkinter as tk
from tkinter import messagebox, ttk


class MainView(tk.Frame):
    def __init__(self, master, restaurante_servicio, usuario_actual, al_cerrar_sesion):
        super().__init__(master, bg="#f5f1eb")
        self.restaurante_servicio = restaurante_servicio
        self.usuario_actual = usuario_actual
        self.al_cerrar_sesion = al_cerrar_sesion
        self.botones_menu = {}
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
                         font=("Arial", 10, "bold"), padding=(10, 5))
        estilo.map("Accion.TButton", background=[("active", "#773318")])
        estilo.configure("Secundario.TButton", background="#eadbc9", foreground="#472d23",
                         font=("Arial", 10), padding=(10, 5))
        estilo.map("Secundario.TButton", background=[("active", "#dcc5ac")])
        estilo.configure("Eliminar.TButton", background="#fbe8e4", foreground="#9f2820",
                         font=("Arial", 10, "bold"), padding=(10, 5))
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
        tk.Label(lateral, text="RESTAURANTE\nAPP", bg="#472d23", fg="white",
                 justify="left", font=("Arial", 13, "bold")).pack(anchor="w")
        tk.Label(lateral, text=f"Sesión de {self.usuario_actual.nombre}", wraplength=146,
                 justify="left", bg="#472d23", fg="#eadbc9",
                 font=("Arial", 10)).pack(anchor="w", pady=(10, 26))
        self.boton_inicio = self.crear_boton_menu(lateral, "Inicio", self.mostrar_inicio)
        self.boton_productos = self.crear_boton_menu(lateral, "Productos", self.mostrar_productos)
        self.boton_usuarios = self.crear_boton_menu(lateral, "Usuarios", self.mostrar_usuarios)
        self.boton_ventas = ttk.Button(lateral, text="Ventas (pendiente)", style="Menu.TButton",
                                       command=self.mostrar_funcionalidad_pendiente)
        self.boton_ventas.pack(fill="x", pady=(0, 8))
        self.boton_cerrar = ttk.Button(lateral, text="Cerrar sesión", style="Secundario.TButton",
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
        boton = ttk.Button(contenedor, text=texto, command=comando, style="Menu.TButton")
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
                              "Gestiona los productos y consulta los usuarios desde el menú lateral.")
        resumen = tk.Frame(self.contenido, bg="#f5f1eb")
        resumen.pack(fill="x", pady=(6, 24))
        for titulo, cantidad in (("Productos registrados", self.restaurante_servicio.cantidad_productos()),
                                 ("Usuarios registrados", self.restaurante_servicio.cantidad_usuarios())):
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
            boton = ttk.Button(acciones, text=texto, command=comando, style=estilo)
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
                                      f"  |  Usuarios: {self.restaurante_servicio.cantidad_usuarios()}")

    def mostrar_funcionalidad_pendiente(self):
        messagebox.showinfo("Ventas pendientes", "Las ventas se incorporarán en una próxima etapa.",
                            parent=self)

    def cerrar_sesion(self):
        self.al_cerrar_sesion()
