"""Pantalla de acceso: recoge credenciales y solicita su validación al servicio."""
import tkinter as tk
from tkinter import ttk
from ui.recursos import cargar_imagen


class LoginView(tk.Frame):
    def __init__(self, master, restaurante_servicio, al_iniciar_sesion):
        super().__init__(master, bg="#f5f1eb")
        self.restaurante_servicio = restaurante_servicio
        self.al_iniciar_sesion = al_iniciar_sesion
        self.definir_estilos()
        self.construir_interfaz()

    def definir_estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Login.TButton", background="#9a431f", foreground="white",
                         font=("Arial", 11, "bold"), padding=(16, 10))
        estilo.map("Login.TButton", background=[("active", "#773318")])

    def construir_interfaz(self):
        contenedor = tk.Frame(self, bg="white", padx=32, pady=28)
        contenedor.place(relx=0.5, rely=0.5, anchor="center")
        self.logo = cargar_imagen(self, "logo/logo.png")
        tk.Label(contenedor, image=self.logo, bg="white").pack(pady=(0, 10))
        tk.Label(contenedor, text="RESTAURANTE APP", bg="white", fg="#472d23",
                 font=("Arial", 22, "bold")).pack(pady=(0, 8))
        tk.Label(contenedor, text="Inicia sesión para gestionar el restaurante",
                 bg="white", fg="#67594f", font=("Arial", 11)).pack(pady=(0, 22))

        tk.Label(contenedor, text="Usuario", bg="white",
                 font=("Arial", 10, "bold")).pack(anchor="w")
        self.usuario_entry = tk.Entry(contenedor, width=32, font=("Arial", 11))
        self.usuario_entry.pack(fill="x", pady=(5, 14), ipady=4)

        tk.Label(contenedor, text="Contraseña", bg="white",
                 font=("Arial", 10, "bold")).pack(anchor="w")
        self.contrasena_entry = tk.Entry(contenedor, show="*", font=("Arial", 11))
        self.contrasena_entry.pack(fill="x", pady=(5, 10), ipady=4)

        self.mensaje_error = tk.Label(contenedor, text="", bg="white", fg="#b42318",
                                      font=("Arial", 10))
        self.mensaje_error.pack(pady=(0, 10))
        self.boton_ingresar = ttk.Button(contenedor, text="Iniciar sesión",
                                         style="Login.TButton", command=self.iniciar_sesion)
        self.boton_ingresar.pack(fill="x")
        tk.Label(contenedor, text="Acceso de demostración · Semana 15", bg="white",
                 fg="#67594f", font=("Arial", 9)).pack(pady=(16, 0))

    def iniciar_sesion(self):
        usuario = self.usuario_entry.get().strip()
        contrasena = self.contrasena_entry.get().strip()
        if not usuario or not contrasena:
            self.mensaje_error.config(text="Ingrese usuario y contraseña.")
            return
        validado = self.restaurante_servicio.validar_acceso(usuario, contrasena)
        if validado is None:
            self.mensaje_error.config(text="Credenciales incorrectas.")
            return
        self.mensaje_error.config(text="")
        self.al_iniciar_sesion(validado)
