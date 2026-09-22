"""Una venta sencilla relaciona un usuario, un producto y una fecha."""
from dataclasses import dataclass
from datetime import date
import re


@dataclass(frozen=True)
class Venta:
    identificador: str
    usuario_id: str
    producto_codigo: str
    fecha: str
    usuario_nombre: str
    producto_nombre: str

    def __post_init__(self):
        for campo in self.__dataclass_fields__:
            valor = getattr(self, campo)
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(f"El campo {campo} de la venta no puede estar vacío.")
            object.__setattr__(self, campo, valor.strip())
        if re.fullmatch(r"V[0-9]+", self.identificador) is None:
            raise ValueError("El identificador de venta debe tener el formato V001.")
        if int(self.identificador[1:]) < 1:
            raise ValueError("El número de venta debe ser positivo.")
        if date.fromisoformat(self.fecha).isoformat() != self.fecha:
            raise ValueError("La fecha de venta debe tener el formato AAAA-MM-DD.")

    def convertir_a_diccionario(self):
        return {campo: getattr(self, campo) for campo in self.__dataclass_fields__}
