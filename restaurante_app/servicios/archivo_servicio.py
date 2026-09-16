"""Lee y escribe JSON locales; no contiene vistas ni reglas del restaurante."""
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


class ArchivoServicio:
    def __init__(self, carpeta_datos):
        self.carpeta_datos = Path(carpeta_datos)

    def leer_json(self, nombre_archivo):
        ruta = self.carpeta_datos / nombre_archivo
        try:
            with ruta.open("r", encoding="utf-8-sig") as archivo:
                datos = json.load(archivo)
        except (OSError, ValueError) as error:
            raise ValueError(f"No se pudo leer {nombre_archivo}: {error}") from error
        if not isinstance(datos, list) or any(not isinstance(fila, dict) for fila in datos):
            raise ValueError(f"{nombre_archivo} debe contener una lista de registros.")
        return datos

    def escribir_json(self, nombre_archivo, datos):
        ruta = self.carpeta_datos / nombre_archivo
        temporal = None
        try:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            # Completa el archivo nuevo antes de reemplazar el JSON anterior.
            with NamedTemporaryFile(mode="w", encoding="utf-8", dir=ruta.parent,
                                    prefix=nombre_archivo + ".", suffix=".tmp",
                                    delete=False) as archivo:
                temporal = Path(archivo.name)
                json.dump(datos, archivo, ensure_ascii=False, indent=4, allow_nan=False)
                archivo.write("\n")
            os.replace(temporal, ruta)
        except (OSError, ValueError, TypeError) as error:
            raise ValueError(f"No se pudo guardar {nombre_archivo}. "
                             "Revise los permisos y el espacio disponible.") from error
        finally:
            if temporal is not None:
                try:
                    temporal.unlink(missing_ok=True)
                except OSError:
                    # La limpieza no debe ocultar el error de guardado original.
                    pass
