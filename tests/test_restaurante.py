"""Pruebas reproducibles con copias temporales: no alteran los JSON de entrega."""
import ast
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

APP = Path(__file__).resolve().parents[1] / "restaurante_app"
sys.path.insert(0, str(APP))
from servicios.archivo_servicio import ArchivoServicio
from servicios.restaurante_servicio import RestauranteServicio
from main import AplicacionRestaurante
from ui.login_view import LoginView
from ui.main_view import MainView


class DatosTemporales(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory(prefix="restaurante15_")
        self.addCleanup(temporal.cleanup)
        self.datos = Path(temporal.name) / "datos"
        shutil.copytree(APP / "datos", self.datos)
        self.archivo = ArchivoServicio(self.datos)
        self.archivo.escribir_json("ventas.json", [])
        self.servicio = self.recargar()

    def recargar(self):
        return RestauranteServicio(ArchivoServicio(self.datos))


class ServicioTest(DatosTemporales):
    def test_acceso_y_consultas_conservados(self):
        self.assertEqual(self.servicio.validar_acceso("ana", "1234").identificacion, "U001")
        for valores in [("", ""), ("ana", "mal"), ("inexistente", "1234")]:
            self.assertIsNone(self.servicio.validar_acceso(*valores))
        self.assertEqual(self.servicio.buscar_producto_por_codigo("P004").nombre, "Coca Cola")
        self.assertTrue(self.servicio.listar_usuarios())

    def test_venta_persistida_y_recuperada_sin_modificar_catalogo(self):
        anteriores = {n: (self.datos / n).read_bytes() for n in ("usuarios.json", "productos.json")}
        venta = self.servicio.registrar_venta(" U001 ", " P001 ")
        self.assertEqual((venta.identificador, venta.usuario_id, venta.producto_codigo), ("V001", "U001", "P001"))
        nueva = self.recargar().listar_ventas()[0]
        self.assertEqual(nueva, venta)
        self.assertEqual(self.archivo.leer_json("ventas.json"), [venta.convertir_a_diccionario()])
        for nombre, contenido in anteriores.items():
            self.assertEqual((self.datos / nombre).read_bytes(), contenido)

    def test_selecciones_invalidas_no_crean_ventas(self):
        antes = (self.datos / "ventas.json").read_bytes()
        for usuario, producto in [("", "P001"), ("U001", ""), ("X", "P001"), ("U001", "X"),
                                  (None, "P001"), ("U001", 1)]:
            with self.subTest(usuario=usuario, producto=producto), self.assertRaises(ValueError):
                self.servicio.registrar_venta(usuario, producto)
        self.assertEqual(self.servicio.cantidad_ventas(), 0)
        self.assertEqual((self.datos / "ventas.json").read_bytes(), antes)

    def test_fallo_guardado_no_produce_exito_parcial(self):
        antes = (self.datos / "ventas.json").read_bytes()
        with patch("servicios.archivo_servicio.os.replace", side_effect=PermissionError("Prueba")):
            with self.assertRaisesRegex(ValueError, "No se pudo guardar"):
                self.servicio.registrar_venta("U001", "P001")
        self.assertEqual(self.servicio.cantidad_ventas(), 0)
        self.assertEqual((self.datos / "ventas.json").read_bytes(), antes)
        self.assertEqual(list(self.datos.glob("*.tmp")), [])
        self.assertEqual(self.servicio.registrar_venta("U001", "P001").identificador, "V001")

    def test_numeracion_sin_colisiones_despues_de_reinicio_y_huecos(self):
        venta = self.servicio.registrar_venta("U001", "P001").convertir_a_diccionario()
        venta["identificador"] = "V020"
        self.archivo.escribir_json("ventas.json", [venta])
        servicio = self.recargar()
        self.assertEqual(servicio.registrar_venta("U001", "P002").identificador, "V021")
        self.assertEqual(self.recargar().registrar_venta("U001", "P003").identificador, "V022")

    def test_historial_conservado_tras_editar_y_eliminar_producto(self):
        self.servicio.registrar_venta("U001", "P001")
        self.servicio.actualizar_producto("P001", "Nuevo nombre", "9", "1")
        self.servicio.eliminar_producto("P001")
        self.assertEqual(self.recargar().listar_ventas()[0].producto_nombre, "Hamburguesa")
        with self.assertRaisesRegex(ValueError, "no existe"):
            self.servicio.registrar_venta("U001", "P001")

    def test_datos_danados_se_informan_y_no_se_borran(self):
        for contenido in ("{mal", "{}", "[1]", '[{"identificador":"V001"}]'):
            with self.subTest(contenido=contenido):
                (self.datos / "ventas.json").write_text(contenido, encoding="utf-8")
                with self.assertRaises(ValueError):
                    self.recargar()
                self.assertEqual((self.datos / "ventas.json").read_text(encoding="utf-8"), contenido)

    def test_ventas_duplicadas_o_fecha_invalida_se_rechazan_al_cargar(self):
        venta = self.servicio.registrar_venta("U001", "P001").convertir_a_diccionario()
        self.archivo.escribir_json("ventas.json", [venta, venta])
        with self.assertRaisesRegex(ValueError, "duplicados"):
            self.recargar()
        venta["fecha"] = "2026-02-30"
        self.archivo.escribir_json("ventas.json", [venta])
        with self.assertRaises(ValueError):
            self.recargar()

    def test_crud_productos_y_validaciones_conservados(self):
        self.servicio.registrar_producto("QA", "Ensalada", "4,50", "2")
        self.assertEqual(self.recargar().buscar_producto_por_codigo("QA").precio, 4.5)
        with self.assertRaises(ValueError):
            self.servicio.registrar_producto("QA", "Duplicado", "1", "1")
        for precio, stock in [("nan", "1"), ("-1", "1"), ("2", "1.5"), ("2", "-1")]:
            with self.assertRaises(ValueError):
                self.servicio.actualizar_producto("QA", "No guardar", precio, stock)
        self.assertEqual(self.recargar().buscar_producto_por_codigo("QA").nombre, "Ensalada")
        self.servicio.actualizar_producto("QA", "Ensalada especial", "5", "3")
        self.assertEqual(self.recargar().buscar_producto_por_codigo("QA").stock, 3)
        self.servicio.eliminar_producto("QA")
        self.assertIsNone(self.recargar().buscar_producto_por_codigo("QA"))

    def test_archivo_ausente_no_se_reemplaza(self):
        (self.datos / "ventas.json").unlink()
        with self.assertRaisesRegex(ValueError, "ventas.json"):
            self.recargar()
        self.assertFalse((self.datos / "ventas.json").exists())


class InterfazTest(DatosTemporales):
    def ejecutar_flujo(self, accion):
        with patch("main.ArchivoServicio", return_value=ArchivoServicio(self.datos)):
            app = AplicacionRestaurante()
        app.root.attributes("-alpha", 0)
        errores = []
        app.root.report_callback_exception = lambda tipo, valor, traza: errores.append(valor)
        def flujo():
            try:
                accion(app)
            except Exception as error:
                errores.append(error)
            finally:
                app.root.destroy()
        app.root.after(20, flujo)
        app.ejecutar()
        if errores:
            raise errores[0]

    def iniciar(self, app):
        login = app.vista_actual
        login.usuario_entry.insert(0, "ana")
        login.contrasena_entry.insert(0, "1234")
        login.boton_ingresar.invoke()
        app.root.update()
        self.assertIsInstance(app.vista_actual, MainView)
        return app.vista_actual

    def test_login_navegacion_usuarios_y_cierre(self):
        def flujo(app):
            login = app.vista_actual
            login.boton_ingresar.invoke()
            self.assertIn("Ingrese", login.mensaje_error.cget("text"))
            vista = self.iniciar(app)
            vista.boton_usuarios.invoke()
            filas = [vista.tabla_usuarios.item(f, "values") for f in vista.tabla_usuarios.get_children()]
            self.assertIn(("U001", "ana", "ana"), filas)
            self.assertNotIn("1234", str(filas))
            vista.boton_cerrar.invoke()
            self.assertIsInstance(app.vista_actual, LoginView)
        self.ejecutar_flujo(flujo)

    def test_boton_delega_actualiza_limpia_y_recupera_tras_cerrar(self):
        def flujo(app):
            vista = self.iniciar(app)
            vista.boton_ventas.invoke()
            self.assertEqual(str(vista.usuario_venta_combo.cget("state")), "readonly")
            self.assertEqual(str(vista.producto_venta_combo.cget("state")), "readonly")
            self.assertEqual(app.restaurante_servicio.cantidad_ventas(), 0)
            vista.boton_registrar_venta.invoke()
            self.assertIn("Seleccione un usuario", vista.mensaje_venta.get())
            vista.usuario_venta_combo.current(0)
            vista.boton_registrar_venta.invoke()
            self.assertIn("Seleccione un producto", vista.mensaje_venta.get())
            vista.producto_venta_combo.current(0)
            servicio = app.restaurante_servicio
            with patch.object(servicio, "registrar_venta", wraps=servicio.registrar_venta) as registrar:
                vista.boton_registrar_venta.invoke()
                registrar.assert_called_once_with("U001", "P001")
            self.assertIn("guardada correctamente", vista.mensaje_venta.get())
            self.assertEqual(len(vista.tabla_ventas.get_children()), 1)
            self.assertIn("Ventas: 1", vista.etiqueta_estado.cget("text"))
            self.assertEqual(vista.usuario_venta_combo.get(), "")
            self.assertEqual(vista.producto_venta_combo.get(), "")
            self.assertEqual(self.recargar().cantidad_ventas(), 1)
        self.ejecutar_flujo(flujo)
        def reinicio(app):
            vista = self.iniciar(app)
            vista.boton_ventas.invoke()
            self.assertEqual(vista.tabla_ventas.item("V001", "values")[2], "P001 · Hamburguesa")
        self.ejecutar_flujo(reinicio)

    def test_error_de_guardado_visible_sin_fila_fantasma(self):
        def flujo(app):
            vista = self.iniciar(app)
            vista.boton_ventas.invoke()
            vista.usuario_venta_combo.current(0)
            vista.producto_venta_combo.current(0)
            with patch("servicios.archivo_servicio.os.replace", side_effect=PermissionError()):
                vista.boton_registrar_venta.invoke()
            self.assertIn("No se pudo guardar", vista.mensaje_venta.get())
            self.assertEqual(vista.tabla_ventas.get_children(), ())
            self.assertTrue(vista.producto_venta_combo.get())
            self.assertEqual(self.recargar().cantidad_ventas(), 0)
        self.ejecutar_flujo(flujo)

    def test_catalogo_vacio_deshabilita_venta(self):
        self.archivo.escribir_json("productos.json", [])
        def flujo(app):
            vista = self.iniciar(app)
            vista.boton_ventas.invoke()
            self.assertTrue(vista.boton_registrar_venta.instate(["disabled"]))
            self.assertIn("Se necesitan", vista.mensaje_venta.get())
        self.ejecutar_flujo(flujo)

    def test_botones_productos_y_selectores_refrescan_catalogo(self):
        def flujo(app):
            vista = self.iniciar(app)
            vista.boton_productos.invoke()
            for entrada, valor in zip(vista.entradas_producto(), ("QA", "Ensalada", "4,50", "3")):
                entrada.delete(0, "end")
                entrada.insert(0, valor)
            vista.botones_accion["Registrar"].invoke()
            self.assertIn("registrado y guardado", vista.mensaje_producto.get())
            vista.boton_ventas.invoke()
            self.assertIn("QA · Ensalada", vista.opciones_productos)
            vista.boton_productos.invoke()
            vista.producto_codigo_entry.insert(0, "QA")
            vista.botones_accion["Cargar por código"].invoke()
            self.assertEqual(vista.producto_nombre_entry.get(), "Ensalada")
            vista.producto_nombre_entry.delete(0, "end")
            vista.producto_nombre_entry.insert(0, "Ensalada especial")
            vista.botones_accion["Actualizar"].invoke()
            self.assertEqual(self.recargar().buscar_producto_por_codigo("QA").nombre, "Ensalada especial")
            with patch("ui.main_view.messagebox.askyesno", return_value=False):
                vista.botones_accion["Eliminar"].invoke()
            self.assertIsNotNone(self.recargar().buscar_producto_por_codigo("QA"))
            with patch("ui.main_view.messagebox.askyesno", return_value=True):
                vista.botones_accion["Eliminar"].invoke()
            self.assertIsNone(self.recargar().buscar_producto_por_codigo("QA"))
            vista.boton_ventas.invoke()
            self.assertNotIn("QA", vista.opciones_productos.values())
        self.ejecutar_flujo(flujo)

    def test_ventana_minima_y_desplazamiento_de_ventas(self):
        for _ in range(25):
            self.servicio.registrar_venta("U001", "P001")
        def flujo(app):
            app.root.geometry("940x620")
            vista = self.iniciar(app)
            vista.boton_ventas.invoke()
            app.root.update()
            self.assertLess(vista.tabla_ventas.yview()[1], 1)
            controles = [vista.usuario_venta_combo, vista.producto_venta_combo,
                         vista.boton_registrar_venta, vista.etiqueta_mensaje_venta,
                         vista.tabla_ventas, vista.etiqueta_estado, vista.boton_cerrar,
                         vista.etiqueta_total_ventas]
            self.comprobar_geometria(app, controles)
            vista.boton_productos.invoke()
            app.root.update()
            controles = [*vista.entradas_producto(), *vista.botones_accion.values(), vista.etiqueta_mensaje]
            self.comprobar_geometria(app, controles)
        self.ejecutar_flujo(flujo)

    def comprobar_geometria(self, app, controles):
        for control in controles:
            self.assertTrue(control.winfo_ismapped())
            padre = control.master
            while padre is not app.root:
                self.assertLessEqual(control.winfo_rooty() + control.winfo_height(), padre.winfo_rooty() + padre.winfo_height())
                self.assertGreaterEqual(control.winfo_rooty(), padre.winfo_rooty())
                self.assertLessEqual(control.winfo_rootx() + control.winfo_width(), padre.winfo_rootx() + padre.winfo_width())
                self.assertGreaterEqual(control.winfo_rootx(), padre.winfo_rootx())
                padre = padre.master


class EstructuraTest(unittest.TestCase):
    def test_ui_sin_persistencia_y_sin_eventos_avanzados(self):
        for archivo in APP.rglob("*.py"):
            arbol = ast.parse(archivo.read_text(encoding="utf-8-sig"))
            for nodo in ast.walk(arbol):
                if isinstance(nodo, ast.Call):
                    if isinstance(nodo.func, ast.Attribute):
                        self.assertNotIn(nodo.func.attr, ("bind", "bind_all"))
                        if "ui" in archivo.parts:
                            self.assertNotIn(nodo.func.attr, ("leer_json", "escribir_json", "open", "write_text"))
                    if isinstance(nodo.func, ast.Name) and "ui" in archivo.parts:
                        self.assertNotEqual(nodo.func.id, "open")
                    for kw in nodo.keywords:
                        if kw.arg == "command":
                            self.assertNotIsInstance(kw.value, ast.Call)

    def test_arranque_desde_otra_carpeta(self):
        codigo = f'''import sys
sys.path.insert(0, {str(APP)!r})
from main import AplicacionRestaurante
app = AplicacionRestaurante()
app.root.attributes('-alpha', 0)
app.root.after(20, app.root.destroy)
app.ejecutar()
'''
        with tempfile.TemporaryDirectory() as carpeta:
            resultado = subprocess.run([sys.executable, "-B", "-c", codigo], cwd=carpeta,
                                       capture_output=True, text=True, timeout=15)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
