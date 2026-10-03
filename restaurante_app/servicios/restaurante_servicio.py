"""Concentra el acceso, usuarios, productos y ventas; delega la persistencia."""
from datetime import date

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta


class RestauranteServicio:
    def __init__(self, archivo_servicio):
        self.archivo_servicio = archivo_servicio
        self._usuarios = []
        self._productos = []
        self._ventas = []
        self._usuarios_por_id = {}
        self._usuarios_por_acceso = {}
        self._productos_por_codigo = {}
        self._usuario_autenticado = None
        self.cargar_datos()

    def cargar_datos(self):
        # ArchivoServicio lee diccionarios; este servicio los convierte en objetos.
        usuarios_json = self.archivo_servicio.leer_json("usuarios.json")
        productos_json = self.archivo_servicio.leer_json("productos.json")
        ventas_json = self.archivo_servicio.leer_json("ventas.json")
        try:
            usuarios = [Usuario(d["identificacion"], d["nombre"], d["usuario"],
                                d["contrasena"], d.get("rol", "Cliente")) for d in usuarios_json]
            productos = [Producto(d["codigo"], d["nombre"], d["precio"],
                                  d["stock"]) for d in productos_json]
            ventas = [Venta(**d) for d in ventas_json]
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"Registro inválido en los datos del restaurante: {error}") from error

        # Reutiliza la búsqueda por clave aprendida en Semana 12 para el login.
        indice = {usuario.usuario: usuario for usuario in usuarios}
        if len(indice) != len(usuarios):
            raise ValueError("Existen nombres de acceso duplicados en usuarios.json.")
        if len({u.identificacion for u in usuarios}) != len(usuarios):
            raise ValueError("Existen identificaciones duplicadas en usuarios.json.")
        if len({p.codigo for p in productos}) != len(productos):
            raise ValueError("Existen códigos duplicados en productos.json.")
        if len({int(v.identificador[1:]) for v in ventas}) != len(ventas):
            raise ValueError("Existen identificadores duplicados en ventas.json.")

        self._usuarios = usuarios
        self._productos = productos
        self._ventas = ventas
        self._usuarios_por_id = {u.identificacion: u for u in usuarios}
        self._usuarios_por_acceso = indice
        self._productos_por_codigo = {p.codigo: p for p in productos}

    def validar_acceso(self, usuario, contrasena):
        self.cerrar_sesion()
        usuario = usuario.strip()
        contrasena = contrasena.strip()
        if not usuario or not contrasena:
            return None
        registrado = self._usuarios_por_acceso.get(usuario)
        if registrado is not None and registrado.contrasena == contrasena:
            self._usuario_autenticado = registrado
            return registrado
        return None

    def cerrar_sesion(self):
        self._usuario_autenticado = None

    def validar_gestion_usuarios(self):
        """Control básico también en el servicio, no solo en el menú."""
        actual = self._usuario_autenticado
        if (actual is None or self._usuarios_por_id.get(actual.identificacion) is not actual
                or actual.rol != "Administrador"):
            raise ValueError("Solo el Administrador puede gestionar usuarios.")

    def buscar_usuario_por_identificacion(self, identificacion):
        identificacion = Usuario.validar_texto(identificacion, "identificación")
        return self._usuarios_por_id.get(identificacion)

    def _guardar_usuarios(self, usuarios):
        # Reutiliza el guardado atómico: confirma memoria e índices solo al guardar.
        self.archivo_servicio.escribir_json(
            "usuarios.json", [u.convertir_a_diccionario() for u in usuarios])
        self._usuarios = usuarios
        self._usuarios_por_id = {u.identificacion: u for u in usuarios}
        self._usuarios_por_acceso = {u.usuario: u for u in usuarios}

    def _validar_usuario_gestionable(self, identificacion):
        self.validar_gestion_usuarios()
        if not identificacion:
            raise ValueError("Seleccione un usuario de la tabla.")
        actual = self.buscar_usuario_por_identificacion(identificacion)
        if actual is None:
            raise ValueError("No existe un usuario con esa identificación.")
        if actual is self._usuario_autenticado:
            raise ValueError("La cuenta administrativa actualmente autenticada está protegida.")
        if actual.rol == "Administrador":
            raise ValueError("La gestión se limita a usuarios Empleado y Cliente.")
        return actual

    def _validar_datos_usuario(self, identificacion, nombre, usuario, contrasena, rol):
        nuevo = Usuario(identificacion, nombre, usuario, contrasena, rol)
        if nuevo.rol not in Usuario.ROLES_GESTIONABLES:
            raise ValueError("Solo se pueden asignar los roles Empleado y Cliente.")
        duplicado = self._usuarios_por_acceso.get(nuevo.usuario)
        if duplicado is not None and duplicado.identificacion != nuevo.identificacion:
            raise ValueError("Ya existe otro usuario con ese nombre de acceso.")
        return nuevo

    def registrar_usuario(self, identificacion, nombre, usuario, contrasena, rol):
        self.validar_gestion_usuarios()
        nuevo = self._validar_datos_usuario(identificacion, nombre, usuario, contrasena, rol)
        if nuevo.identificacion in self._usuarios_por_id:
            raise ValueError("Ya existe un usuario con esa identificación.")
        if any(v.usuario_id == nuevo.identificacion for v in self._ventas):
            raise ValueError("Esa identificación pertenece al historial de ventas. Use otra.")
        self._guardar_usuarios(self._usuarios + [nuevo])
        return nuevo

    def actualizar_usuario(self, identificacion, nombre, usuario, contrasena, rol):
        actual = self._validar_usuario_gestionable(identificacion)
        # Crea un reemplazo; evita mutar el objeto o sus índices antes de guardar.
        nuevo = self._validar_datos_usuario(actual.identificacion, nombre, usuario, contrasena, rol)
        self._guardar_usuarios([nuevo if u.identificacion == actual.identificacion else u
                               for u in self._usuarios])
        return nuevo

    def eliminar_usuario(self, identificacion):
        actual = self._validar_usuario_gestionable(identificacion)
        self._guardar_usuarios([u for u in self._usuarios if u.identificacion != actual.identificacion])
        return actual

    def listar_usuarios(self):
        return self._usuarios.copy()

    def listar_productos(self):
        return self._productos.copy()

    def cantidad_usuarios(self):
        return len(self._usuarios)

    def cantidad_productos(self):
        return len(self._productos)

    def listar_ventas(self):
        return self._ventas.copy()

    def cantidad_ventas(self):
        return len(self._ventas)

    def registrar_venta(self, usuario_id, producto_codigo):
        # La vista solo entrega las selecciones; las reglas se comprueban aquí.
        if not isinstance(usuario_id, str) or not usuario_id.strip():
            raise ValueError("Seleccione un usuario para registrar la venta.")
        if not isinstance(producto_codigo, str) or not producto_codigo.strip():
            raise ValueError("Seleccione un producto para registrar la venta.")
        usuario = self._usuarios_por_id.get(usuario_id.strip())
        producto = self._productos_por_codigo.get(producto_codigo.strip())
        if usuario is None:
            raise ValueError("El usuario seleccionado no existe.")
        if producto is None:
            raise ValueError("El producto seleccionado no existe.")
        siguiente = max((int(v.identificador[1:]) for v in self._ventas), default=0) + 1
        venta = Venta(f"V{siguiente:03d}", usuario.identificacion, producto.codigo,
                      date.today().isoformat(), usuario.nombre, producto.nombre)
        ventas = self._ventas + [venta]
        # Conserva los nombres del momento de la venta, aunque cambie el catálogo.
        # Primero guarda: un fallo no agrega una venta ficticia a la memoria.
        self.archivo_servicio.escribir_json(
            "ventas.json", [v.convertir_a_diccionario() for v in ventas])
        self._ventas = ventas
        return venta

    def buscar_producto_por_codigo(self, codigo):
        codigo = Producto.validar_texto(codigo, "código")
        return self._productos_por_codigo.get(codigo)

    @staticmethod
    def _crear_producto(codigo, nombre, precio, stock):
        # Entry entrega texto. Su conversión y validación pertenecen al servicio.
        if isinstance(stock, str):
            try:
                stock = int(stock.strip())
            except ValueError:
                raise ValueError("El stock debe ser un entero no negativo.") from None
        if isinstance(precio, str):
            precio = precio.strip().replace(",", ".")
        return Producto(codigo, nombre, precio, stock)

    def _guardar_cambios(self, productos):
        datos = [p.convertir_a_diccionario() for p in productos]
        # Si el guardado falla, las listas e índices conservan su estado anterior.
        self.archivo_servicio.escribir_json("productos.json", datos)
        self._productos = productos
        self._productos_por_codigo = {p.codigo: p for p in productos}

    def registrar_producto(self, codigo, nombre, precio, stock):
        producto = self._crear_producto(codigo, nombre, precio, stock)
        if self.buscar_producto_por_codigo(producto.codigo) is not None:
            raise ValueError("Ya existe un producto con ese código.")
        self._guardar_cambios(self._productos + [producto])
        return producto

    def actualizar_producto(self, codigo, nombre, precio, stock):
        actual = self.buscar_producto_por_codigo(codigo)
        if actual is None:
            raise ValueError("No existe un producto con ese código.")
        actualizado = self._crear_producto(actual.codigo, nombre, precio, stock)
        productos = [actualizado if p.codigo == actual.codigo else p
                     for p in self._productos]
        self._guardar_cambios(productos)
        return actualizado

    def eliminar_producto(self, codigo):
        actual = self.buscar_producto_por_codigo(codigo)
        if actual is None:
            raise ValueError("No existe un producto con ese código.")
        self._guardar_cambios([p for p in self._productos if p.codigo != actual.codigo])
        return actual
