# CIC — Reportes PDF

**Proyecto:** CIC — Centro de Inteligencia Comercial  
**Versión documentada:** CIC v1  
**Tipo de documento:** Especificación funcional y técnica de reportes  
**Estado:** Reconstrucción basada en el código actual  
**Última actualización:** 05/10/2026  

---

## 1. Propósito

Este documento describe el sistema de generación de reportes PDF de CIC v1.

El objetivo es dejar explícito:

- qué información recibe el reporte;
- qué modelos intervienen;
- de dónde proviene cada indicador;
- qué cálculos se realizan;
- qué gráficas se generan;
- cómo se compone el documento;
- cómo se aplican encabezados, pies y control documental;
- cómo se almacena o envía;
- qué dependencias externas existen;
- qué reglas deben protegerse durante mantenimiento o migración.

El documento se basa en el código actual, principalmente en:

```text
modelo/exceles_modelo.py
modelo/reporte_pdf/distribucion_clientes.py
modelo/reporte_pdf/servicio_cliente_modelo.py
modelo/reporte_pdf/tipo_clientes.py
modelo/resumen_movilidad_modelo.py
modelo/kilometraje_modelo.py
modelo/cobertura_cartera_modelo.py
```

---

# 2. Objetivo funcional del reporte

El reporte busca proporcionar una vista consolidada del desempeño de un vendedor durante un mes y año determinados.

La implementación actual integra información de:

```text
Ventas
Presupuesto
Metas
Ventas por segmento
Evolución mensual
Clientes
Movilidad
Planeación
Visitas
Cobertura
Demostraciones
Prospectos
Oportunidades
```

Por lo tanto, el PDF actual debe entenderse como un:

> **Reporte de seguimiento estratégico del personal comercial**

y no únicamente como un reporte de ventas.

---

# 3. Entrada principal

La generación utiliza principalmente:

```text
vendedor
mes
año
```

Conceptualmente:

```text
Vendedor
   +
Mes
   +
Año
   │
   ▼
generar_pdf_reporte()
```

Estos parámetros determinan el periodo y vendedor cuyos indicadores se incorporarán.

---

# 4. Componente principal

La generación está concentrada principalmente en:

```text
modelo/exceles_modelo.py
```

mediante:

```text
generar_pdf_reporte()
```

También existe:

```text
generar_pdf_reporte_boton()
```

asociado al flujo de generación desde interfaz.

`ExcelesModelo` concentra actualmente responsabilidades de:

- consulta de ventas;
- metas/presupuesto;
- preparación de datos;
- gráficas;
- construcción PDF;
- formato;
- envío por correo.

Esta concentración está documentada como deuda arquitectónica en `architecture.md`.

---

# 5. Pipeline general

```text
Vendedor + Mes + Año
          │
          ▼
   Consultas de datos
          │
          ├── ventas
          ├── presupuesto
          ├── metas
          ├── categorías
          ├── clientes
          ├── movilidad
          ├── planeación
          ├── actividades
          └── oportunidades
          │
          ▼
     Transformaciones
          │
          ├── totales
          ├── diferencias
          ├── cumplimiento
          ├── acumulados
          ├── porcentajes
          └── agrupaciones
          │
          ▼
        Gráficas
          │
          ▼
       ReportLab
          │
          ├── tablas
          ├── imágenes
          ├── encabezados
          ├── pie
          └── control documental
          │
          ▼
          PDF
          │
          ├── archivo / descarga
          └── correo SMTP
```

---

# 6. Fuentes de información

## Ventas

Principalmente:

```text
dev_Detalle_Corregida
vw_CategoriaIngresos
```

## Metas

```text
Metas
```

## Presupuesto

```text
PresupuestoSegmentos
```

## Movilidad

```text
MovilidadRegistro
ResumenMovilidad
```

## Servicio y actividad comercial

```text
Accounts
Activities
Calendars
Opportunities
```

## Usuarios/correo

```text
UsuariosCIC
```

---

# 7. Dependencias Python

El flujo utiliza principalmente:

```text
ReportLab
Pandas
Plotly
Matplotlib
BytesIO
smtplib
email
python-dotenv
```

Las gráficas generadas se convierten a imágenes para poder incorporarlas al documento ReportLab.

---

# 8. Formato del documento

El reporte utiliza:

```text
SimpleDocTemplate
```

de ReportLab.

La implementación observada utiliza orientación:

```text
landscape
```

para disponer de mayor ancho para tablas y gráficas.

La estructura se construye mediante una colección:

```text
story
```

a la que se agregan elementos como:

```text
Paragraph
Spacer
Table
Image
PageBreak
```

Finalmente:

```text
doc.build(...)
```

genera el PDF.

---

# 9. Estructura general observada

El código actual organiza el reporte en al menos dos hojas principales.

```text
HOJA 1
│
├── Título
├── Resumen ventas / presupuesto
├── Comparativo temporal
├── Ventas por segmento
├── Distribución por categoría
└── Principales clientes
       │
       ▼
   PageBreak
       │
HOJA 2
│
├── Resumen de movilidad
└── Indicadores de servicio comercial
```

La composición exacta puede evolucionar, pero esta estructura corresponde a la implementación revisada.

---

# 10. Título principal

El código utiliza el título:

```text
SEGUIMIENTO ESTRATÉGICO DE PERSONAL COMERCIAL
```

acompañado por:

```text
vendedor
mes
año
```

También se conserva información de fecha de generación.

Esto identifica claramente al reporte como documento de seguimiento individual por periodo.

---

# 11. Resumen de ventas

La primera sección contiene una tabla con columnas:

```text
Ventas
Presupuesto
Diferencia
Cumplimiento
```

y filas:

```text
Mensual
Acumulado
```

Conceptualmente:

| Periodo | Ventas | Presupuesto | Diferencia | Cumplimiento |
|---|---:|---:|---:|---:|
| Mensual | venta del mes | presupuesto mes | venta - presupuesto | porcentaje |
| Acumulado | venta acumulada | presupuesto acumulado | diferencia | porcentaje |

---

# 12. Cálculo de diferencia

Conceptualmente:

```text
Diferencia mensual =
Ventas mensuales - Presupuesto mensual
```

y:

```text
Diferencia acumulada =
Ventas acumuladas - Presupuesto acumulado
```

Los valores se muestran en USD.

---

# 13. Cumplimiento

El reporte calcula porcentajes de cumplimiento comparando ventas contra presupuesto.

Conceptualmente:

```text
Cumplimiento =
Ventas
──────────── × 100
Presupuesto
```

Debe conservarse el tratamiento actual de casos sin presupuesto o denominador igual a cero.

Al migrar esta regla no debe suponerse una política distinta sin validar el código y los resultados históricos.

---

# 14. Presupuesto mensual

El reporte obtiene el presupuesto mediante:

```text
PresupuestoModelo
```

incluyendo:

```text
obtener_total_presupuesto_mensual()
```

El resultado se compara con ventas reales del vendedor para el periodo.

---

# 15. Presupuesto acumulado

Se utiliza:

```text
obtener_total_presupuesto_acumulado()
```

para construir el comparativo acumulado.

Esto permite analizar no solamente el mes seleccionado sino el avance dentro del año.

---

# 16. Evolución mensual

El reporte genera una gráfica mediante:

```text
generar_grafica_lineas_ingresos_mensuales_fig()
```

La función recibe información como:

```text
ventas/clases
vendedor
año
mes
metas
periodo anterior
```

El objetivo es mostrar la evolución/comparación temporal de resultados.

---

# 17. Renderizado de gráfica de líneas

La figura se genera primero como objeto gráfico.

Posteriormente:

```text
figura
   │
   ▼
write_image()
   │
   ▼
BytesIO
   │
   ▼
ReportLab Image
```

En el código revisado se utiliza un render de aproximadamente:

```text
1000 x 450 px
```

y después se escala al espacio disponible en el PDF.

Si no existen datos, el reporte utiliza un texto alternativo:

```text
No hay datos gráfica de líneas
```

en lugar de interrumpir la generación.

---

# 18. Ventas por segmento

La primera hoja contiene una tabla:

```text
Ventas por Segmento
```

con comparaciones para:

```text
Mes seleccionado
Año
```

Las columnas observadas incluyen:

```text
Segmento
Importe mes
Cumplimiento mes
Importe año
Cumplimiento año
```

---

# 19. Fuente de ventas por segmento

La información proviene de consultas como:

```text
obtener_categoria_ingresos_reporte()
obtener_categoria_ingresos_anual_reporte()
```

y se relaciona con presupuesto por segmento.

---

# 20. Categorías comerciales

El reporte utiliza categorías derivadas de las clases comerciales.

Entre las observadas:

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

La categorización forma parte de la regla de negocio y no debe modificarse únicamente por motivos visuales.

---

# 21. Gráfica de ventas por categoría

Se genera mediante:

```text
generar_grafica_pastel_categoria()
```

Entrada principal:

```text
df_categoria
mes
año
```

Su propósito es representar visualmente la distribución de ventas por segmento/categoría.

---

# 22. Gráfica de principales clientes

Se genera mediante:

```text
generar_grafica_pastel_top_clientes()
```

Entrada:

```text
vendedor
mes
año
```

El objetivo es mostrar la concentración/distribución de ingresos entre clientes relevantes.

---

# 23. Renderizado de gráficas circulares

Las gráficas se convierten a PNG en memoria mediante:

```text
BytesIO
```

El código revisado utiliza un render aproximado de:

```text
1050 x 600 px
```

para reducir el riesgo de cortar etiquetas laterales.

Posteriormente ambas gráficas se colocan en una tabla de dos columnas:

```text
┌───────────────────────┬───────────────────────┐
│ Ventas por categoría  │ Principales clientes  │
└───────────────────────┴───────────────────────┘
```

Si una figura no está disponible se muestra texto alternativo.

---

# 24. Salto de página

Después del bloque comercial principal se agrega:

```text
PageBreak()
```

para iniciar la segunda sección del reporte.

Esto separa visualmente:

```text
resultados comerciales
```

de:

```text
movilidad / servicio comercial
```

---

# 25. Resumen de movilidad

La segunda hoja consulta:

```text
ResumenMovilidadModelo
```

mediante:

```text
obtener_resumenes_reporte_pdf()
```

También consulta kilometraje:

```text
KilometrajeModelo
```

mediante:

```text
obtener_total_kilometraje_mes()
```

---

# 26. Indicadores de movilidad

La tabla contiene:

```text
Días Hábiles
Total Kilometraje
Promedio Diario Recorrido (Km)
Cantidad Visitas
Tiempo Atención (Hrs)
Promedio Tiempo con Cliente (Hrs)
Promedio Visitas por Día
```

Correspondencias observadas:

```text
DiasHabiles
TotalKilometros
AvgDiarioRecorrido
CantidadVisitas
TiempoDestinadoAtencion
AvgTiempoConCliente
AvgVisitasPorDia
```

---

# 27. Origen del kilometraje

El kilometraje se obtiene de:

```text
MovilidadRegistro
```

mediante:

```text
obtener_total_kilometraje_mes()
```

La tabla de movilidad combina por tanto información de:

```text
ResumenMovilidad
+
MovilidadRegistro
```

---

# 28. Ausencia de datos de movilidad

El reporte contempla explícitamente la ausencia de información.

En ese caso muestra:

```text
Sin datos de movilidad para este período.
```

Esto permite continuar generando el PDF aunque el módulo de movilidad no tenga registros para el vendedor/periodo.

---

# 29. Indicadores de servicio comercial

El reporte consulta:

```text
modelo/reporte_pdf/servicio_cliente_modelo.py
```

para obtener porcentajes y cantidades de diferentes indicadores.

Clase funcional:

```text
ServicioClienteModelo
```

---

# 30. Asistencia vs planeación

Funciones:

```text
get_porcentaje_asistencia_vs_planeacion()
get_cantidad_asistencia()
```

El indicador busca relacionar planeación con asistencia/ejecución observada.

Fuentes involucradas por el modelo:

```text
Calendars
Activities
Accounts
```

según la consulta correspondiente.

La fórmula exacta debe preservarse desde el código y validarse con casos conocidos antes de cualquier reimplementación.

---

# 31. Cobertura de cartera

Funciones:

```text
get_porcentaje_cobertura_cartera()
get_cantidad_cobertura_cartera()
```

La cobertura relaciona la cartera objetivo con la actividad/visitas realizadas.

Fuentes principales:

```text
Accounts
Activities
```

También existe:

```text
modelo/cobertura_cartera_modelo.py
```

para cálculos relacionados.

---

# 32. Visitas comerciales

Porcentaje:

```text
get_porcentaje_visitas_comerciales()
```

Existe también:

```text
get_cantidad_visitas_comerciales()
```

pero en la implementación de `generar_pdf_reporte()` revisada la cantidad utilizada en el PDF proviene de:

```text
ResumenMovilidadModelo.obtener_cantidad_visitas_pdf()
```

y no de `get_cantidad_visitas_comerciales()`.

Este detalle es importante para reproducir exactamente el reporte actual.

---

# 33. Demostraciones PMX

Funciones:

```text
get_porcentaje_demostraciones_pmx()
get_cantidad_demostraciones_pmx()
```

El indicador forma parte del bloque de seguimiento de servicio/actividad comercial.

La definición SQL exacta se encuentra en `servicio_cliente_modelo.py`.

---

# 34. Nuevos clientes

Funciones:

```text
get_porcentaje_nuevos_clientes()
get_cantidad_nuevos_clientes()
```

Fuentes del modelo incluyen:

```text
Accounts
Opportunities
```

La definición de cliente nuevo depende de reglas de fecha/estado y debe mantenerse consistente con los demás módulos.

---

# 35. Nuevos prospectos

Funciones:

```text
get_porcentaje_nuevos_prospectos()
get_cantidad_nuevos_prospectos()
```

El indicador cuantifica la generación/actividad asociada a nuevos prospectos durante el periodo.

---

# 36. Oportunidades

Funciones:

```text
get_porcentaje_oportunidades()
get_cantidad_oportunidades()
```

Fuente principal:

```text
Opportunities
```

El indicador forma parte del seguimiento comercial complementario a las ventas.

---

# 37. Resumen de indicadores de servicio

El bloque reúne:

| Indicador | Porcentaje | Cantidad |
|---|---|---|
| Asistencia vs planeación | `get_porcentaje_asistencia_vs_planeacion()` | `get_cantidad_asistencia()` |
| Cobertura cartera | `get_porcentaje_cobertura_cartera()` | `get_cantidad_cobertura_cartera()` |
| Visitas comerciales | `get_porcentaje_visitas_comerciales()` | `obtener_cantidad_visitas_pdf()` en el PDF actual |
| Demostraciones PMX | `get_porcentaje_demostraciones_pmx()` | `get_cantidad_demostraciones_pmx()` |
| Nuevos clientes | `get_porcentaje_nuevos_clientes()` | `get_cantidad_nuevos_clientes()` |
| Nuevos prospectos | `get_porcentaje_nuevos_prospectos()` | `get_cantidad_nuevos_prospectos()` |
| Oportunidades | `get_porcentaje_oportunidades()` | `get_cantidad_oportunidades()` |

---

# 38. Distribución de clientes

Existe el modelo:

```text
modelo/reporte_pdf/distribucion_clientes.py
```

con:

```text
get_distribucion_clientes()
```

Su objetivo es obtener información de distribución de clientes asociada al vendedor.

La función primero obtiene el identificador del vendedor mediante:

```text
_get_id_vendedor()
```

y después ejecuta la consulta correspondiente.

---

# 39. Actividad por tipo de cliente

Existe:

```text
modelo/reporte_pdf/tipo_clientes.py
```

con:

```text
get_actividad_tipo_cliente()
```

Fuentes principales:

```text
Accounts
Activities
```

El objetivo es analizar actividad según tipo de cliente.

---

# 40. Funciones gráficas adicionales

`ExcelesModelo` contiene también:

```text
generar_grafica_pastel_distribucion_clientes()
generar_grafica_pastel_actividad_tipo_cliente()
```

Estas funciones corresponden al soporte visual para información de clientes/actividad.

La presencia de una función en el modelo no debe interpretarse automáticamente como garantía de que aparezca en todas las versiones o variantes del PDF; la composición efectiva depende de `generar_pdf_reporte()`.

---

# 41. Encabezado y pie

El PDF utiliza una función:

```text
agregar_borde()
```

que se ejecuta tanto para:

```text
onFirstPage
```

como para:

```text
onLaterPages
```

mediante:

```text
doc.build(
    story,
    onFirstPage=agregar_borde,
    onLaterPages=agregar_borde
)
```

Esto permite mantener una presentación consistente entre páginas.

---

# 42. Recursos gráficos de margen

Se cargan desde variables de entorno:

```text
ENCABEZADO_GRIS
ENCABEZADO_ROJO
PIE_ROJO
```

Estas rutas apuntan a imágenes utilizadas para construir la identidad visual del documento.

Históricamente se han utilizado rutas similares a:

```text
C:\MargenesReporte\encabezado_gris.png
C:\MargenesReporte\encabezado_rojo.png
C:\MargenesReporte\pie_rojo.png
```

pero las rutas deben configurarse para cada instalación.

---

# 43. Logotipo

Existe configuración:

```text
LOGO_PDF
```

relacionada con los recursos visuales del reporte.

Su uso exacto debe revisarse junto con la versión activa de `agregar_borde()` cuando se modifique el diseño.

---

# 44. Control documental ISO

El pie/encabezado incorpora valores configurables mediante:

```text
CODIGO_NORMA
REVISION_NORMA
FECHA_APLICACION_NORMA
```

Ejemplo histórico documentado:

```text
Código: FO-C1-CM-06
Revisión: 4.0
Fecha de aplicación: 17 de agosto 2026
```

Estos valores no deberían quedar codificados permanentemente en Python.

La configuración mediante `.env` permite modificarlos sin alterar la lógica del reporte.

---

# 45. Número de página

El diseño incorpora información de página dentro del control documental.

Por tanto, el pie del reporte cumple dos objetivos:

```text
identidad visual
+
control documental
```

Cualquier rediseño debe conservar la legibilidad de:

```text
Código
Revisión
Fecha de aplicación
Página
```

si estos campos continúan siendo requisito organizacional.

---

# 46. Configuración relevante

Variables de entorno relacionadas:

```text
LOGO_PDF

ENCABEZADO_GRIS
ENCABEZADO_ROJO
PIE_ROJO

CODIGO_NORMA
REVISION_NORMA
FECHA_APLICACION_NORMA

CARPETA_REPORTES
CARPETA_DESTINO

CORREO_EMISOR
APP_PASSWORD
CORREO_REPORTES_1
CORREO_REPORTES_2
CORREO_REPORTES_3
```

No todas las variables documentadas históricamente aparecen necesariamente en cada función activa.

Por ejemplo, el envío revisado utiliza explícitamente:

```text
CORREO_REPORTES_1
CORREO_REPORTES_2
```

por lo que `CORREO_REPORTES_3` debe verificarse antes de considerarlo destinatario activo.

---

# 47. Envío por correo

Existen funciones:

```text
enviar_correo_reportes_pdf()
enviar_correos()
```

El envío utiliza:

```text
smtplib
```

y el servidor:

```text
smtp.gmail.com
```

puerto:

```text
587
```

con:

```text
STARTTLS
```

---

# 48. Credenciales de correo

Se cargan mediante:

```text
CORREO_EMISOR
APP_PASSWORD
```

No deben almacenarse directamente en Git.

El código contempla específicamente errores de autenticación SMTP y recomienda verificar estas variables cuando ocurre un fallo.

---

# 49. Destinatarios

`enviar_correo_reportes_pdf()` obtiene destinatarios desde:

```text
CORREO_REPORTES_1
CORREO_REPORTES_2
```

También existe lógica para obtener correos válidos mediante:

```text
obtener_correos_validos()
```

y consultas relacionadas con:

```text
UsuariosCIC
```

Por ello existen al menos dos conceptos:

```text
destinatarios configurados
```

y:

```text
correos obtenidos desde CIC
```

La política final de destinatarios debe verificarse antes de modificar el envío.

---

# 50. Adjuntos

El PDF se adjunta al correo mediante la infraestructura de:

```text
email
```

utilizando el nombre de archivo generado.

Flujo:

```text
PDF
 │
 ▼
mensaje MIME
 │
 ▼
adjunto
 │
 ▼
SMTP
 │
 ▼
destinatarios
```

---

# 51. Almacenamiento

El proyecto contempla variables:

```text
CARPETA_REPORTES
CARPETA_DESTINO
```

para rutas relacionadas con archivos generados.

`CARPETA_DESTINO` aparece directamente en lógica de envío/archivos revisada.

La función exacta de `CARPETA_REPORTES` debe validarse en la versión activa antes de considerarla requisito obligatorio.

---

# 52. Manejo de datos faltantes

El reporte contiene varios mecanismos para evitar fallar cuando una fuente no tiene datos.

Ejemplos:

```text
No hay datos gráfica de líneas
Sin datos gráfica pastel
Sin datos gráfica barras
Sin datos de movilidad para este período.
```

Esta tolerancia es importante.

Un reporte parcial puede ser preferible a impedir completamente la generación cuando falta un indicador no crítico.

---

# 53. Dependencias críticas

La generación puede verse afectada por fallas en:

```text
SQL Server
variables .env
archivos de margen
motor de render de gráficas
ReportLab
sistema de archivos
SMTP
```

No todas impiden necesariamente construir el PDF.

Por ejemplo:

```text
fallo SMTP
```

debería distinguirse conceptualmente de:

```text
fallo generación PDF
```

para evitar considerar que el reporte no fue generado únicamente porque no pudo enviarse.

---

# 54. Riesgo de acoplamiento

Actualmente:

```text
ExcelesModelo
```

participa en:

```text
importación
consultas
gráficas
PDF
correo
```

Esto significa que cambios en funciones aparentemente no relacionadas pueden ocurrir dentro del mismo archivo.

Durante mantenimiento:

1. modificar únicamente el bloque necesario;
2. probar importación si se toca lógica compartida;
3. probar PDF;
4. probar correo si aplica;
5. registrar el cambio en `dev_log.csv`.

---

# 55. Pruebas mínimas del reporte

Cada cambio relevante debería validar al menos:

## Caso normal

```text
vendedor con ventas
presupuesto
movilidad
actividades
clientes
```

## Sin movilidad

El PDF debe seguir generándose.

## Sin ventas en una categoría

Las gráficas/tablas deben manejar valores vacíos.

## Sin presupuesto

No debe producirse división inválida en cumplimiento.

## Sin gráfica

Debe aparecer el fallback correspondiente.

## Vendedor con caracteres especiales

Validar nombres, acentos y longitud.

## Diferentes meses

Especialmente:

```text
enero
diciembre
```

por los cálculos acumulados y comparaciones temporales.

---

# 56. Pruebas visuales

Además de validar datos, debe inspeccionarse:

- títulos;
- márgenes;
- encabezados;
- pie;
- código ISO;
- revisión;
- fecha;
- número de página;
- tablas;
- etiquetas de gráficas;
- saltos de página;
- textos largos;
- alineación;
- imágenes.

Los cambios históricos de septiembre de 2026 relacionados con:

```text
margenes
margenes_acomodados
```

demuestran que la validación visual forma parte importante del mantenimiento de este módulo.

---

# 57. Pruebas de datos

Para un vendedor/mes conocido debe compararse manualmente:

```text
ventas mensual
ventas acumuladas
presupuesto mensual
presupuesto acumulado
cumplimiento
ventas por segmento
kilometraje
cantidad de visitas
indicadores de servicio
```

contra las fuentes SQL correspondientes.

Esto es especialmente importante antes de migrar el reporte a CIC v2.

---

# 58. Contrato funcional para CIC v2

CIC v2 no necesita reproducir la implementación ReportLab actual.

Debe reproducir primero el **contrato de información**.

Conceptualmente:

```text
Reporte vendedor/mes
│
├── Resumen comercial
│   ├── ventas
│   ├── presupuesto
│   ├── diferencia
│   └── cumplimiento
│
├── Evolución
│
├── Segmentos
│
├── Clientes
│
├── Movilidad
│
└── Servicio comercial
    ├── asistencia vs planeación
    ├── cobertura
    ├── visitas
    ├── demostraciones
    ├── nuevos clientes
    ├── nuevos prospectos
    └── oportunidades
```

La tecnología de render puede cambiar sin perder este contrato.

---

# 59. Separación futura recomendada

En una arquitectura futura podría existir:

```text
ReporteService
    │
    ├── SalesMetricsService
    ├── MobilityMetricsService
    ├── CustomerMetricsService
    ├── ReportChartService
    ├── PdfRenderer
    └── EmailService
```

Esto no describe CIC v1.

Es únicamente una posible separación para CIC v2 o una refactorización futura.

---

# 60. Datos vs presentación

Una mejora importante para una futura versión es separar:

```text
ReporteData
```

de:

```text
PdfRenderer
```

Ejemplo conceptual:

```text
SQL / reglas
     │
     ▼
ReporteData
{
  vendedor,
  periodo,
  ventas,
  presupuesto,
  segmentos,
  movilidad,
  servicio
}
     │
     ▼
Renderer
     │
     ├── PDF
     ├── pantalla
     └── exportación futura
```

Esto permitiría validar los datos independientemente del formato visual.

---

# 61. Historial verificable relacionado

El historial Git reconstruido contiene cambios específicos en esta funcionalidad:

```text
04/09/2026 — reporte_update_1
07/09/2026 — margenes
07/09/2026 — margenes_acomodados
```

Además existen tags asociados a:

```text
margenes
margenes_acomodados
```

Estos registros indican una etapa de evolución visual del reporte.

Para el detalle histórico general consultar:

```text
logs/development.md
```

---

# 62. Regla de mantenimiento

Actualizar este documento cuando cambie:

- una sección del PDF;
- un indicador;
- una fórmula;
- una fuente SQL;
- una gráfica;
- una categoría;
- presupuesto/meta;
- movilidad;
- diseño;
- encabezado;
- pie;
- control ISO;
- nombre de archivo;
- ruta de salida;
- destinatarios;
- servidor SMTP;
- estrategia de generación.

El cambio también debe registrarse en:

```text
logs/dev_log.csv
```

Si implica una decisión técnica relevante:

```text
docs/decisions.md
```

---

# 63. Documentos relacionados

```text
README.md
```

Configuración general y variables de entorno.

```text
docs/architecture.md
```

Arquitectura e integraciones.

```text
docs/database.md
```

Origen y estructura de los datos.

```text
docs/modules.md
```

Contexto funcional de ventas, movilidad, planeación y demás módulos.

```text
docs/decisions.md
```

Decisiones técnicas.

```text
logs/development.md
```

Evolución histórica.

```text
logs/dev_log.csv
```

Cambios actuales.

---

# 64. Conclusión

El reporte PDF de CIC v1 es un producto consolidado de varias áreas del sistema.

No debe entenderse como una función aislada de exportación.

Su flujo real es:

```text
ForceSync
+
Ventas reales
+
Metas / presupuesto
+
Movilidad
+
Clientes
+
Actividad comercial
        │
        ▼
Reglas de negocio
        │
        ▼
Indicadores y gráficas
        │
        ▼
ReportLab
        │
        ▼
Seguimiento estratégico
        │
        ├── PDF
        └── correo
```

Esto convierte al reporte en una de las mejores referencias para comprender qué información considera relevante CIC para evaluar el desempeño comercial.

Durante una futura migración, el objetivo principal no debe ser reproducir exactamente el código de `generar_pdf_reporte()`.

El objetivo debe ser:

> **preservar y validar el significado de cada indicador antes de cambiar la forma en que se obtiene o presenta.**
