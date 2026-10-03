"""Usuario del restaurante con credenciales didácticas y un rol básico."""


class Usuario:
    ROLES = ("Administrador", "Empleado", "Cliente")
    ROLES_GESTIONABLES = ("Empleado", "Cliente")

    def __init__(self, identificacion, nombre, usuario, contrasena, rol="Cliente"):
        self.identificacion = identificacion
        self.nombre = nombre
        self.usuario = usuario
        self.contrasena = contrasena
        self.rol = rol

    @staticmethod
    def validar_texto(valor, campo):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"El campo {campo} no puede estar vacío.")
        return valor.strip()

    @property
    def identificacion(self):
        return self._identificacion

    @identificacion.setter
    def identificacion(self, valor):
        self._identificacion = self.validar_texto(valor, "identificación")

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = self.validar_texto(valor, "nombre")

    @property
    def usuario(self):
        return self._usuario

    @usuario.setter
    def usuario(self, valor):
        valor = self.validar_texto(valor, "usuario")
        # La clave se mantiene estable para el índice del servicio.
        if hasattr(self, "_usuario") and valor != self._usuario:
            raise ValueError("El nombre de acceso no se puede cambiar.")
        self._usuario = valor

    @property
    def contrasena(self):
        return self._contrasena

    @contrasena.setter
    def contrasena(self, valor):
        self._contrasena = self.validar_texto(valor, "contraseña")

    @property
    def rol(self):
        return self._rol

    @rol.setter
    def rol(self, valor):
        valor = self.validar_texto(valor, "rol")
        if valor not in self.ROLES:
            raise ValueError("El rol debe ser Administrador, Empleado o Cliente.")
        self._rol = valor

    def convertir_a_diccionario(self):
        return {"identificacion": self.identificacion, "nombre": self.nombre,
                "usuario": self.usuario, "contrasena": self.contrasena,
                "rol": self.rol}
