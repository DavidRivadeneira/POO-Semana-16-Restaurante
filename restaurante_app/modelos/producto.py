"""Conserva los atributos del producto y valida sus datos para la gestión gráfica."""
from math import isfinite


class Producto:
    def __init__(self, codigo, nombre, precio, stock):
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio
        self.stock = stock

    @staticmethod
    def validar_texto(valor, campo):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"El campo {campo} no puede estar vacío.")
        return valor.strip()

    @property
    def codigo(self):
        return self._codigo

    @codigo.setter
    def codigo(self, valor):
        valor = self.validar_texto(valor, "código")
        if hasattr(self, "_codigo") and valor != self._codigo:
            raise ValueError("El código identifica al producto y no se puede cambiar.")
        self._codigo = valor

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = self.validar_texto(valor, "nombre")

    @property
    def precio(self):
        return self._precio

    @precio.setter
    def precio(self, valor):
        if isinstance(valor, bool):
            raise ValueError("El precio debe ser un número válido.")
        try:
            precio = float(valor)
        except (TypeError, ValueError):
            raise ValueError("El precio debe ser un número válido.") from None
        if not isfinite(precio) or precio < 0:
            raise ValueError("El precio debe ser finito y no negativo.")
        self._precio = precio

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, valor):
        if type(valor) is not int or valor < 0:
            raise ValueError("El stock debe ser un entero no negativo.")
        self._stock = valor

    def convertir_a_diccionario(self):
        return {"codigo": self.codigo, "nombre": self.nombre,
                "precio": self.precio, "stock": self.stock}
