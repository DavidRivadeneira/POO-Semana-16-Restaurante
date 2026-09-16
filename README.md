# Restaurante App · Semana 14

**Taller práctico: Organización modular de un sistema orientado a objetos en Python**

**Tema:** Componentes y contenedores con Tkinter.

| Información académica | Dato |
| --- | --- |
| Estudiante | Juan David Rivadeneira Cuascota |
| Universidad | Universidad Estatal Amazónica |
| Asignatura | Programación Orientada a Objetos |
| Docente | Kevin Bolívar Lascano Sánchez |
| Semestre y paralelo | Segundo semestre · F |
| Código del curso | 2626-UEA-L-UFB-030-F |
| Semana | 14 |

## Propósito

Esta versión evoluciona la interfaz gráfica de `restaurante_app` mediante
componentes y contenedores de Tkinter y ttk. Conserva el inicio de sesión y la
consulta de usuarios, e incorpora un formulario y una tabla para **registrar,
cargar por código, actualizar y eliminar productos**.

Los botones utilizan `command=`. La vista recibe datos y presenta resultados;
`RestauranteServicio` valida, ejecuta las operaciones y solicita su persistencia
a `ArchivoServicio`. El objetivo de esta semana es organizar e integrar los
componentes de la interfaz dentro de la arquitectura existente.

## Continuidad con la Semana 13

El proyecto parte de la [Semana 13](https://github.com/DavidRivadeneira/POO-Semana-13-Restaurante).
Su historial de Git se conserva como base de esta evolución. Se mantienen los
modelos `Producto` y `Usuario`, los nombres de sus atributos, los datos iniciales,
las vistas `LoginView` y `MainView`, los servicios y el flujo de una sola ventana.

| Elemento | Semana 13 | Evolución en Semana 14 |
| --- | --- | --- |
| Acceso | Usuario y contraseña mediante LoginView. | Mismo acceso y validación mediante el servicio. |
| Navegación | Barra de opciones y panel de consulta. | Menú lateral, sección activa, panel Inicio y conteos actualizados. |
| Productos | Consulta mediante filas de texto. | Formulario, cinco botones y tabla con desplazamiento. |
| Usuarios | Consulta de identificación, nombre y usuario. | Mismos datos en una tabla; las contraseñas no se muestran. |
| Persistencia | Lectura de productos y usuarios desde JSON. | Se añade escritura de productos después de registrar, actualizar o eliminar. |
| Modelos | Producto con código, nombre, precio y stock; Usuario con datos de acceso. | Mismos atributos; Producto incorpora conversión a diccionario y mantiene estable su código. |
| Ventas | Opción pendiente. | Continúa identificada como pendiente, fuera del alcance de esta semana. |

Los JSON iniciales son iguales a los de Semana 13. Cada entrega tiene su propia
carpeta de datos: las operaciones realizadas aquí no modifican las semanas anteriores.
Se retira el atajo de Enter del login para utilizar exclusivamente los botones
mediante `command=` en esta actividad.

## Estructura

```text
Repositorio/
├── README.md
├── .gitignore
└── restaurante_app/
    ├── README.md
    ├── main.py
    ├── datos/
    │   ├── productos.json
    │   └── usuarios.json
    ├── modelos/
    │   ├── __init__.py
    │   ├── producto.py
    │   └── usuario.py
    ├── servicios/
    │   ├── __init__.py
    │   ├── archivo_servicio.py
    │   └── restaurante_servicio.py
    └── ui/
        ├── __init__.py
        ├── login_view.py
        └── main_view.py
```

| Capa o archivo | Responsabilidad |
| --- | --- |
| `modelos/producto.py` | Representar y validar código, nombre, precio y stock; convertir el producto a diccionario. |
| `modelos/usuario.py` | Conservar los datos del usuario y las credenciales de demostración. |
| `servicios/archivo_servicio.py` | Leer y escribir archivos JSON; informar errores de lectura y guardado. |
| `servicios/restaurante_servicio.py` | Construir objetos, validar acceso, listar y contar registros, consultar productos y ejecutar su gestión. |
| `ui/login_view.py` | Capturar credenciales, solicitar su validación y mostrar mensajes de acceso. |
| `ui/main_view.py` | Organizar navegación, formulario, botones, tablas y mensajes; solicitar las operaciones al servicio. |
| `main.py` | Preparar servicios, crear una única instancia de Tk y cambiar entre vistas con un único mainloop. |

## Componentes y contenedores

| Componente | Uso real en la aplicación |
| --- | --- |
| `Tk` | Ventana principal compartida entre el login y el panel. |
| `Frame` | Menú lateral, contenido, barra de estado, resumen, acciones y área de tabla. |
| `LabelFrame` | Agrupar el formulario de productos, el listado y las instrucciones del panel Inicio. |
| `Label` | Títulos, campos, instrucciones, conteos y mensajes de resultado. |
| `Entry` y `ttk.Entry` | Capturar credenciales y código, nombre, precio y stock del producto. |
| `ttk.Button` | Navegar y activar cada operación mediante `command=`. |
| `ttk.Treeview` | Mostrar productos y usuarios en filas y columnas, sin edición directa. |
| `ttk.Scrollbar` | Desplazamiento vertical y horizontal de las tablas. |
| `StringVar` | Mantener el mensaje visible del formulario. |
| `ttk.Style` | Unificar colores, tipografía y presentación de botones y tablas. |
| `messagebox` | Confirmar una eliminación e informar que Ventas está pendiente. |

Se usa `pack()` para distribuir las áreas grandes y `grid()` para alinear el
formulario, el listado y las barras de desplazamiento en sus propios contenedores.
El login conserva `place()` para centrar su panel. **No se mezclan `pack()` y
`grid()` entre widgets hermanos dentro del mismo contenedor.**

La ventana se puede redimensionar, con un mínimo de 940 × 620. Se conserva la
paleta del restaurante de Semana 13. La sección activa se distingue en el menú,
los resultados aparecen junto al formulario y los conteos se actualizan después
de modificar productos. No se requieren imágenes ni paquetes externos.

## Operaciones de productos

| Botón | Acción |
| --- | --- |
| **Registrar** | Crear un producto con código único, nombre, precio y stock válidos. Guardarlo y refrescar la tabla. |
| **Cargar por código** | Consultar el código escrito y completar el formulario con los datos existentes. No modifica el JSON. |
| **Actualizar** | Modificar nombre, precio y stock del producto identificado por el código escrito. Guardar y refrescar la tabla. |
| **Eliminar** | Consultar el producto, pedir confirmación, eliminarlo, guardar y limpiar el formulario. Cancelar conserva los datos. |
| **Limpiar** | Vaciar los campos y dejar stock en cero. No modifica los registros. |

Para consultar o editar se escribe el código y se utiliza **Cargar por código**.
El código identifica al producto y no se renombra. La tabla presenta registros;
seleccionar una fila no carga ni modifica el formulario.

El servicio convierte los textos numéricos recibidos desde la interfaz y utiliza
las validaciones del modelo. Rechaza campos obligatorios vacíos, códigos duplicados,
precios negativos o no finitos y stock negativo o no entero. El precio admite punto
o coma decimal. Cargar, actualizar o eliminar un código inexistente informa el error.
El precio cero y el stock cero son válidos, conservando las reglas del modelo anterior.

## Flujo y persistencia

```text
main.py → LoginView → RestauranteServicio valida el acceso → MainView
                                                           ├── Inicio: resumen
                                                           ├── Usuarios: consulta
                                                           ├── Productos: gestión
                                                           └── Cerrar sesión → LoginView

Formulario → Botón → RestauranteServicio → Producto valida los datos
                                       → ArchivoServicio guarda productos.json
                                       → lista e índice actualizados
                                       → tabla, conteos y mensaje actualizados
```

- `productos.json` conserva `codigo`, `nombre`, `precio` y `stock`.
- `usuarios.json` conserva `identificacion`, `nombre`, `usuario` y `contrasena`.
  En esta semana solo se consulta; la aplicación no lo modifica.
- Las listas contienen objetos. Los índices por usuario de acceso y por código
  de producto facilitan las consultas y se reconstruyen al cargar los JSON.
- Después de registrar, actualizar o eliminar, el servicio guarda la nueva
  colección antes de reemplazar la lista e índice en memoria.
- `ArchivoServicio` escribe primero un archivo temporal junto al original y lo
  reemplaza cuando termina. Si el guardado falla, se informa el error y se conserva
  el estado anterior de productos en memoria. Los archivos temporales se limpian.
- Al reiniciar, se recuperan los cambios guardados. Las rutas se calculan desde
  la ubicación del proyecto; no dependen de una ruta personal ni de la carpeta de la terminal.
- Un JSON ausente, dañado o con registros inválidos detiene el inicio con un aviso;
  no se reemplaza automáticamente por una colección vacía.

El acceso es una simulación pedagógica con credenciales locales. Esta entrega
no añade gestión de usuarios, ventas completas, nuevas entidades ni base de datos.
Tampoco incorpora `bind()`, doble clic, eventos personalizados de teclado o mouse,
edición de celdas ni carga automática desde una fila de la tabla.

## Ejecución

Requisitos: **Python 3.10 o superior con Tkinter** y entorno gráfico disponible.
Se verificó con Python 3.14.3 en Windows. No es necesario instalar dependencias.

Desde la raíz del repositorio:

```powershell
python restaurante_app/main.py
```

En Windows también se puede utilizar `py restaurante_app/main.py`. Si la terminal
ya está dentro de `restaurante_app`, ejecutar `python main.py`.

**Acceso de demostración:** usuario `ana`, contraseña `1234`.

Los datos iniciales conservan `U001 - ana` y los productos `P001 - Hamburguesa`
($3.50, stock 8), `P002 - Jugo natural` ($1.50, stock 12) y `P003 - Salchipapa`
($2.75, stock 5).

## Comprobación desde la interfaz

Esta secuencia puede realizarse en una copia del proyecto para conservar los datos
iniciales. Registrar, actualizar y eliminar sí modifican `productos.json`.

| Paso | Acción | Resultado esperado |
| --- | --- | --- |
| 1 | Abrir main.py e intentar acceder con campos vacíos y con una contraseña incorrecta. | Mensajes visibles; permanece en el login. |
| 2 | Acceder con `ana / 1234` y abrir Usuarios. | Panel principal y tabla con U001, ana y usuario ana. |
| 3 | Abrir Productos; escribir `P001` y pulsar Cargar por código. | Formulario con Hamburguesa, precio 3.5 y stock 8. |
| 4 | Pulsar Limpiar; completar `P014`, `Ensalada`, `4.50`, `6` y pulsar Registrar. | Cuatro productos; Ensalada aparece en la tabla y se confirma el guardado. |
| 5 | Intentar registrar otra vez P014 o actualizarlo con stock `1.5`. | Mensaje de validación; datos anteriores intactos. |
| 6 | Cargar P014; cambiar nombre a `Ensalada especial`, precio a `5.25` y stock a `9`; pulsar Actualizar. | Tabla y archivo reflejan los cambios. |
| 7 | Cerrar la aplicación, abrirla, iniciar sesión y cargar P014. | Se recuperan Ensalada especial, 5.25 y 9. |
| 8 | Pulsar Eliminar y cancelar; después repetir y confirmar. | Cancelar conserva el registro; confirmar lo elimina y actualiza tabla y conteo. |
| 9 | Cerrar, volver a abrir y consultar P014. | Se informa que ya no existe; permanecen los tres productos iniciales. |
| 10 | Pulsar Cerrar sesión. | Regreso al login dentro de la misma ventana. |

Se comprobaron las operaciones con botones reales de Tkinter, los reinicios,
validaciones, cancelación de eliminación, consulta de usuarios, tablas vacías y
con desplazamiento, conteos y manejo de un fallo de guardado. Las comprobaciones
utilizaron datos temporales y conservaron los JSON iniciales de la entrega.

## Correspondencia con los criterios de evaluación

| Criterio | Evidencia |
| --- | --- |
| Evolución y arquitectura | Base de Semana 13 conservada; mismas capas, modelos y datos iniciales. |
| Gestión de productos | Registro, carga por código, actualización y eliminación mediante RestauranteServicio y JSON. |
| Componentes, contenedores y experiencia de usuario | Menú lateral, Frame, LabelFrame, formulario, botones, tablas, barras y mensajes organizados. |
| Ejecución y funcionamiento | Acceso, navegación, usuarios, operaciones, refresco y persistencia; una ventana principal. |
| Documentación | Propósito, continuidad, estructura, componentes, operaciones, persistencia, ejecución y secuencia de comprobación. |

## Referencias y entrega

- Consigna y rúbrica de Semana 14 publicadas en el EVA.
- Guía y diapositivas de Semana 14: Componentes y contenedores.
- [Proyecto docente de Semana 14](https://github.com/kevin10lascano-sketch/Clase-Semana-14-POO).
- [Explorador de componentes de Semana 14.1](https://github.com/kevin10lascano-sketch/Clase-Semana-14.1-POO).

Se revisaron y ejecutaron los dos ejemplos docentes. Su organización se adapta
al dominio del restaurante y a los datos del proyecto anterior.

**Enlace de entrega:** [POO-Semana-14-Restaurante](https://github.com/DavidRivadeneira/POO-Semana-14-Restaurante).
En el EVA se entrega únicamente el enlace del repositorio público de Semana 14.
