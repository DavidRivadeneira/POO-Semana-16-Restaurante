"""Semana 16: CRUD, permisos básicos y eventos reales sobre datos temporales."""
import unittest
from unittest.mock import patch

import test_restaurante as base


class UsuariosServicioTest(base.DatosTemporales):
    def setUp(self):
        super().setUp()
        self.servicio.validar_acceso("ana", "1234")

    def registrar(self, codigo="U002", acceso="luis", rol="Cliente"):
        return self.servicio.registrar_usuario(codigo, "Luis", acceso, "demo123", rol)

    def test_crud_roles_indices_y_reinicio(self):
        self.registrar()
        self.registrar("U003", "mesero", "Empleado")
        self.assertEqual(self.recargar().buscar_usuario_por_identificacion("U003").rol, "Empleado")
        self.servicio.actualizar_usuario("U002", "Luis Pérez", "luis2", "nueva", "Empleado")
        reinicio = self.recargar()
        self.assertIsNone(reinicio.validar_acceso("luis", "demo123"))
        self.assertEqual(reinicio.validar_acceso("luis2", "nueva").nombre, "Luis Pérez")
        self.servicio.eliminar_usuario("U002")
        self.assertIsNone(self.recargar().validar_acceso("luis2", "nueva"))
        self.assertIsNone(self.servicio.buscar_usuario_por_identificacion("U002"))
        self.assertEqual(self.servicio.cantidad_usuarios(), 2)

    def test_campos_roles_duplicados_y_seleccion_invalidos(self):
        self.registrar()
        antes = (self.datos / "usuarios.json").read_bytes()
        casos = [("U003", "", "nuevo", "x", "Cliente"),
                 ("", "Nombre", "nuevo", "x", "Cliente"),
                 ("U003", "Nombre", " ", "x", "Cliente"),
                 ("U003", "Nombre", "nuevo", " ", "Cliente"),
                 ("U003", "Nombre", "nuevo", "x", "Gerente"),
                 ("U003", "Nombre", "nuevo", "x", "Administrador"),
                 ("U002", "Nombre", "nuevo", "x", "Empleado"),
                 ("U003", "Nombre", "luis", "x", "Cliente")]
        for datos in casos:
            with self.subTest(datos=datos), self.assertRaises(ValueError):
                self.servicio.registrar_usuario(*datos)
        for identificacion in (None, "", "U999"):
            with self.assertRaises(ValueError):
                self.servicio.actualizar_usuario(identificacion, "Nombre", "nuevo", "x", "Cliente")
            with self.assertRaises(ValueError):
                self.servicio.eliminar_usuario(identificacion)
        with self.assertRaises(ValueError):
            self.servicio.actualizar_usuario("U002", "Nombre", "ana", "x", "Cliente")
        self.assertEqual((self.datos / "usuarios.json").read_bytes(), antes)

    def test_no_admin_no_sesion_y_cierre_rechazan_operaciones(self):
        self.registrar()
        self.registrar("U003", "mesero", "Empleado")
        for acceso in ("luis", "mesero", None):
            if acceso:
                self.servicio.validar_acceso(acceso, "demo123")
            else:
                self.servicio.cerrar_sesion()
            with self.subTest(acceso=acceso):
                for operacion in (
                    lambda: self.registrar("U004", "nuevo"),
                    lambda: self.servicio.actualizar_usuario("U002", "X", "x", "x", "Cliente"),
                    lambda: self.servicio.eliminar_usuario("U002"),
                    self.servicio.validar_gestion_usuarios,
                ):
                    with self.assertRaisesRegex(ValueError, "Solo el Administrador"):
                        operacion()
        self.assertEqual(self.recargar().cantidad_usuarios(), 3)

    def test_cuenta_administrativa_y_ascenso_protegidos(self):
        self.registrar()
        antes = (self.datos / "usuarios.json").read_bytes()
        for operacion in (
            lambda: self.servicio.eliminar_usuario("U001"),
            lambda: self.servicio.actualizar_usuario("U001", "Ana", "ana", "1234", "Cliente"),
            lambda: self.servicio.actualizar_usuario("U002", "Luis", "luis", "demo123", "Administrador"),
        ):
            with self.assertRaises(ValueError):
                operacion()
        self.assertEqual((self.datos / "usuarios.json").read_bytes(), antes)

    def test_fallos_escritura_conservan_json_memoria_e_indices(self):
        self.registrar()
        antes = (self.datos / "usuarios.json").read_bytes()
        actual = self.servicio.buscar_usuario_por_identificacion("U002")
        with patch("servicios.archivo_servicio.os.replace", side_effect=PermissionError("Prueba")):
            for operacion in (
                lambda: self.registrar("U003", "nuevo"),
                lambda: self.servicio.actualizar_usuario("U002", "Cambio", "cambio", "x", "Empleado"),
                lambda: self.servicio.eliminar_usuario("U002"),
            ):
                with self.assertRaisesRegex(ValueError, "No se pudo guardar"):
                    operacion()
                self.assertEqual((self.datos / "usuarios.json").read_bytes(), antes)
                self.assertIs(self.servicio.buscar_usuario_por_identificacion("U002"), actual)
                self.assertEqual(self.servicio.cantidad_usuarios(), 2)
        self.assertEqual(list(self.datos.glob("*.tmp")), [])
        self.assertEqual(self.servicio.validar_acceso("luis", "demo123"), actual)

    def test_ventas_conservan_historial_del_usuario_eliminado(self):
        self.registrar()
        venta = self.servicio.registrar_venta("U002", "P001")
        self.servicio.actualizar_usuario("U002", "Otro nombre", "otro", "x", "Empleado")
        self.servicio.eliminar_usuario("U002")
        self.assertEqual(self.recargar().listar_ventas(), [venta])
        self.assertEqual(venta.usuario_nombre, "Luis")
        with self.assertRaisesRegex(ValueError, "historial"):
            self.registrar()

    def test_formato_anterior_no_otorga_permisos_y_rol_invalido_se_informa(self):
        datos = self.archivo.leer_json("usuarios.json")
        datos[0].pop("rol")
        self.archivo.escribir_json("usuarios.json", datos)
        self.assertEqual(self.recargar().listar_usuarios()[0].rol, "Cliente")
        datos[0]["rol"] = "Inválido"
        self.archivo.escribir_json("usuarios.json", datos)
        with self.assertRaisesRegex(ValueError, "rol"):
            self.recargar()
        self.assertEqual(self.archivo.leer_json("usuarios.json"), datos)


class UsuariosInterfazTest(base.DatosTemporales):
    ejecutar_flujo = base.InterfazTest.ejecutar_flujo
    iniciar = base.InterfazTest.iniciar
    comprobar_geometria = base.InterfazTest.comprobar_geometria

    def completar(self, vista, codigo="U002", nombre="Luis", acceso="luis", clave="demo123", rol="Cliente"):
        for entrada, valor in zip(vista.entradas_usuario(), (codigo, nombre, acceso, clave)):
            entrada.delete(0, "end")
            entrada.insert(0, valor)
        vista.usuario_rol_combo.set(rol)

    def tecla(self, app, widget, evento):
        widget.focus_force()
        app.root.update()
        widget.event_generate(evento)
        app.root.update()

    def seleccionar(self, app, vista, codigo):
        vista.tabla_usuarios.selection_set(codigo)
        app.root.update()

    def test_eventos_registro_seleccion_actualizacion_escape_y_reinicio(self):
        def flujo(app):
            vista = self.iniciar(app)
            vista.boton_usuarios.invoke()
            self.completar(vista)
            vista.usuario_rol_combo.set("Empleado")
            vista.usuario_rol_combo.event_generate("<<ComboboxSelected>>")
            app.root.update()
            self.assertEqual(vista.usuario_rol_estado.get(), "Rol seleccionado: Empleado")
            with patch.object(app.restaurante_servicio, "registrar_usuario",
                              wraps=app.restaurante_servicio.registrar_usuario) as registrar:
                self.tecla(app, vista.usuario_contrasena_entry, "<Return>")
                registrar.assert_called_once_with("U002", "Luis", "luis", "demo123", "Empleado")
            self.assertEqual(vista.tabla_usuarios.item("U002", "values"), ("U002", "Luis", "luis", "Empleado"))
            self.assertNotIn("demo123", str(vista.tabla_usuarios.item("U002")))
            with patch.object(app.restaurante_servicio, "buscar_usuario_por_identificacion",
                              wraps=app.restaurante_servicio.buscar_usuario_por_identificacion) as buscar:
                self.seleccionar(app, vista, "U002")
                buscar.assert_called_once_with("U002")
            self.assertEqual(vista.usuario_nombre_entry.get(), "Luis")
            self.assertEqual(vista.usuario_contrasena_entry.get(), "demo123")
            self.assertEqual(vista.usuario_contrasena_entry.cget("show"), "*")
            self.assertTrue(vista.usuario_identificacion_entry.instate(["readonly"]))
            vista.usuario_nombre_entry.delete(0, "end")
            vista.usuario_nombre_entry.insert(0, "Luis Pérez")
            vista.botones_usuario["Actualizar"].invoke()
            app.root.update()
            self.assertEqual(self.recargar().buscar_usuario_por_identificacion("U002").nombre, "Luis Pérez")
            self.seleccionar(app, vista, "U002")
            self.tecla(app, vista.tabla_usuarios, "<Escape>")
            self.assertEqual(vista.tabla_usuarios.selection(), ())
            self.assertIsNone(vista.usuario_id_seleccionado)
            self.assertTrue(all(e.get() == "" for e in vista.entradas_usuario()))
            self.assertEqual(vista.usuario_rol_combo.get(), "Cliente")
            self.assertEqual(app.root.focus_get(), vista.usuario_identificacion_entry)
        self.ejecutar_flujo(flujo)
        def reinicio(app):
            vista = self.iniciar(app)
            vista.boton_usuarios.invoke()
            self.assertEqual(vista.tabla_usuarios.item("U002", "values")[1], "Luis Pérez")
        self.ejecutar_flujo(reinicio)

    def test_botones_confirmacion_cancelacion_y_catalogo_ventas(self):
        def flujo(app):
            vista = self.iniciar(app)
            vista.boton_usuarios.invoke()
            self.completar(vista)
            vista.botones_usuario["Registrar"].invoke()
            self.seleccionar(app, vista, "U002")
            with patch("ui.main_view.messagebox.askyesno", return_value=False) as pregunta:
                vista.botones_usuario["Eliminar"].invoke()
                pregunta.assert_called_once()
            self.assertIsNotNone(self.recargar().buscar_usuario_por_identificacion("U002"))
            vista.boton_ventas.invoke()
            self.assertIn("U002", vista.opciones_usuarios.values())
            vista.boton_usuarios.invoke()
            self.seleccionar(app, vista, "U002")
            with patch("ui.main_view.messagebox.askyesno", return_value=True) as pregunta:
                vista.botones_usuario["Eliminar"].invoke()
                pregunta.assert_called_once()
            app.root.update()
            self.assertIsNone(self.recargar().buscar_usuario_por_identificacion("U002"))
            self.assertNotIn("U002", vista.tabla_usuarios.get_children())
            self.assertIn("Usuarios: 1", vista.etiqueta_estado.cget("text"))
            vista.boton_ventas.invoke()
            self.assertNotIn("U002", vista.opciones_usuarios.values())
        self.ejecutar_flujo(flujo)

    def test_cliente_empleado_sin_menu_ni_gestion_directa(self):
        self.servicio.validar_acceso("ana", "1234")
        for i, rol in enumerate(("Cliente", "Empleado"), 2):
            self.servicio.registrar_usuario(f"U00{i}", rol, rol, "demo", rol)
        def flujo(app):
            for rol in ("Cliente", "Empleado"):
                login = app.vista_actual
                login.usuario_entry.insert(0, rol)
                login.contrasena_entry.insert(0, "demo")
                login.boton_ingresar.invoke()
                vista = app.vista_actual
                self.assertIsNone(vista.boton_usuarios)
                with patch("ui.main_view.messagebox.showerror") as aviso:
                    vista.mostrar_usuarios()
                    aviso.assert_called_once()
                self.assertFalse(hasattr(vista, "tabla_usuarios"))
                vista.boton_productos.invoke()
                vista.boton_ventas.invoke()
                vista.boton_cerrar.invoke()
        self.ejecutar_flujo(flujo)

    def test_admin_protegido_enter_en_seleccion_y_escape_en_boton(self):
        def flujo(app):
            vista = self.iniciar(app)
            vista.boton_usuarios.invoke()
            self.seleccionar(app, vista, "U001")
            for texto in ("Registrar", "Actualizar", "Eliminar"):
                self.assertTrue(vista.botones_usuario[texto].instate(["disabled"]))
            self.tecla(app, vista.usuario_nombre_entry, "<Return>")
            self.assertEqual(self.recargar().cantidad_usuarios(), 1)
            self.tecla(app, vista.botones_usuario["Limpiar"], "<Escape>")
            self.assertEqual(vista.tabla_usuarios.selection(), ())
            self.assertTrue(vista.botones_usuario["Registrar"].instate(["!disabled"]))
        self.ejecutar_flujo(flujo)

    def test_error_visible_conserva_formulario_sin_fila_fantasma(self):
        def flujo(app):
            vista = self.iniciar(app)
            vista.boton_usuarios.invoke()
            vista.botones_usuario["Registrar"].invoke()
            self.assertIn("vacío", vista.mensaje_usuario.get())
            self.completar(vista)
            with patch("servicios.archivo_servicio.os.replace", side_effect=PermissionError()):
                vista.botones_usuario["Registrar"].invoke()
            self.assertIn("No se pudo guardar", vista.mensaje_usuario.get())
            self.assertEqual(vista.usuario_nombre_entry.get(), "Luis")
            self.assertEqual(vista.tabla_usuarios.get_children(), ("U001",))
        self.ejecutar_flujo(flujo)

    def test_atajos_locales_tras_navegar_y_reabrir(self):
        def flujo(app):
            vista = self.iniciar(app)
            for _ in range(3):
                vista.boton_usuarios.invoke()
                vista.boton_productos.invoke()
                self.tecla(app, vista.producto_nombre_entry, "<Return>")
                self.tecla(app, vista.producto_nombre_entry, "<Escape>")
            vista.boton_usuarios.invoke()
            self.completar(vista)
            self.tecla(app, vista.usuario_rol_combo, "<Return>")
            self.assertEqual(self.recargar().cantidad_usuarios(), 2)
            self.assertEqual(vista.tabla_usuarios.get_children(), ("U001", "U002"))
        self.ejecutar_flujo(flujo)

    def test_controles_y_tabla_visibles_en_tamano_minimo(self):
        self.servicio.validar_acceso("ana", "1234")
        for i in range(2, 25):
            self.servicio.registrar_usuario(f"U{i:03}", f"Cliente {i}", f"demo{i}", "demo", "Cliente")
        def flujo(app):
            app.root.geometry("940x620")
            vista = self.iniciar(app)
            vista.boton_usuarios.invoke()
            app.root.update()
            self.comprobar_geometria(app, [*vista.entradas_usuario(), vista.usuario_rol_combo,
                *vista.botones_usuario.values(), vista.tabla_usuarios, vista.etiqueta_total_usuarios,
                vista.etiqueta_mensaje_usuario, vista.etiqueta_estado, vista.boton_cerrar])
            self.assertLess(vista.tabla_usuarios.yview()[1], 1)
            self.assertGreaterEqual(vista.tabla_usuarios.winfo_height(), 100)
        self.ejecutar_flujo(flujo)


if __name__ == "__main__":
    unittest.main(verbosity=2)
