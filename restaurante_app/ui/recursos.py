"""Recursos de presentación desde assets; no accede a los datos del negocio."""
from pathlib import Path
import tkinter as tk


def cargar_imagen(master, nombre):
    ruta = Path(__file__).resolve().parent.parent / "assets" / nombre
    return tk.PhotoImage(master=master, file=str(ruta))
