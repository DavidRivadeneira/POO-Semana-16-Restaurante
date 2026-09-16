"""Punto de entrada: servicios compartidos, una ventana y cambio de vistas."""
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from servicios.archivo_servicio import ArchivoServicio
from servicios.restaurante_servicio import RestauranteServicio
from ui.login_view import LoginView
from ui.main_view import MainView


class AplicacionRestaurante:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Restaurante App - Semana 14")
        self.root.geometry("1040x680")
        self.root.minsize(940, 620)

        ruta_base = Path(__file__).resolve().parent
        archivo_servicio = ArchivoServicio(ruta_base / "datos")
        try:
            self.restaurante_servicio = RestauranteServicio(archivo_servicio)
        except ValueError as error:
            messagebox.showerror("No se pudo iniciar el restaurante", str(error), parent=self.root)
            self.root.destroy()
            raise

        self.vista_actual = None
        self.mostrar_login()

    def cambiar_vista(self, nueva_vista):
        # Destruye solamente el Frame anterior y conserva la ventana principal.
        if self.vista_actual is not None:
            self.vista_actual.destroy()
        self.vista_actual = nueva_vista
        self.vista_actual.pack(fill="both", expand=True)

    def mostrar_login(self):
        vista = LoginView(self.root, self.restaurante_servicio,
                          self.mostrar_interfaz_principal)
        self.cambiar_vista(vista)
        vista.usuario_entry.focus_set()

    def mostrar_interfaz_principal(self, usuario_actual):
        vista = MainView(self.root, self.restaurante_servicio,
                         usuario_actual, self.mostrar_login)
        self.cambiar_vista(vista)

    def ejecutar(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = AplicacionRestaurante()
    except ValueError:
        raise SystemExit(1)
    app.ejecutar()
