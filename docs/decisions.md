# CIC --- Registro de Decisiones Técnicas

**Proyecto:** CIC --- Centro de Inteligencia Comercial\
**Versión documentada:** CIC v1\
**Tipo de documento:** Registro de decisiones técnicas / ADR
simplificado\
**Estado:** Reconstrucción retrospectiva y registro vigente\
**Última actualización:** 05/10/2026

------------------------------------------------------------------------

## 1. Propósito

Este documento registra decisiones técnicas y arquitectónicas relevantes
de CIC.

A diferencia de otros documentos:

-   `development.md` explica **cómo evolucionó** el proyecto;
-   `architecture.md` explica **cómo está construido**;
-   `database.md` explica **cómo utiliza los datos**;
-   `modules.md` explica **qué hace cada módulo**;
-   `reports.md` explica **cómo funciona el sistema de reportes**;

`decisions.md` responde principalmente a:

> **¿Qué decisión se tomó, por qué se tomó, qué consecuencias tiene y
> sigue siendo válida?**

Debido a que CIC comenzó a documentarse formalmente después de varios
años/etapas de desarrollo, no todas las razones históricas pueden
reconstruirse con certeza.

Por ello, este documento evita inventar justificaciones que no estén
respaldadas por el código, el historial Git o el conocimiento confirmado
del proyecto.

------------------------------------------------------------------------

# 2. Estados de una decisión

Cada decisión utiliza uno de los siguientes estados:

``` text
PROPUESTA
ACEPTADA
REEMPLAZADA
DESCARTADA
PENDIENTE DE VALIDAR
```

## ACEPTADA

La decisión forma parte de la implementación actual o ha sido confirmada
como criterio vigente.

## REEMPLAZADA

Fue válida en algún momento, pero otra decisión tomó su lugar.

## DESCARTADA

Se evaluó o utilizó temporalmente y ya no debe aplicarse.

## PROPUESTA

Es una alternativa futura todavía no aprobada.

## PENDIENTE DE VALIDAR

La implementación permite observar la decisión, pero no existe
suficiente información para reconstruir con certeza su motivación
histórica.

------------------------------------------------------------------------

# 3. Nivel de evidencia

Para distinguir hechos de reconstrucciones se utilizan tres niveles.

### Confirmada

Existe evidencia directa en código, historial Git o información
confirmada del proyecto.

### Reconstruida

La decisión puede inferirse razonablemente a partir de la implementación
actual, pero no existe un ADR histórico que explique el razonamiento
original.

### Propuesta

No forma parte de CIC v1. Se registra únicamente para evaluación futura.

------------------------------------------------------------------------

# ADR-001 --- Utilizar Python y Streamlit para CIC v1

**Estado:** ACEPTADA\
**Evidencia:** Confirmada por implementación\
**Ámbito:** Arquitectura / interfaz

## Contexto

CIC requería una interfaz para consultar y analizar información
comercial, aplicar filtros y presentar gráficas, tablas e indicadores.

## Decisión

Desarrollar CIC v1 como aplicación Python utilizando:

``` text
Streamlit
```

como framework principal de interfaz.

## Evidencia observable

El punto de entrada:

``` text
main.py
```

configura Streamlit y delega la navegación a:

``` text
NavegacionControladorLogin
```

Las vistas utilizan componentes Streamlit para filtros, tablas,
mensajes, navegación y visualizaciones.

## Consecuencias positivas

-   integración directa con Pandas;
-   desarrollo rápido de interfaces analíticas;
-   facilidad para trabajar con Python y SQL;
-   integración sencilla con Plotly, Matplotlib y ReportLab;
-   una sola base tecnológica para análisis y presentación.

## Consecuencias / limitaciones

-   cada interacción puede provocar reruns;
-   se requiere `st.session_state` para conservar estado;
-   navegación compleja aumenta el tamaño del controlador principal;
-   frontend y backend permanecen fuertemente ligados.

## Vigencia

Se mantiene para CIC v1.

No debe asumirse automáticamente como decisión para CIC v2.

------------------------------------------------------------------------

# ADR-002 --- Organizar CIC v1 mediante una separación MVC

**Estado:** ACEPTADA\
**Evidencia:** Confirmada por estructura; motivación histórica
reconstruida\
**Ámbito:** Organización del código

## Contexto

A medida que CIC incorporó más funcionalidades fue necesario separar
presentación, coordinación y acceso/procesamiento de información.

## Decisión

Organizar el proyecto principalmente en:

``` text
controlador/
modelo/
vista/
```

## Implementación

Ejemplo conceptual:

``` text
Vista
  │
  ▼
Controlador
  │
  ▼
Modelo
  │
  ▼
SQL Server
```

## Consecuencias positivas

-   facilita localizar componentes;
-   separa gran parte de la interfaz del acceso a datos;
-   permite agrupar controladores por dominio;
-   mejora la comprensión frente a una aplicación completamente
    monolítica en un solo archivo.

## Limitaciones observadas

La separación no es estricta.

Por ejemplo:

``` text
exceles_modelo.py
```

también contiene generación de gráficas, PDF y correo.

## Vigencia

Mantener la estructura existente en CIC v1.

No realizar una refactorización completa únicamente para convertirla en
MVC puro.

------------------------------------------------------------------------

# ADR-003 --- Mantener CIC v1 como monolito modular

**Estado:** ACEPTADA\
**Evidencia:** Reconstruida a partir de la arquitectura actual\
**Ámbito:** Arquitectura

## Contexto

CIC integra interfaz, consultas, análisis, importación, reportes y
correo dentro de una misma aplicación.

## Decisión observada

Mantener estas capacidades dentro de un único proyecto/proceso Python,
organizadas en módulos internos.

## Resultado

``` text
Streamlit
   │
Controladores
   │
Modelos
   │
SQL / archivos / APIs / PDF / SMTP
```

## Consecuencias positivas

-   despliegue relativamente simple;
-   acceso directo a modelos y datos;
-   menor infraestructura;
-   apropiado para la evolución histórica de una herramienta interna.

## Consecuencias negativas

-   mayor acoplamiento;
-   componentes grandes;
-   dificultad para reutilizar lógica desde otros clientes;
-   interfaz y reglas de negocio no están completamente desacopladas.

## Vigencia

Aceptada para mantenimiento de CIC v1.

La evolución hacia una arquitectura API + frontend corresponde a CIC v2
y debe decidirse/documentarse en ese proyecto.

------------------------------------------------------------------------

# ADR-004 --- Utilizar SQL Server `ForceSyncDB_Worker` como fuente central de datos

**Estado:** ACEPTADA\
**Evidencia:** Confirmada\
**Ámbito:** Datos

## Contexto

CIC necesita combinar información comercial procedente del ecosistema
ForceSync/ForceManager con información complementaria administrada por
CIC.

## Decisión

Utilizar:

``` text
Microsoft SQL Server
ForceSyncDB_Worker
```

como base central consultada por CIC v1.

## Entidades principales observadas

``` text
Users
Accounts
Activities
Calendars
Opportunities
dev_Detalle_Corregida
Metas
PresupuestoSegmentos
MovilidadRegistro
ResumenMovilidad
UsuariosCIC
```

## Consecuencias

CIC depende fuertemente del esquema y disponibilidad de esta base.

Los cambios de columnas, vistas o reglas SQL pueden afectar múltiples
módulos.

## Vigencia

Aceptada para CIC v1.

------------------------------------------------------------------------

# ADR-005 --- Centralizar la creación de conexiones SQL

**Estado:** ACEPTADA\
**Evidencia:** Confirmada\
**Ámbito:** Datos / infraestructura

## Decisión

Centralizar la creación de conexiones en:

``` text
modelo/db_connection.py
```

mediante:

``` text
DatabaseConnection
```

## Configuración

La conexión obtiene parámetros desde `.env`.

## Consecuencia positiva

Evita mantener cadenas de conexión diferentes en cada modelo.

## Limitación

Las consultas SQL continúan distribuidas entre numerosos modelos.

## Vigencia

Aceptada.

------------------------------------------------------------------------

# ADR-006 --- Utilizar autenticación integrada de Windows para la conexión activa a SQL Server

**Estado:** ACEPTADA EN IMPLEMENTACIÓN\
**Evidencia:** Confirmada por código\
**Ámbito:** Seguridad / datos

## Decisión observada

La cadena activa utiliza:

``` text
Trusted_Connection=yes
```

## Contexto histórico

El código también conserva una alternativa comentada basada en:

``` text
UID
PWD
```

pero no es la implementación activa revisada.

## Consecuencias

La aplicación depende de que el usuario/proceso de Windows tenga
permisos adecuados en SQL Server.

## Nota

Las variables:

``` text
USERNAME
PASSWORD
```

se cargan actualmente, aunque no participan en la cadena activa.

## Vigencia

Aceptada en CIC v1 mientras el entorno de despliegue continúe utilizando
autenticación Windows.

------------------------------------------------------------------------

# ADR-007 --- Mantener configuración y secretos fuera del código mediante `.env`

**Estado:** ACEPTADA\
**Evidencia:** Confirmada\
**Ámbito:** Configuración / seguridad

## Decisión

Utilizar variables de entorno para:

``` text
SQL Server
Banxico
correo
rutas
recursos PDF
control documental
```

## Ejemplos

``` text
SERVER
DATABASE
DRIVER

BANXICO
SERIE_BANXICO

CORREO_EMISOR
APP_PASSWORD

ENCABEZADO_GRIS
ENCABEZADO_ROJO
PIE_ROJO

CODIGO_NORMA
REVISION_NORMA
FECHA_APLICACION_NORMA
```

## Consecuencias positivas

-   evita hardcodear secretos;
-   permite diferentes instalaciones;
-   facilita modificar rutas y configuración sin cambiar Python.

## Requisito

El `.env` real no debe versionarse.

## Recomendación vigente

Mantener un:

``` text
.env.example
```

sin valores sensibles.

------------------------------------------------------------------------

# ADR-008 --- Incorporar ventas reales mediante archivos Excel

**Estado:** ACEPTADA\
**Evidencia:** Confirmada por implementación e historia reconstruida\
**Ámbito:** Integración de datos

## Contexto

La información necesaria para analizar ventas reales no se obtiene
exclusivamente de ForceManager.

## Decisión

Crear un módulo de importación de archivos Excel y almacenar los datos
procesados en:

``` text
dev_Detalle_Corregida
```

## Flujo

``` text
Excel
  │
  ▼
validación
  │
  ▼
normalización
  │
  ▼
tipo de cambio
  │
  ▼
dev_Detalle_Corregida
```

## Consecuencias positivas

-   permite incorporar ventas reales al análisis;
-   hace posible comparar ventas reales contra movilidad, metas y
    presupuesto;
-   desacopla parte del análisis del registro comercial de ForceManager.

## Consecuencias

La calidad de numerosos módulos depende de la correcta importación.

`dev_Detalle_Corregida` se convierte en una estructura crítica.

## Vigencia

Aceptada en CIC v1.

------------------------------------------------------------------------

# ADR-009 --- Utilizar Banxico para el tipo de cambio

**Estado:** ACEPTADA\
**Evidencia:** Confirmada\
**Ámbito:** Integración externa / reglas comerciales

## Decisión

Consultar la API SIE de Banxico para obtener tipo de cambio durante el
procesamiento de ventas.

## Configuración

``` text
BANXICO
SERIE_BANXICO
```

## Consecuencia

La importación depende parcialmente de disponibilidad/configuración de
un servicio externo.

## Riesgo

Debe existir manejo adecuado cuando no sea posible obtener el valor
requerido.

## Vigencia

Aceptada para el proceso actual.

------------------------------------------------------------------------

# ADR-010 --- Conservar ventas ForceManager y ventas reales como conceptos distintos

**Estado:** ACEPTADA\
**Evidencia:** Confirmada por código\
**Ámbito:** Dominio comercial

## Contexto

CIC contiene funciones y cuadrantes diferentes para:

``` text
ventas ForceManager
```

y:

``` text
ventas reales
```

## Decisión

No tratar ambas fuentes como si fueran necesariamente equivalentes.

## Evidencia

Existen métodos diferenciados como:

``` text
obtener_datos_ventasForce_gps()
obtener_ventas_reales_cuadrante()
obtener_datos_ventasReales_gps()
```

y variantes de cuadrantes.

## Consecuencia

Los indicadores deben indicar claramente qué fuente de venta utilizan.

## Vigencia

Regla crítica.

Debe preservarse explícitamente durante CIC v2 hasta que exista una
decisión formal de unificación.

------------------------------------------------------------------------

# ADR-011 --- Utilizar cuadrantes para relacionar actividad y resultados

**Estado:** ACEPTADA\
**Evidencia:** Confirmada por origen funcional e implementación\
**Ámbito:** Analítica comercial

## Contexto

La dirección necesitaba entender comportamientos donde vendedores podían
presentar combinaciones muy diferentes entre resultados y
actividad/movilidad.

## Decisión

Utilizar comparaciones bidimensionales y clasificación por cuadrantes
para analizar relaciones como:

``` text
Ventas vs Movilidad
Ventas vs GPS
Visitas vs Ventas
Visitas vs Movilidad
Actividades vs Movilidad
Tareas vs Actividades
Tiempo vs Visitas
```

## Principio

El cuadrante ayuda a observar patrones.

No demuestra causalidad.

Por ejemplo:

``` text
ventas altas + movilidad baja
```

no debe interpretarse automáticamente como comportamiento incorrecto.

## Vigencia

Funcionalidad central de CIC v1.

------------------------------------------------------------------------

# ADR-012 --- Utilizar `st.session_state` para conservar sesión y navegación

**Estado:** ACEPTADA\
**Evidencia:** Confirmada\
**Ámbito:** Interfaz

## Contexto

Streamlit reejecuta el script ante interacciones.

## Decisión

Mantener estado mediante:

``` text
st.session_state
```

## Información almacenada

Incluye:

``` text
autenticación
permisos
módulo activo
selecciones
```

## Consecuencia

El estado de interfaz depende directamente del mecanismo de Streamlit.

## Limitación

El crecimiento de múltiples flags:

``` text
mostrar_*
```

incrementa la complejidad de navegación.

## Vigencia

Aceptada para CIC v1.

------------------------------------------------------------------------

# ADR-013 --- Administrar metas mensuales dentro de CIC

**Estado:** ACEPTADA\
**Evidencia:** Confirmada\
**Ámbito:** Dominio comercial

## Decisión

Registrar metas por:

``` text
Vendedor
Mes
Año
```

en:

``` text
Metas
```

## Motivo funcional

Permitir comparar resultados reales contra objetivos comerciales.

## Consecuencia

CIC deja de ser únicamente un consumidor de ForceManager y mantiene
información propia de negocio.

## Vigencia

Aceptada.

------------------------------------------------------------------------

# ADR-014 --- Administrar presupuesto por segmentos dentro de CIC

**Estado:** ACEPTADA\
**Evidencia:** Confirmada\
**Ámbito:** Dominio comercial

## Decisión

Mantener presupuesto por vendedor, periodo y segmento en:

``` text
PresupuestoSegmentos
```

## Consecuencia

Permite comparar ventas por segmento contra objetivos específicos.

## Identidad lógica utilizada

``` text
NombreVendedor
MesPresupuesto
YearPresupuesto
```

## Vigencia

Aceptada.

------------------------------------------------------------------------

# ADR-015 --- Incorporar movilidad manual/complementaria

**Estado:** ACEPTADA\
**Evidencia:** Confirmada\
**Ámbito:** Dominio comercial

## Contexto

El análisis comercial requiere información de desplazamiento que no
depende únicamente de las entidades núcleo de ForceSync.

## Decisión

Mantener:

``` text
MovilidadRegistro
ResumenMovilidad
```

para registrar kilometraje e indicadores agregados.

## Consecuencia

La movilidad se convierte en una fuente complementaria utilizada por
cuadrantes y reportes.

## Vigencia

Aceptada en CIC v1.

------------------------------------------------------------------------

# ADR-016 --- Mantener relaciones de negocio por nombre de vendedor en varias estructuras

**Estado:** ACEPTADA EN LEGACY / REVISAR PARA V2\
**Evidencia:** Confirmada por consultas\
**Ámbito:** Modelo de datos

## Contexto

Varias estructuras utilizan:

``` text
NombreVendedor
Vendedor
RepresentanteDeVentas
SalesRepName
```

como referencia lógica.

## Decisión observada

Relacionar información de diferentes fuentes mediante nombres cuando no
se utiliza un identificador canónico compartido.

## Consecuencias

Riesgo de inconsistencias por:

-   acentos;
-   espacios;
-   mayúsculas;
-   cambios de nombre;
-   abreviaturas;
-   duplicados;
-   vendedores de piso.

## Vigencia

No se recomienda realizar una migración masiva de CIC v1 únicamente por
este motivo si el sistema permanece estable.

Para CIC v2 debe evaluarse un:

``` text
vendedor_id
```

canónico.

------------------------------------------------------------------------

# ADR-017 --- Mantener reglas especiales para vendedores de piso

**Estado:** ACEPTADA\
**Evidencia:** Confirmada por lógica del proyecto\
**Ámbito:** Dominio / datos

## Contexto

El análisis de ventas distingue entre vendedores convencionales y
registros asociados a piso.

## Decisión

Mantener tratamientos específicos durante:

``` text
importación
consultas
ventas reales
filtros
```

## Consecuencia

No debe eliminarse esta distinción durante una refactorización sin
validar primero el significado comercial de los registros.

## Vigencia

Regla de negocio crítica.

------------------------------------------------------------------------

# ADR-018 --- Generar reportes PDF con ReportLab

**Estado:** ACEPTADA\
**Evidencia:** Confirmada\
**Ámbito:** Reportes

## Decisión

Utilizar:

``` text
ReportLab
```

para componer reportes PDF.

## Implementación

Se utilizan:

``` text
SimpleDocTemplate
Paragraph
Table
Image
Spacer
PageBreak
```

## Consecuencias positivas

-   control detallado de tablas y layout;
-   posibilidad de encabezados/pies personalizados;
-   generación local sin servicio externo.

## Consecuencias

El código de presentación del reporte es relativamente extenso y está
acoplado a `ExcelesModelo`.

## Vigencia

Aceptada para CIC v1.

No obliga a CIC v2 a utilizar la misma librería.

------------------------------------------------------------------------

# ADR-019 --- Incorporar control documental en los reportes

**Estado:** ACEPTADA\
**Evidencia:** Confirmada\
**Ámbito:** Reportes / documentación organizacional

## Decisión

Incorporar en el PDF información como:

``` text
Código
Revisión
Fecha de aplicación
Página
```

y recursos gráficos:

``` text
ENCABEZADO_GRIS
ENCABEZADO_ROJO
PIE_ROJO
```

## Configuración

``` text
CODIGO_NORMA
REVISION_NORMA
FECHA_APLICACION_NORMA
```

## Consecuencia

El diseño visual del PDF no es únicamente decorativo; contiene
información de control documental.

## Vigencia

Aceptada mientras continúe siendo requisito organizacional.

------------------------------------------------------------------------

# ADR-020 --- Aplicar encabezado y pie en todas las páginas del PDF

**Estado:** ACEPTADA\
**Evidencia:** Confirmada\
**Ámbito:** Reportes

## Decisión

Utilizar:

``` text
onFirstPage=agregar_borde
onLaterPages=agregar_borde
```

## Consecuencia

Todas las páginas mantienen identidad y control documental consistente.

## Historial relacionado

El historial Git contiene:

``` text
07/09/2026 — margenes
07/09/2026 — margenes_acomodados
```

y tags equivalentes.

## Vigencia

Aceptada.

------------------------------------------------------------------------

# ADR-021 --- Permitir reportes parciales cuando falten ciertos datos

**Estado:** ACEPTADA\
**Evidencia:** Confirmada por implementación\
**Ámbito:** Robustez / reportes

## Contexto

No todos los vendedores o periodos disponen necesariamente de todas las
fuentes.

## Decisión

Mostrar mensajes alternativos en lugar de abortar el reporte cuando
faltan determinados datos.

Ejemplos:

``` text
No hay datos gráfica de líneas
Sin datos gráfica pastel
Sin datos gráfica barras
Sin datos de movilidad para este período.
```

## Consecuencia positiva

El reporte puede seguir siendo útil aun cuando una sección no tenga
información.

## Vigencia

Debe preservarse.

------------------------------------------------------------------------

# ADR-022 --- Enviar reportes mediante SMTP

**Estado:** ACEPTADA\
**Evidencia:** Confirmada\
**Ámbito:** Integración / reportes

## Decisión

Utilizar:

``` text
smtplib
smtp.gmail.com:587
STARTTLS
```

para distribuir reportes.

## Credenciales

``` text
CORREO_EMISOR
APP_PASSWORD
```

## Consecuencia

El envío depende de configuración y disponibilidad del servicio SMTP.

## Principio importante

Debe distinguirse:

``` text
PDF generado correctamente
```

de:

``` text
correo enviado correctamente
```

Un fallo de correo no implica necesariamente fallo de generación.

------------------------------------------------------------------------

# ADR-023 --- Mantener seguimiento de uso de ForceManager mediante planeación, notificaciones y strikes

**Estado:** ACEPTADA\
**Evidencia:** Confirmada por implementación e historia funcional\
**Ámbito:** Seguimiento comercial

## Contexto

Una necesidad del proyecto fue verificar que los vendedores utilizaran
ForceManager y registraran actividad.

## Decisión

Incorporar un módulo de planeación/seguimiento apoyado en:

``` text
Calendars
Accounts
NotificacionesVendedores
StrikesVendedores
```

## Consecuencia

CIC no analiza únicamente resultados; también incorpora seguimiento del
registro de actividad comercial.

## Vigencia

Aceptada en CIC v1.

------------------------------------------------------------------------

# ADR-024 --- Priorizar estabilidad y documentación sobre una refactorización profunda de CIC v1

**Estado:** ACEPTADA\
**Evidencia:** Decisión actual confirmada durante formalización
documental\
**Ámbito:** Estrategia de mantenimiento

## Contexto

CIC v1 continúa operativo mientras CIC v2 se desarrolla en paralelo.

El sistema legacy contiene reglas de negocio importantes que todavía
deben reconstruirse y validarse.

## Decisión

Para CIC v1:

``` text
documentar
estabilizar
probar
corregir
```

antes que:

``` text
reescribir
reorganizar completamente
migrar arquitectura
```

## Motivo

Una refactorización extensa podría introducir regresiones sin aportar
suficiente valor si las nuevas capacidades se desarrollarán en CIC v2.

## Consecuencia

La deuda técnica se documenta y se corrige selectivamente.

No toda deuda técnica implica una refactorización inmediata.

## Vigencia

Criterio principal de mantenimiento actual.

------------------------------------------------------------------------

# ADR-025 --- Mantener CIC v1 y CIC v2 como proyectos separados

**Estado:** ACEPTADA\
**Evidencia:** Confirmada\
**Ámbito:** Estrategia / versionado

## Contexto

CIC v2 se desarrolla con una arquitectura distinta y no representa
simplemente una nueva rama de cambios menores sobre CIC v1.

## Decisión

No mezclar el historial técnico de ambos proyectos.

CIC v1 sirve como:

``` text
sistema operativo actual
+
fuente de requisitos
+
referencia de reglas de negocio
```

CIC v2 mantiene su propia:

``` text
arquitectura
historia
roadmap
decisiones
```

## Consecuencia

Los documentos del repositorio CIC v1 pueden mencionar la migración,
pero no deben documentar funcionalidades de v2 como si ya existieran en
v1.

## Vigencia

Aceptada.

------------------------------------------------------------------------

# ADR-026 --- Utilizar CIC v1 como referencia funcional para CIC v2, no como diseño obligatorio

**Estado:** ACEPTADA\
**Evidencia:** Decisión actual\
**Ámbito:** Migración

## Decisión

Durante la migración debe preservarse:

``` text
necesidad de negocio
+
regla de negocio
+
resultado esperado
```

pero no necesariamente:

``` text
estructura de carpetas
clases
framework
SQL embebido
layout
implementación MVC
```

## Ejemplo

CIC v1:

``` text
ClasesIngresosControlador
+
VentasRealesModelo
+
ClasesIngresosVista
```

puede transformarse en CIC v2 en:

``` text
endpoint API
+
servicio
+
repositorio
+
frontend
```

si el resultado funcional permanece validado.

## Vigencia

Aceptada.

------------------------------------------------------------------------

# ADR-027 --- No afirmar PK/FK o constraints sin validar el esquema real

**Estado:** ACEPTADA\
**Evidencia:** Decisión documental actual\
**Ámbito:** Documentación de datos

## Contexto

El repositorio no contiene el DDL completo de `ForceSyncDB_Worker`.

## Decisión

Documentar como:

``` text
relación lógica
```

las relaciones observadas mediante consultas, sin etiquetarlas
automáticamente como:

``` text
FOREIGN KEY
```

## Ejemplo

Puede observarse:

``` text
Accounts.Id = Activities.AccountId_Id
```

pero esto no demuestra por sí solo que SQL Server tenga una FK física.

## Consecuencia

`database.md` distingue hechos del código de información pendiente de
consultar en el catálogo SQL.

## Vigencia

Aceptada hasta completar la inspección del esquema.

------------------------------------------------------------------------

# ADR-028 --- No considerar CTEs como tablas físicas

**Estado:** ACEPTADA\
**Evidencia:** Confirmada durante reconstrucción documental\
**Ámbito:** Documentación SQL

## Contexto

Consultas del proyecto utilizan nombres como:

``` text
ClientesActivos
ClientesNuevos
ClientesBase
TotalClientes
```

mediante:

``` sql
WITH ...
```

## Decisión

Documentarlos como estructuras temporales de consulta y no como
entidades persistentes.

## Consecuencia

Evita construir un mapa de base de datos incorrecto.

------------------------------------------------------------------------

# ADR-029 --- Registrar cambios futuros de forma estructurada

**Estado:** ACEPTADA\
**Evidencia:** Decisión actual\
**Ámbito:** Proceso de desarrollo

## Contexto

La falta de documentación histórica dificultó reconstruir la evolución
inicial de CIC.

## Decisión

Mantener:

``` text
logs/development.md
logs/roadmap.md
logs/dev_log.csv
docs/decisions.md
```

con responsabilidades diferentes.

## Regla

``` text
development.md
= cómo evolucionó CIC

roadmap.md
= hacia dónde va CIC

dev_log.csv
= qué cambió

decisions.md
= por qué se tomó una decisión
```

## Consecuencia

Los cambios futuros deberían requerir mucha menos reconstrucción
retrospectiva.

------------------------------------------------------------------------

# ADR-030 --- No inventar fechas o motivos del periodo pre-Git

**Estado:** ACEPTADA\
**Evidencia:** Decisión documental actual\
**Ámbito:** Trazabilidad

## Contexto

El historial Git disponible comienza el:

``` text
02/09/2026
```

cuando CIC ya tenía una cantidad considerable de funcionalidad.

## Decisión

Separar:

``` text
historia pre-Git reconstruida
```

de:

``` text
historial Git verificable
```

y no asignar fechas exactas o motivos que no puedan demostrarse.

## Consecuencia

La documentación puede contener vacíos explícitos en lugar de crear una
falsa precisión histórica.

------------------------------------------------------------------------

# 4. Decisiones propuestas, no aprobadas

Las siguientes ideas aparecen como recomendaciones en la documentación,
pero **no deben interpretarse como decisiones ya tomadas**.

------------------------------------------------------------------------

## PROP-001 --- Dividir `ExcelesModelo`

**Estado:** PROPUESTA

Posible separación:

``` text
ImportacionVentasService
TipoCambioService
ReportePdfService
EmailService
GraficasReporteService
```

### Motivo

`exceles_modelo.py` concentra múltiples responsabilidades.

### Estado actual

No implementar automáticamente en CIC v1.

Evaluar únicamente si existe una necesidad concreta de mantenimiento.

------------------------------------------------------------------------

## PROP-002 --- Crear repositorios de acceso a datos

**Estado:** PROPUESTA

Ejemplo:

``` text
VentasRepository
MetasRepository
MovilidadRepository
UsuariosRepository
```

### Objetivo

Separar SQL de reglas de negocio.

### Destino más probable

CIC v2.

------------------------------------------------------------------------

## PROP-003 --- Utilizar identificador canónico de vendedor

**Estado:** PROPUESTA PARA CIC v2

En lugar de depender principalmente de:

``` text
NombreVendedor
RepresentanteDeVentas
SalesRepName
```

utilizar:

``` text
vendedor_id
```

estable.

### Beneficio

Reducir errores de integración entre fuentes.

------------------------------------------------------------------------

## PROP-004 --- Separar datos del reporte y render PDF

**Estado:** PROPUESTA

Conceptualmente:

``` text
ReportDataService
      │
      ▼
ReporteData
      │
      ▼
PdfRenderer
```

### Beneficio

Permitir validar indicadores sin depender de la presentación.

------------------------------------------------------------------------

## PROP-005 --- Crear pruebas automatizadas para reglas críticas

**Estado:** PROPUESTA PRIORITARIA

Priorizar:

``` text
clasificación de cuadrantes
categorización de ventas
conversión monetaria
clientes activos/nuevos
metas y presupuesto
indicadores PDF
```

### Motivo

Son reglas que CIC v2 deberá reproducir o reemplazar conscientemente.

------------------------------------------------------------------------

# 5. Plantilla para nuevas decisiones

A partir de esta documentación, una nueva decisión puede registrarse
así:

``` text
# ADR-XXX — Título

Estado:
Fecha:
Responsable:
Evidencia:

## Contexto

¿Qué problema o necesidad existe?

## Opciones consideradas

1. Opción A
2. Opción B
3. Opción C

## Decisión

¿Qué se decidió?

## Motivo

¿Por qué?

## Consecuencias positivas

¿Qué mejora?

## Consecuencias negativas / riesgos

¿Qué costo introduce?

## Validación

¿Cómo sabemos que funciona?

## Relación con CIC v2

¿Aplica solamente a v1, solamente a v2 o a ambos?
```

No es obligatorio llenar alternativas históricas cuando no se conocen.

Es preferible escribir:

``` text
Alternativas históricas: no documentadas
```

que reconstruirlas artificialmente.

------------------------------------------------------------------------

# 6. Cuándo crear un ADR

No todo cambio requiere una entrada en `decisions.md`.

## Sí registrar

Cambios como:

-   cambio de arquitectura;
-   nueva fuente de datos;
-   cambio de autenticación;
-   cambio de estrategia de reportes;
-   cambio de reglas de integración;
-   decisión de migración;
-   reemplazo de una tecnología;
-   cambio de modelo de datos;
-   modificación importante de una regla comercial;
-   eliminación de un módulo;
-   decisión con consecuencias difíciles de revertir.

## No es necesario registrar

Cambios como:

-   corrección de texto;
-   ajuste visual menor;
-   limpieza de comentarios;
-   bug trivial;
-   renombrado interno sin impacto;
-   actualización menor que no cambia comportamiento.

Estos cambios sí pueden aparecer en:

``` text
dev_log.csv
```

------------------------------------------------------------------------

# 7. Relación entre ADR y Git

Cuando sea posible, una nueva decisión debe registrar:

``` text
fecha
commit
rama
issue/ticket
```

si existen.

Ejemplo:

``` text
ADR-031
Commit: abc1234
Rama: feature/...
```

Esto permitirá conectar:

``` text
razón
   │
   ▼
decisión
   │
   ▼
implementación
   │
   ▼
commit
```

------------------------------------------------------------------------

# 8. Decisiones que requieren validación futura

Aún existen áreas cuyo razonamiento histórico no está suficientemente
documentado.

Entre ellas:

``` text
por qué se eligieron exactamente ciertos umbrales de cuadrantes;
origen formal de algunas categorías comerciales;
motivo original de ciertas reglas para vendedores de piso;
por qué algunas relaciones utilizan nombres en lugar de IDs;
criterio original de notificaciones y strikes;
definición histórica exacta de algunos indicadores de servicio;
política original de destinatarios de correo;
origen de algunas rutas y convenciones de archivos.
```

Estas cuestiones no deben rellenarse por inferencia.

Si se recupera información mediante:

-   documentación antigua;
-   correos;
-   responsables del proceso;
-   commits;
-   scripts SQL;
-   archivos históricos;

se podrá crear o actualizar el ADR correspondiente.

------------------------------------------------------------------------

# 9. Principios derivados de las decisiones actuales

La documentación reconstruida permite establecer algunos principios de
mantenimiento.

## 9.1 Preservar significado antes que implementación

Una regla comercial vale más que la clase Python que actualmente la
implementa.

## 9.2 No confundir correlación con causalidad

Los cuadrantes ayudan a observar comportamientos; no demuestran por sí
solos por qué ocurre un resultado.

## 9.3 Diferenciar fuentes

ForceManager, ventas reales, movilidad y datos propios de CIC no deben
mezclarse sin conocer su origen.

## 9.4 Mantener trazabilidad

Los cambios futuros deben poder responder:

``` text
qué cambió
por qué cambió
quién/qué módulo se afecta
cómo se validó
```

## 9.5 CIC v1 debe permanecer estable

Las mejoras profundas deben justificarse por una necesidad concreta.

## 9.6 CIC v2 debe aprender de v1 sin copiar sus limitaciones

La migración debe preservar reglas válidas y rediseñar conscientemente
los acoplamientos técnicos.

------------------------------------------------------------------------

# 10. Documentos relacionados

``` text
README.md
```

Entrada general al proyecto.

``` text
docs/architecture.md
```

Arquitectura actual.

``` text
docs/database.md
```

Mapa de datos y relaciones observadas.

``` text
docs/modules.md
```

Catálogo funcional.

``` text
docs/reports.md
```

Pipeline de reportes PDF.

``` text
logs/development.md
```

Historia reconstruida.

``` text
logs/roadmap.md
```

Dirección futura.

``` text
logs/dev_log.csv
```

Registro estructurado de cambios.

------------------------------------------------------------------------

# 11. Conclusión

La principal función de este documento es evitar que CIC vuelva a perder
el contexto detrás de sus decisiones.

En el periodo histórico previo a la documentación formal, muchas
decisiones quedaron únicamente representadas por el código.

A partir de esta etapa, la intención es que una modificación importante
pueda reconstruirse mediante:

``` text
development.md
        +
dev_log.csv
        +
decisions.md
        +
Git
```

De esta manera será posible conocer no solamente:

> **qué hace CIC**

sino también:

> **por qué terminó funcionando de esa manera.**

Esto será especialmente importante mientras CIC v1 permanezca operativo
y CIC v2 avance en paralelo.
