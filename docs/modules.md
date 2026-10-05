# CIC — Módulos Funcionales

**Proyecto:** CIC — Centro de Inteligencia Comercial  
**Versión documentada:** CIC v1  
**Tipo de documento:** Catálogo funcional y técnico de módulos  
**Estado:** Reconstrucción basada en el código actual  
**Última actualización:** 05/10/2026  

---

## 1. Propósito

Este documento describe CIC v1 desde el punto de vista de sus **módulos funcionales**.

Mientras `architecture.md` explica cómo está construido el sistema y `database.md` explica cómo se organiza la información, este documento responde principalmente a:

> **¿Qué hace cada parte de CIC y qué componentes participan para hacerlo?**

Para cada módulo se documentan, cuando el código lo permite:

- objetivo de negocio;
- acceso desde la navegación;
- controlador;
- vista;
- modelo;
- entradas;
- fuentes de datos;
- procesamiento;
- salidas;
- reglas relevantes;
- dependencias;
- consideraciones de mantenimiento.

La documentación refleja el código revisado. Cuando una intención de negocio no puede demostrarse completamente mediante el repositorio, se indica como interpretación o queda pendiente de validación.

---

# 2. Mapa funcional general

CIC puede dividirse en los siguientes bloques:

```text
CIC
│
├── Autenticación y navegación
│
├── Comportamiento de vendedores
│   └── Cuadrantes Gartner
│
├── Ventas reales
│   ├── Categorías vs ingresos
│   ├── Clases vs ingresos
│   ├── Clases vs cantidad
│   └── Clientes vs ingresos
│
├── Perfiles
│   ├── Ventas mensuales
│   ├── Status de clientes
│   └── Clientes nuevos y activos
│
├── Captura / información complementaria
│   ├── Importación Excel
│   ├── Metas
│   ├── Presupuesto
│   ├── Kilometraje
│   └── Resumen de movilidad
│
├── Rendimiento
│
├── Planeación / seguimiento ForceManager
│
├── Reportes PDF
│
└── Administración y configuración
```

---

# 3. Flujo común de un módulo

Aunque existen excepciones, muchos módulos siguen este patrón:

```text
NavegacionControladorLogin
          │
          ▼
Controlador funcional
          │
     ┌────┴────┐
     ▼         ▼
   Vista     Modelo
     │         │
     │         ▼
     │    SQL Server
     │         │
     └────◄────┘
          │
          ▼
       Streamlit
```

El controlador suele coordinar:

1. filtros de interfaz;
2. consulta de datos;
3. procesamiento;
4. selección de gráfica o tabla;
5. presentación del resultado.

---

# 4. Autenticación

## Objetivo

Controlar el acceso a CIC y obtener la identidad del usuario que utilizará la aplicación.

## Componentes

```text
controlador/navegacion_controlador_login.py
vista/login/login_vista.py
modelo/usuarios_modelo.py
```

## Datos

```text
UsuariosCIC
```

## Estado de sesión

La autenticación se conserva mediante:

```text
st.session_state
```

con valores como:

```text
usuario_autenticado
permisos_usuario
```

## Flujo

```text
Correo / contraseña
        │
        ▼
LoginVista
        │
        ▼
UsuariosModelo
        │
        ▼
UsuariosCIC
        │
        ▼
resultado autenticación
        │
        ▼
st.session_state
        │
        ▼
Navegación autorizada
```

## Consideración

La implementación activa observada debe revisarse respecto al tratamiento de contraseñas, como se documenta en `database.md`.

---

# 5. Navegación y permisos

## Objetivo

Determinar qué módulos puede utilizar cada usuario y cuál se encuentra activo.

## Componente principal

```text
controlador/navegacion_controlador_login.py
```

Clase:

```text
NavegacionControladorLogin
```

## Responsabilidades

- construir navegación;
- mostrar login;
- mostrar pantalla inicial;
- verificar permisos;
- activar módulos;
- cambiar entre vistas;
- coordinar controladores;
- conservar selección mediante `st.session_state`.

## Áreas controladas

```text
Comportamientos
Perfiles
Exceles
Metas
Presupuesto
Administración
Configuración
Kilometraje
Planeación
Resumen de movilidad
Rendimiento
Ventas reales
```

## Dependencia

Este controlador es uno de los componentes más acoplados del sistema.

Un cambio en él debe probar la navegación de varios módulos.

---

# 6. Cuadrantes Gartner

## Objetivo general

Relacionar dos indicadores comerciales para ubicar vendedores dentro de cuadrantes y facilitar la interpretación conjunta de **actividad y resultados**.

Este bloque representa una de las funcionalidades originales de CIC.

## Componentes comunes

### Modelos

```text
modelo/gartner_modelo.py
modelo/vendedores_modelo.py
modelo/vendedores_registrados.py
```

### Vista

```text
vista/vendedores_vista.py
```

### Controladores

```text
controlador/cuadrantesGartner/
```

### Presentación de resultados

```text
controlador/cuadrantesGartner/mostrar_resultados_cuadrantes.py
```

## Patrón común

Los controladores de cuadrantes presentan una estructura similar:

```text
ejecutar_vista_cuadrante()
        │
        ▼
obtener datos
        │
        ▼
_procesar_datos()
        │
        ▼
GartnerModelo
        │
        ▼
clasificación / preparación
        │
        ▼
ResultadosCuadrantes
        │
        ▼
VendedoresVista
```

También existen variantes de ejecución según privilegios:

```text
comparacion_privilegios_completos()
comparacion_privilegios_acotados()
```

---

# 7. Cuadrante — Ventas vs Movilidad

## Controlador

```text
controlador/cuadrantesGartner/vendedores_controlador.py
```

Clase:

```text
VendedoresControlador
```

## Modelos

```text
GartnerModelo
VendedoresModelo
```

## Datos

El código dispone de métodos para combinar:

```text
ventas
kilometraje / movilidad
```

y variantes de datos reales.

## Procesamiento

`GartnerModelo` contiene:

```text
clasificar_vendedor()
clasificar_vendedorReal()
preparar_datos_cuadrante()
preparar_datos_reales_cuadrante()
```

## Resultado

Clasificación del vendedor según la combinación de ambas métricas.

Conceptualmente:

```text
Ventas
   │
   ├──────────────┐
   │              ▼
   │         clasificación
   │              ▲
   └── Movilidad ─┘
```

## Interpretación

El cuadrante permite observar combinaciones como:

```text
ventas altas / movilidad alta
ventas altas / movilidad baja
ventas bajas / movilidad alta
ventas bajas / movilidad baja
```

La clasificación ayuda al análisis; no debe interpretarse automáticamente como una causa del desempeño.

---

# 8. Cuadrante — Ventas ForceManager vs GPS

## Controlador

```text
ventas_gps_controlador.py
```

Clase:

```text
VentasGpsControlador
```

## Modelo

`VendedoresModelo` contiene:

```text
obtener_datos_ventasForce_gps()
```

y `GartnerModelo`:

```text
clasificar_ventasForce_gps()
preparar_cuadrante_ventasForce_gps()
```

## Objetivo

Comparar ventas procedentes del ecosistema ForceManager/ForceSync con una métrica de desplazamiento GPS.

## Resultado

Cuadrante comercial ventas vs GPS.

---

# 9. Cuadrante — Ventas reales vs GPS

## Controlador

```text
ventas_reales_gps_controlador.py
```

Clase:

```text
VentasRealesGpsControlador
```

## Datos

`VendedoresModelo`:

```text
obtener_ventas_reales_cuadrante()
obtener_datos_ventasReales_gps()
```

## Procesamiento

`GartnerModelo`:

```text
clasificar_ventasReales_gps()
preparar_cuadrante_ventasReales_gps()
```

## Fuente de ventas

```text
dev_Detalle_Corregida
```

## Diferencia respecto al cuadrante anterior

El código distingue explícitamente:

```text
ventas ForceManager
```

de:

```text
ventas reales importadas/procesadas
```

Esta distinción debe conservarse al migrar la funcionalidad.

---

# 10. Cuadrante — Visitas vs Movilidad

## Controlador

```text
visitas_movilidad_controlador.py
```

Clase:

```text
VisitaMovilidadControlador
```

## Modelo

`VendedoresModelo`:

```text
obtener_visita_movilidad()
```

`GartnerModelo`:

```text
clasificar_visita_movilidad()
preparar_cuadrante_visitas_movilidad()
```

## Objetivo

Relacionar el volumen de visitas con la movilidad del vendedor.

---

# 11. Cuadrante — Visitas generales vs Movilidad

## Controlador

```text
visitas_general_movilidad_controlador.py
```

Clase:

```text
VisitaGeneralMovilidadControlador
```

## Modelo

`VendedoresModelo`:

```text
obtener_visitas_general()
obtener_visitaGeneral_movilidad()
```

`GartnerModelo`:

```text
preparar_cuadrante_visitas_generales_movilidad()
```

## Consideración

El código diferencia entre:

```text
visitas
```

y:

```text
visitas generales
```

La regla exacta que diferencia ambos conceptos debe mantenerse documentada junto con las consultas correspondientes cuando se formalice la especificación funcional detallada.

---

# 12. Cuadrante — Visitas vs Ventas

## Controlador

```text
visitas_ventas_controlador.py
```

Clase:

```text
VisitaVentasControlador
```

## Modelos

`VendedoresModelo`:

```text
obtener_visita_ventas()
obtener_visita_ventasReales()
```

`GartnerModelo`:

```text
clasificar_visita_ventas()
preparar_cuadrante_visita_ventas()
preparar_cuadrante_visita_ventasReales()
```

## Funcionalidad

El código contempla comparaciones tanto con información comercial de ForceManager como con ventas reales.

Conceptualmente:

```text
Visitas
   │
   ├──────► ventas ForceManager
   │
   └──────► ventas reales
```

---

# 13. Cuadrante — Tareas vs Actividades

## Controlador

```text
tareas_actividades_controlador.py
```

Clase:

```text
TareaActividadControlador
```

## Datos

`VendedoresModelo`:

```text
obtener_tareas()
obtener_actividades()
obtener_tareas_actividades()
```

## Procesamiento

`GartnerModelo`:

```text
clasificar_tareas_actividades()
crear_cuadrante_tareas_actividades()
```

## Objetivo

Relacionar tareas registradas con actividades comerciales.

---

# 14. Cuadrante — Actividades vs Movilidad

## Controlador

```text
actividades_movilidad_controlador.py
```

Clase:

```text
ActividadMovilidadControlador
```

## Datos

`VendedoresModelo`:

```text
obtener_actividades()
obtener_actividades_movilidad()
```

## Procesamiento

`GartnerModelo`:

```text
clasificar_actividades_movilidad()
crear_cuadrante_actividades_movilidad()
```

## Objetivo

Relacionar actividad registrada con desplazamiento/movilidad.

---

# 15. Cuadrante — Tiempo de visitas vs Visitas

## Controlador

```text
tiempos_visitas_controlador.py
```

Clase:

```text
TiemposVisitasControlador
```

## Datos

`VendedoresModelo`:

```text
obtener_tiempo_visitas()
obtener_tiemposVisita_visitas()
```

## Procesamiento

`GartnerModelo`:

```text
clasificar_tiempo_visitas()
crear_cuadrante_tiempos_visitas()
```

## Fuente

El cálculo de tiempos utiliza información asociada a visitas, incluyendo la vista:

```text
vw_Activities
```

## Objetivo

Comparar tiempo destinado a visitas contra cantidad de visitas.

---

# 16. Cuadrante — Tiempo promedio vs Visitas

## Controlador

```text
tiempos_visitas_promedio_controlador.py
```

Clase:

```text
TiemposPromedioVisitasControlador
```

## Datos

`VendedoresModelo`:

```text
obtener_tiempo_promedio_visitas()
obtener_tiemposVisitaPromedio_visitas()
```

## Procesamiento

`GartnerModelo`:

```text
crear_cuadrante_tiemposPromedio_visitas()
```

## Objetivo

Relacionar duración promedio de las visitas con la cantidad de visitas realizadas.

---

# 17. Ventas reales

## Objetivo general

Analizar las ventas importadas y procesadas por CIC desde diferentes perspectivas.

## Controladores

```text
controlador/ventasReales/
```

## Modelo principal

```text
modelo/ventas_reales_modelo.py
```

## Fuentes principales

```text
dev_Detalle_Corregida
vw_CategoriaIngresos
Metas
PresupuestoSegmentos
```

## Navegación observada

```text
Ventas por Proyecto
Ventas por Cliente
Ventas por Clases
Cantidad Clases Vendida
```

---

# 18. Ventas — Categorías vs Ingresos

## Controlador

```text
categoria_ingresos_controlador.py
```

Clase:

```text
CategoriaIngresosControlador
```

## Modelos

```text
VentasRealesModelo
PresupuestoModelo
ExcelesModelo
```

## Vista

```text
CategoriaIngresosVista
```

## Funciones del controlador

```text
obtener_datos_filtrados()
validar_datos()
obtener_datos_totales_filtrados()
obtener_ingresos_mensuales_filtrados()
```

## Datos

Principalmente:

```text
vw_CategoriaIngresos
```

## Regla importante

Las clases de productos se agrupan mediante reglas de categorización comercial.

Entre las categorías observadas:

```text
COMPONENTES
CONSUMIBLES MANUALES
CONSUMIBLES MECANIZADOS LASER
CONSUMIBLES MECANIZADOS OXICORTE
CONSUMIBLES MECANIZADOS PLASMA
CONSUMIBLES MECANIZADOS WATER
MAQUINAS MECANIZADAS
OTROS
POWERMAX
REFACCIONES
SISTEMAS DE CORTE LASER
SISTEMAS DE CORTE PLASMA
```

## Salida

Análisis de ingresos agrupados por categoría, con filtros de vendedor y periodo según la vista/controlador.

---

# 19. Ventas — Clases vs Ingresos

## Controlador

```text
clases_ingresos_controlador.py
```

Clase:

```text
ClasesIngresosControlador
```

## Modelo

```text
VentasRealesModelo
PresupuestoModelo
```

## Vista

```text
ClasesIngresosVista
```

## Operaciones del modelo

Existen consultas diferenciadas para:

```text
general
vendedor
piso
sumatoria
```

Ejemplos:

```text
obtener_clases_ingresos_general()
obtener_clases_ingresos_vendedor()
obtener_clases_ingresos_piso()
obtener_clases_ingresos_vendedor_sumatoria()
obtener_clases_ingresos_piso_sumatoria()
```

## Salida

Distribución de ingresos por clase de producto.

---

# 20. Ventas — Clases vs Cantidad

## Controlador

```text
clases_cantidad_controlador.py
```

Clase:

```text
ClasesCantidadControlador
```

## Modelo

```text
VentasRealesModelo
PresupuestoModelo
```

## Vista

```text
ClasesCantidadVista
```

## Operaciones

```text
obtener_clases_cantidad_general()
obtener_clases_cantidad_vendedor()
obtener_clases_cantidad_piso()
obtener_clases_cantidad_vendedor_sumatoria()
obtener_clases_cantidad_piso_sumatoria()
```

## Salida

Cantidad vendida agrupada por clase.

---

# 21. Ventas — Clientes vs Ingresos

## Controlador

```text
clientes_ingresos_controlador.py
```

Clase:

```text
ClientesIngresosControlador
```

## Modelo

```text
VentasRealesModelo
PresupuestoModelo
```

## Vista

```text
ClientesIngresosVista
```

## Operaciones

```text
obtener_clientes_ingresos_general()
obtener_clientes_ingresos_vendedor()
obtener_clientes_ingresos_piso()
obtener_clientes_ingresos_vendedor_sumatoria()
obtener_clientes_ingresos_piso_sumatoria()
```

## Salida

Ingresos agrupados por cliente.

---

# 22. Importación de ventas Excel

## Objetivo

Incorporar al sistema información de ventas procedente de archivos Excel.

## Componentes

### Controlador

```text
controlador/reportes/exceles_controlador.py
```

### Vista

```text
vista/exceles_vista.py
```

### Modelo

```text
modelo/exceles_modelo.py
```

## Flujo

```text
Archivo Excel
     │
     ▼
ExcelesVista
     │
     ▼
ExcelesControlador
     │
     ▼
ExcelesModelo
     │
     ├── mapear columnas
     ├── validar fechas
     ├── validar vendedores
     ├── obtener tipo de cambio
     ├── transformar datos
     └── insertar
            │
            ▼
dev_Detalle_Corregida
```

## Funciones relevantes

```text
mapear_columnas()
obtener_meses_años_existentes()
validar_fechas_duplicadas()
insertar_detalles()
obtener_vendedores_validos()
```

## Integración externa

```text
Banxico SIE API
```

mediante:

```text
obtener_tipo_cambio()
```

## Riesgo

Este proceso alimenta una tabla crítica utilizada posteriormente por múltiples módulos.

Los cambios en importación deben validarse antes de incorporarse a producción.

---

# 23. Metas

## Objetivo

Registrar y mantener metas comerciales mensuales por vendedor.

## Componentes

```text
controlador/reportes/metas_controlador.py
vista/metas_vista.py
modelo/metas_modelo.py
```

## Datos

```text
Metas
```

## Funciones principales

```text
insertar_meta()
verificar_meta_existente()
obtener_todas_las_metas()
obtener_metas_por_vendedor()
actualizar_meta()
insertar_o_actualizar_meta()
```

## Identidad lógica

```text
NombreVendedor
MesMeta
YearMeta
```

## Flujo

```text
Vendedor
  +
Mes
  +
Año
  +
Valor meta
     │
     ▼
MetasModelo
     │
     ▼
Metas
```

## Consumidores

La información posteriormente se utiliza en:

```text
ventas reales
rendimiento
reportes PDF
```

---

# 24. Presupuesto por segmentos

## Objetivo

Registrar presupuesto comercial por vendedor y segmento.

## Componentes

```text
controlador/reportes/presupuesto_controlador.py
vista/presupuesto_vista.py
modelo/presupuesto_modelo.py
```

## Datos

```text
PresupuestoSegmentos
```

## Segmentos observados

Incluyen campos para:

```text
ConsumibleMecanizadoPlasma
ConsumibleManual
Refacciones
ConsumibleMecanizadoLaser
ConsumibleMecanizadoOxicorte
SisCorteLaser
SisCortePlasma
SisCorteOxyWater
Powermax
Robotica
```

## Funciones

```text
insertar_presupuesto()
verificar_presupuesto_existente()
obtener_todas_los_presupuestos()
obtener_presupuesto_por_vendedor()
actualizar_presupuesto()
insertar_o_actualizar_presupuesto()
obtener_total_presupuesto_anual()
obtener_total_presupuesto_mensual()
obtener_total_presupuesto_acumulado()
obtener_presupuesto_anual_vendedores()
insertar_o_actualizar_todos_los_meses()
```

## Identidad lógica

```text
NombreVendedor
MesPresupuesto
YearPresupuesto
```

---

# 25. Rendimiento

## Objetivo

Comparar resultados comerciales contra referencias de desempeño para obtener métricas por vendedor y periodo.

## Componentes

```text
controlador/rendimiento/rendimiento_controlador.py
vista/rendimiento_vista.py
modelo/rendimiento_modelo.py
```

El controlador también utiliza:

```text
VentasRealesModelo
```

## Datos

```text
dev_Detalle_Corregida
PresupuestoSegmentos
```

y otras métricas comerciales utilizadas por la vista/controlador.

## Funciones del modelo

```text
obtener_venta_mensual_metrica()
obtener_venta_rango_metrica()
obtener_meta_mensual_metrica()
obtener_meta_rango_metrica()
obtener_metricas_rendimiento()
obtener_metricas_rendimiento_rango()
```

## Modalidades

El código distingue:

```text
métrica mensual
```

y:

```text
métrica por rango
```

## Salida

Indicadores de rendimiento presentados mediante Streamlit.

---

# 26. Kilometraje

## Objetivo

Registrar manualmente kilómetros asociados a un vendedor y consultar acumulados mensuales.

## Componentes

```text
controlador/reportes/kilometraje_controlador.py
vista/kilometraje_vista.py
modelo/kilometraje_modelo.py
```

## Datos

```text
MovilidadRegistro
```

## Funciones

```text
obtener_total_kilometraje_mes()
insertar_kilometraje()
obtener_registros_kilometraje()
eliminar_kilometraje()
eliminar_kilometraje_por_id()
```

## Entrada

Conceptualmente:

```text
Vendedor
Kilómetros
Descripción
Fecha de movilidad
```

## Salida

- registros capturados;
- total mensual;
- historial;
- posibilidad de eliminar registros.

---

# 27. Resumen de movilidad

## Objetivo

Registrar indicadores agregados de movilidad y actividad comercial por vendedor y periodo.

## Componentes

```text
controlador/reportes/resumen_movilidad_controlador.py
vista/resumen_movilidad_vista.py
modelo/resumen_movilidad_modelo.py
```

## Datos

```text
ResumenMovilidad
```

## Indicadores observados

```text
Días hábiles
Promedio diario recorrido
Cantidad de visitas
Tiempo destinado a atención
Promedio de tiempo con cliente
Promedio de visitas por día
Mes
Año
Vendedor
```

## Funciones

```text
verificar_resumen_existente()
insertar_resumen()
actualizar_resumen()
insertar_o_actualizar_resumen()
obtener_resumenes()
obtener_resumenes_reporte_pdf()
obtener_cantidad_visitas_pdf()
```

## Consumidor importante

Los datos se utilizan también en la generación de reportes PDF.

---

# 28. Planeación y seguimiento de ForceManager

## Objetivo

Analizar actividad de planeación de vendedores y apoyar el seguimiento del uso de ForceManager.

## Componentes

```text
controlador/reportes/planeacion_controlador.py
modelo/planeacion_modelo.py
```

La vista asociada se utiliza desde la lógica del módulo aunque el controlador no instancia una clase `...Vista` con el mismo patrón que otros módulos.

## Fuentes

```text
Calendars
Accounts
NotificacionesVendedores
StrikesVendedores
```

## Funciones principales

```text
obtener_vendedores_completos()
obtener_actividades_vendedores()
obtener_tabla_completa_actividades()
obtener_detalle_actividades()
obtener_notificaciones()
insertar_notificacion()
insertar_strike()
reiniciar_notificaciones()
obtener_strikes()
obtener_detalle_planeacion()
obtener_actividad_semanal()
notificacion_existente_hoy()
```

## Flujo conceptual

```text
Calendars + Accounts
        │
        ▼
actividad / planeación
        │
        ▼
PlaneacionModelo
        │
        ├── seguimiento
        ├── notificaciones
        └── strikes
```

## Importancia

Este módulo responde a la necesidad histórica de verificar que los vendedores registren actividad en ForceManager.

---

# 29. Perfiles

## Objetivo general

Presentar indicadores descriptivos sobre comportamiento comercial y cartera.

## Modelo

```text
modelo/perfiles_modelo.py
```

## Vista

```text
vista/perfiles_vista.py
```

## Controladores

```text
ventas_mensuales_controlador.py
status_cliente_controlador.py
nuevos_activos_controlador.py
```

---

# 30. Perfil — Ventas mensuales

## Controlador

```text
VentasMensualesControlador
```

## Funciones del modelo

```text
obtener_ventas_mensuales_por_rango()
obtener_cotizaciones_mensuales_por_rango()
obtener_rango_fechas_disponibles()
obtener_ventas_mensuales()
obtener_años_disponibles()
```

## Modalidades

El controlador contiene lógica separada para:

```text
vista por rango
```

y:

```text
vista mensual
```

## Salida

Evolución temporal de ventas/cotizaciones.

---

# 31. Perfil — Status de clientes

## Controlador

```text
StatusClienteControlador
```

## Modelo

```text
PerfilesModelo
```

## Funciones

```text
obtener_status_cliente_general()
obtener_status_cliente_vendedores_seleccionados()
obtener_status_cliente()
```

## Datos

Principalmente información derivada de oportunidades y cuentas según las consultas internas.

## Salida

Distribución/estado de clientes para análisis de cartera.

---

# 32. Perfil — Clientes nuevos y activos

## Controlador

```text
NuevosActivosControlador
```

## Funciones

```text
obtener_nuevos_activos_general()
obtener_nuevos_activos_vendedores_seleccionados()
obtener_nuevos_activos_vendedor()
```

## Regla general observada

Los clientes activos y nuevos se derivan principalmente de:

```text
Accounts
Opportunities
```

considerando estado de venta, año y fecha de creación.

La regla detallada está documentada en `database.md`.

---

# 33. Cobertura de cartera

## Modelo

```text
modelo/cobertura_cartera_modelo.py
```

Clase:

```text
CoberturaCarteraModelo
```

## Función

```text
obtener_cobertura()
```

## Datos

```text
Accounts
Activities
```

## Objetivo

Relacionar cartera de clientes con visitas/actividad realizada.

Conceptualmente:

```text
Clientes de cartera
       │
       ▼
Clientes visitados
       │
       ▼
Cobertura
```

Esta métrica también es utilizada dentro de información de reportes.

---

# 34. Administración

## Objetivo

Gestionar configuraciones administrativas relacionadas con vendedores y su disponibilidad dentro de CIC.

## Componentes

```text
controlador/admin/admin_controlador.py
modelo/admin/admin_modelo.py
```

## Funciones del controlador

```text
_seccion_agregar()
_seccion_tabla()
_seccion_eliminar()
ejecutar_vista_admin()
```

## Funciones del modelo

El modelo trabaja con vendedores de:

```text
ForceManager
Excel / ventas reales
```

y configuraciones regionales.

Funciones observadas:

```text
obtener_vendedores_exceles()
obtener_vendedores_force()

obtener_guardados()

agregar_vendedor_force()
agregar_vendedor_excel()

eliminar_vendedor_force()
eliminar_vendedor_excel()

agregar_vendedor_norte_force()
agregar_vendedor_norte_excel()

agregar_vendedor_bajio_force()
agregar_vendedor_bajio_excel()
```

y operaciones equivalentes de eliminación.

## Persistencia adicional

El modelo contiene:

```text
_leer_json()
_escribir_json()
```

por lo que parte de esta configuración se mantiene en archivos JSON además de consultar SQL Server.

---

# 35. Configuración de usuario

## Controlador

```text
controlador/admin/configuracion_controlador.py
```

Clase:

```text
ConfiguracionControlador
```

## Modelos

```text
AdminModelo
UsuariosModelo
```

## Vista

```text
LoginVista
```

## Funciones

```text
_resetear_modulos()
ejecutar_vista_configuracion()
```

## Objetivo

Gestionar opciones asociadas al usuario/configuración y retornar correctamente al flujo de navegación.

---

# 36. Registro de vendedores por zona

## Modelo

```text
modelo/vendedores_registrados.py
```

## Objetivo

Proporcionar conjuntos de vendedores utilizados por diferentes módulos según origen y zona.

## Grupos observados

### ForceManager

```text
completos
Monclova
Monterrey
Guadalajara
León
Norte
Bajío
```

### Ventas reales

```text
completos
León
Guadalajara
Monclova
Monterrey
Norte
Bajío
```

## Importancia

Este componente influye en qué vendedores pueden aparecer en filtros o comparaciones.

Las listas y reglas regionales deben tratarse como configuración de negocio.

---

# 37. Reportes PDF

## Objetivo

Generar un reporte consolidado por vendedor y periodo.

## Componente principal

```text
modelo/exceles_modelo.py
```

## Componentes auxiliares

```text
modelo/reporte_pdf/distribucion_clientes.py
modelo/reporte_pdf/servicio_cliente_modelo.py
modelo/reporte_pdf/tipo_clientes.py
modelo/cobertura_cartera_modelo.py
modelo/resumen_movilidad_modelo.py
```

## Funciones principales

```text
obtener_datos_vendedor_periodo()
obtener_meta_vendedor()
generar_grafica_lineas_mensual()
generar_grafica_barras_meta()
generar_grafica_pastel_categoria()
generar_grafica_pastel_top_clientes()
generar_grafica_pastel_distribucion_clientes()
generar_grafica_pastel_actividad_tipo_cliente()
generar_pdf_reporte()
enviar_correo_reportes_pdf()
enviar_correos()
generar_pdf_reporte_boton()
```

## Flujo

```text
Ventas
Metas
Movilidad
Clientes
Actividades
Planeación
    │
    ▼
ExcelesModelo + modelos auxiliares
    │
    ├── cálculos
    ├── gráficas
    └── composición
           │
           ▼
        ReportLab
           │
           ▼
           PDF
           │
           ├── descarga / archivo
           └── correo
```

La estructura detallada se documentará en:

```text
docs/reports.md
```

---

# 38. Distribución de clientes para reporte

## Modelo

```text
modelo/reporte_pdf/distribucion_clientes.py
```

## Funciones

```text
_get_id_vendedor()
get_distribucion_clientes()
```

## Objetivo

Obtener información de distribución de clientes asociada a un vendedor para incorporarla al reporte.

---

# 39. Actividad por tipo de cliente

## Modelo

```text
modelo/reporte_pdf/tipo_clientes.py
```

## Funciones

```text
_get_id_vendedor()
get_actividad_tipo_cliente()
```

## Datos

```text
Accounts
Activities
```

## Objetivo

Clasificar o resumir actividad según tipo de cliente para su representación en el reporte.

---

# 40. Indicadores de servicio al cliente

## Modelo

```text
modelo/reporte_pdf/servicio_cliente_modelo.py
```

## Datos

```text
Accounts
Activities
Calendars
Opportunities
```

## Indicadores observados

El modelo calcula porcentajes y cantidades para:

```text
asistencia vs planeación
cobertura de cartera
visitas comerciales
demostraciones PMX
nuevos clientes
nuevos prospectos
oportunidades
```

Funciones de porcentaje:

```text
get_porcentaje_asistencia_vs_planeacion()
get_porcentaje_cobertura_cartera()
get_porcentaje_visitas_comerciales()
get_porcentaje_demostraciones_pmx()
get_porcentaje_nuevos_clientes()
get_porcentaje_nuevos_prospectos()
get_porcentaje_oportunidades()
```

Funciones de cantidad equivalentes:

```text
get_cantidad_asistencia()
get_cantidad_cobertura_cartera()
get_cantidad_visitas_comerciales()
get_cantidad_demostraciones_pmx()
get_cantidad_nuevos_clientes()
get_cantidad_nuevos_prospectos()
get_cantidad_oportunidades()
```

Estos indicadores son reglas de negocio importantes y deben conservarse explícitamente durante una futura migración.

---

# 41. Dependencias entre módulos

Los módulos no son completamente independientes.

Un mapa simplificado es:

```text
Importación Excel
      │
      ▼
dev_Detalle_Corregida
      │
      ├────────► Ventas reales
      │
      ├────────► Rendimiento
      │
      ├────────► Cuadrantes con ventas reales
      │
      └────────► Reportes PDF

Metas ────────────────────────► Ventas / Rendimiento / PDF

Presupuesto ──────────────────► Ventas / Rendimiento

Kilometraje / Movilidad ─────► Cuadrantes / PDF

ForceManager / ForceSync
      │
      ├────────► Cuadrantes
      ├────────► Perfiles
      ├────────► Planeación
      ├────────► Cobertura
      └────────► Reportes PDF
```

---

# 42. Matriz técnica resumida

| Módulo | Controlador principal | Modelo principal | Fuente principal |
|---|---|---|---|
| Login | Navegación | `UsuariosModelo` | `UsuariosCIC` |
| Cuadrantes | `cuadrantesGartner/*` | `GartnerModelo`, `VendedoresModelo` | ForceSync + ventas + movilidad |
| Categorías vs ingresos | `CategoriaIngresosControlador` | `VentasRealesModelo` | `vw_CategoriaIngresos` |
| Clases vs ingresos | `ClasesIngresosControlador` | `VentasRealesModelo` | `dev_Detalle_Corregida` |
| Clases vs cantidad | `ClasesCantidadControlador` | `VentasRealesModelo` | `dev_Detalle_Corregida` |
| Clientes vs ingresos | `ClientesIngresosControlador` | `VentasRealesModelo` | `dev_Detalle_Corregida` |
| Importación | `ExcelesControlador` | `ExcelesModelo` | Excel → SQL |
| Metas | `MetasControlador` | `MetasModelo` | `Metas` |
| Presupuesto | `PresupuestoControlador` | `PresupuestoModelo` | `PresupuestoSegmentos` |
| Rendimiento | `RendimientoControlador` | `RendimientoModelo` | ventas + presupuesto/meta |
| Kilometraje | `KilometrajeControlador` | `KilometrajeModelo` | `MovilidadRegistro` |
| Resumen movilidad | `ResumenMovilidadControlador` | `ResumenMovilidadModelo` | `ResumenMovilidad` |
| Planeación | `PlaneacionControlador` | `PlaneacionModelo` | `Calendars`, `Accounts` |
| Ventas mensuales | `VentasMensualesControlador` | `PerfilesModelo` | `Opportunities` |
| Status clientes | `StatusClienteControlador` | `PerfilesModelo` | `Accounts` / `Opportunities` |
| Nuevos/activos | `NuevosActivosControlador` | `PerfilesModelo` | `Accounts` / `Opportunities` |
| Administración | `AdminControlador` | `AdminModelo` | SQL + JSON |
| PDF | integrado en flujo de reportes | `ExcelesModelo` + auxiliares | múltiples fuentes |

---

# 43. Entradas externas

CIC recibe información desde varias fuentes.

```text
SQL Server / ForceSync
Excel de ventas
Banxico
Captura manual
Configuración JSON
Variables .env
```

## Captura manual

Incluye principalmente:

```text
metas
presupuesto
kilometraje
resumen de movilidad
```

## Automatizada / consulta

Incluye:

```text
ForceManager / ForceSync
tipo de cambio Banxico
```

## Archivo

Incluye:

```text
ventas Excel
```

---

# 44. Salidas del sistema

Los módulos producen diferentes tipos de salida:

```text
gráficas Streamlit
tablas
métricas
cuadrantes
indicadores
registros SQL
PDF
correo electrónico
```

Por lo tanto, CIC no es únicamente una herramienta de visualización; también incorpora captura, procesamiento y generación de documentos.

---

# 45. Reglas de negocio que deben protegerse

Durante mantenimiento o migración deben identificarse y probarse especialmente:

- definición de vendedor válido;
- diferencia ForceManager vs ventas reales;
- asignación de ventas a vendedor;
- vendedores de piso;
- conversión monetaria;
- categorización de clases;
- definición de cliente activo;
- definición de cliente nuevo;
- clasificación de cuadrantes;
- cálculo de movilidad;
- cálculo de visitas;
- tiempo de visita;
- metas mensuales;
- presupuesto por segmento;
- indicadores de servicio;
- notificaciones y strikes;
- filtros por zona;
- filtros por periodo.

Estas reglas constituyen conocimiento de negocio y no deberían quedar únicamente implícitas en Python o SQL.

---

# 46. Consideraciones para pruebas

El orden recomendado para crear pruebas es:

## Nivel 1 — reglas puras

Funciones de:

```text
clasificación de cuadrantes
agrupación
categorización
cálculos porcentuales
```

## Nivel 2 — consultas

Validar resultados conocidos para:

```text
ventas
metas
presupuesto
movilidad
clientes
actividades
```

## Nivel 3 — flujos

```text
importación Excel
generación PDF
login
captura de metas
captura de presupuesto
captura de kilometraje
```

## Nivel 4 — interfaz

Validar navegación y permisos según rol.

---

# 47. Módulos con mayor impacto transversal

## `ExcelesModelo`

Impacta:

```text
importación
ventas
tipo de cambio
gráficas
PDF
correo
```

## `VendedoresModelo`

Impacta principalmente:

```text
cuadrantes
movilidad
visitas
actividades
ventas
GPS
```

## `NavegacionControladorLogin`

Impacta:

```text
acceso
permisos
navegación
activación de módulos
```

## `VentasRealesModelo`

Impacta:

```text
ventas reales
reportes
metas
análisis mensuales
```

Estos componentes requieren pruebas cuidadosas ante modificaciones.

---

# 48. Uso de este documento para CIC v2

Cada sección de este archivo puede convertirse posteriormente en un requisito funcional.

Ejemplo:

```text
CIC v1
"Clases vs ingresos"
        │
        ▼
Requisito funcional
"Consultar ingresos agrupados por clase,
filtrables por vendedor y periodo"
        │
        ▼
CIC v2
API + frontend
```

El objetivo no es migrar literalmente:

```text
controlador + vista + modelo
```

sino preservar:

```text
necesidad
+
regla de negocio
+
resultado esperado
```

---

# 49. Estado de migración futuro

Cuando comience la migración formal, puede añadirse a cada módulo una sección:

```text
Estado CIC v2:
[ ] No evaluado
[ ] Mantener
[ ] Rediseñar
[ ] Reemplazar
[ ] Descartar
[ ] Implementado
[ ] Validado contra CIC v1
```

Actualmente no se asignan esos estados para evitar anticipar decisiones todavía no tomadas.

---

# 50. Mantenimiento

Actualizar `modules.md` cuando:

- se agregue una funcionalidad;
- se elimine un módulo;
- cambie una regla de negocio;
- cambie la fuente de información;
- cambie un controlador;
- cambie el flujo de captura;
- cambie un indicador;
- cambien permisos;
- se migre una funcionalidad a CIC v2.

Toda modificación debe registrarse además en:

```text
logs/dev_log.csv
```

Las decisiones estructurales deben registrarse en:

```text
docs/decisions.md
```

---

# 51. Documentos relacionados

```text
README.md
```

Descripción general e instalación.

```text
docs/architecture.md
```

Arquitectura técnica.

```text
docs/database.md
```

Tablas, vistas y relaciones de datos.

```text
docs/reports.md
```

Especificación detallada de generación de reportes.

```text
docs/decisions.md
```

Decisiones técnicas y arquitectónicas.

```text
logs/development.md
```

Historia del proyecto.

```text
logs/roadmap.md
```

Dirección futura.

---

# 52. Conclusión

CIC v1 no está compuesto únicamente por pantallas independientes.

Sus módulos forman una cadena de información:

```text
captura / sincronización
        │
        ▼
procesamiento
        │
        ▼
reglas de negocio
        │
        ▼
análisis
        │
        ▼
seguimiento
        │
        ▼
reportes
```

Los cuadrantes representan el núcleo histórico de análisis del comportamiento comercial, mientras que los módulos incorporados posteriormente amplían el sistema hacia ventas reales, metas, presupuesto, movilidad, planeación, perfiles, rendimiento y reportes.

La principal recomendación para la evolución del sistema es:

> **Documentar y probar las reglas de negocio antes de trasladar funcionalidades a una nueva arquitectura.**

En CIC v2, la estructura técnica podrá cambiar significativamente, pero los resultados comerciales que CIC v1 ya proporciona deben poder explicarse, reproducirse y validarse.
