# CIC — Arquitectura del Sistema

**Proyecto:** CIC — Centro de Inteligencia Comercial  
**Versión documentada:** CIC v1  
**Tipo de documento:** Arquitectura técnica  
**Estado:** Arquitectura existente documentada retrospectivamente  
**Última actualización:** 05/10/2026  

---

## 1. Propósito

Este documento describe la arquitectura técnica actualmente observable en CIC v1.

Su objetivo es permitir que un desarrollador pueda comprender:

- cómo inicia la aplicación;
- cómo se organiza el código;
- cómo se realiza la navegación;
- cómo interactúan controladores, vistas y modelos;
- cómo se accede a SQL Server;
- qué integraciones externas existen;
- dónde se mantiene el estado de la sesión;
- qué componentes presentan mayor acoplamiento;
- qué aspectos deberían considerarse al evolucionar CIC v1 o trasladar reglas de negocio hacia CIC v2.

Este documento distingue entre:

1. **arquitectura observada**, respaldada por el código actual;
2. **consideraciones de evolución**, que representan recomendaciones y no componentes existentes.

---

# 2. Resumen arquitectónico

CIC v1 es una aplicación monolítica desarrollada en Python con Streamlit como capa de interfaz.

La aplicación sigue una separación inspirada en el patrón **Modelo–Vista–Controlador (MVC)**:

```text
┌───────────────────────────────┐
│            Usuario            │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│          Streamlit UI         │
│                               │
│ vistas + componentes visuales │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│         Controladores         │
│                               │
│ navegación + coordinación     │
└───────────┬─────────┬─────────┘
            │         │
            ▼         ▼
┌──────────────────┐  ┌──────────────────┐
│      Modelos     │  │ st.session_state │
│                  │  │                  │
│ consultas        │  │ sesión           │
│ reglas/cálculos  │  │ navegación       │
│ procesamiento    │  │ permisos         │
└─────────┬────────┘  └──────────────────┘
          │
          ▼
┌───────────────────────────────┐
│        SQL Server             │
│      ForceSyncDB_Worker       │
└───────────────────────────────┘
```

Algunos modelos también interactúan directamente con servicios o recursos externos:

```text
                         ┌───────────────────┐
                         │ API de Banxico    │
                         └─────────▲─────────┘
                                   │
                                   │ HTTP
┌───────────────┐        ┌─────────┴─────────┐
│ SQL Server    │◄──────►│     Modelos       │
└───────────────┘        │                   │
                         │ procesamiento     │
                         │ Excel / reportes  │
                         └──────┬──────┬─────┘
                                │      │
                           PDF  │      │ SMTP
                                ▼      ▼
                         ┌─────────┐ ┌──────────┐
                         │ReportLab│ │  Gmail   │
                         └─────────┘ └──────────┘
```

---

# 3. Estilo arquitectónico

## 3.1 Monolito modular

CIC v1 se ejecuta como una sola aplicación Streamlit.

No se identificó en esta versión una separación mediante servicios independientes o una API intermedia entre la interfaz y la base de datos.

Por lo tanto, la clasificación más adecuada para el estado actual es:

> **Aplicación monolítica modular con separación MVC parcial.**

Es monolítica porque interfaz, navegación, lógica de aplicación, acceso a datos, procesamiento y generación de reportes se ejecutan dentro del mismo proceso Python.

Es modular porque el código se encuentra distribuido por responsabilidades y dominios funcionales.

---

## 3.2 MVC parcial

La estructura principal utiliza:

```text
controlador/
modelo/
vista/
```

y varios controladores instancian explícitamente un modelo y una vista.

Ejemplo conceptual:

```python
self.modelo = PerfilesModelo()
self.vista = PerfilesVista()
```

El flujo esperado es:

```text
Vista
  │
  │ entrada del usuario
  ▼
Controlador
  │
  │ solicita datos / ejecuta lógica
  ▼
Modelo
  │
  ▼
Base de datos
```

y posteriormente:

```text
Modelo
  │
  │ datos procesados
  ▼
Controlador
  │
  ▼
Vista
  │
  ▼
Usuario
```

Sin embargo, la separación no es estricta en todo el proyecto. Existen componentes que realizan más de una responsabilidad, por lo que no debe describirse CIC como una implementación MVC pura.

---

# 4. Estructura física del proyecto

La estructura principal observada es:

```text
CIC/
│
├── main.py
├── requirements.txt
├── README.md
│
├── controlador/
│   ├── base_controlador.py
│   ├── navegacion_controlador_login.py
│   │
│   ├── admin/
│   ├── cuadrantesGartner/
│   ├── perfilesGraficas/
│   ├── rendimiento/
│   ├── reportes/
│   └── ventasReales/
│
├── modelo/
│   ├── db_connection.py
│   ├── exceles_modelo.py
│   ├── gartner_modelo.py
│   ├── ventas_reales_modelo.py
│   ├── perfiles_modelo.py
│   ├── metas_modelo.py
│   ├── presupuesto_modelo.py
│   ├── rendimiento_modelo.py
│   ├── kilometraje_modelo.py
│   ├── planeacion_modelo.py
│   ├── resumen_movilidad_modelo.py
│   ├── usuarios_modelo.py
│   ├── vendedores_modelo.py
│   ├── cobertura_cartera_modelo.py
│   │
│   ├── admin/
│   ├── cifrado/
│   └── reporte_pdf/
│
├── vista/
│   ├── base_vista.py
│   ├── exceles_vista.py
│   ├── perfiles_vista.py
│   ├── metas_vista.py
│   ├── presupuesto_vista.py
│   ├── rendimiento_vista.py
│   ├── kilometraje_vista.py
│   ├── planeacion_vista.py
│   ├── resumen_movilidad_vista.py
│   ├── vendedores_vista.py
│   │
│   ├── admin/
│   ├── componentes/
│   ├── login/
│   ├── seleccion_usuarios/
│   ├── ventasRealesVista/
│   └── images/
│
├── logs/
│   ├── development.md
│   ├── roadmap.md
│   └── dev_log.csv
│
└── docs/
    └── architecture.md
```

Las carpetas `logs/` y `docs/` corresponden al esquema documental que se está formalizando y pueden no estar presentes todavía en todas las copias históricas del repositorio.

---

# 5. Punto de entrada

El punto de entrada de CIC es:

```text
main.py
```

Su responsabilidad principal es:

1. configurar la página Streamlit;
2. crear el controlador principal de navegación;
3. iniciar el flujo de la aplicación;
4. capturar errores generales durante el arranque.

El flujo observado es:

```text
main.py
   │
   ▼
NavegacionControladorLogin()
   │
   ▼
ejecutar_barra_principal()
```

`main.py` no contiene la lógica funcional principal del sistema.

La mayor parte de la coordinación se delega a:

```text
controlador/navegacion_controlador_login.py
```

---

# 6. Controlador principal de navegación

`NavegacionControladorLogin` funciona actualmente como el principal **orquestador de interfaz** de CIC.

Entre sus responsabilidades observadas se encuentran:

- instanciar controladores funcionales;
- instanciar algunos modelos y componentes visuales;
- mostrar la pantalla de autenticación;
- controlar el menú lateral;
- consultar permisos del usuario;
- activar o desactivar módulos;
- determinar qué pantalla debe ejecutarse;
- mantener estados de navegación mediante `st.session_state`.

Ejemplos de áreas coordinadas desde este controlador:

```text
Comportamiento de vendedores
Ventas reales
Perfiles
Importación / reportes
Metas
Presupuesto
Administración
Configuración
Rendimiento
Kilometraje
Planeación
Resumen de movilidad
```

Además contiene diccionarios de controladores para grupos funcionales.

### Comportamientos / cuadrantes

```text
Ventas vs GPS
Ventas vs Movilidad
Visitas vs Ventas
Visitas Generales vs Movilidad
Visitas vs Movilidad
Tareas vs Actividades
Actividades vs Movilidad
Tiempos vs Visitas
Tiempos Promedio vs Visitas
```

### Perfiles / estimaciones

```text
Ventas Mensuales
Status Clientes
Clientes Nuevos y Activos
```

### Ventas

```text
Ventas por Proyecto
Ventas por Cliente
Ventas por Clases
Cantidad Clases Vendida
```

---

# 7. Gestión del estado

Streamlit vuelve a ejecutar el script cuando se producen interacciones de interfaz.

CIC utiliza:

```python
st.session_state
```

para conservar información entre esas ejecuciones.

Se identificaron estados relacionados con:

```text
usuario_autenticado
permisos_usuario

mostrar_comportamientos
mostrar_perfiles
mostrar_exceles
mostrar_metas
mostrar_presupuesto
mostrar_admin
mostrar_config
mostrar_rendimiento
mostrar_kilometraje
mostrar_planeacion
mostrar_resumen_movilidad
mostrar_ventas_reales

pagina_seleccionada
perfil_seleccionado
venta_seleccionada
```

Por lo tanto, `st.session_state` forma parte importante de la arquitectura de CIC v1.

Conceptualmente:

```text
Interacción usuario
       │
       ▼
Streamlit rerun
       │
       ▼
st.session_state
       │
       ├── autenticación
       ├── permisos
       ├── pantalla activa
       └── filtros/selecciones
       │
       ▼
Controlador correspondiente
```

---

# 8. Capa de controladores

Los controladores coordinan la interacción entre interfaz y datos.

Las áreas observadas son:

## 8.1 Administración

```text
controlador/admin/
```

Incluye lógica relacionada con administración y configuración.

---

## 8.2 Cuadrantes Gartner

```text
controlador/cuadrantesGartner/
```

Contiene controladores para análisis comparativos entre indicadores comerciales.

Ejemplos:

```text
ventas_gps_controlador.py
vendedores_controlador.py
visitas_ventas_controlador.py
visitas_movilidad_controlador.py
visitas_general_movilidad_controlador.py
tareas_actividades_controlador.py
actividades_movilidad_controlador.py
tiempos_visitas_controlador.py
tiempos_visitas_promedio_controlador.py
```

Estos módulos representan una parte central del propósito histórico de CIC.

---

## 8.3 Perfiles y gráficas

```text
controlador/perfilesGraficas/
```

Coordina análisis como:

- ventas mensuales;
- estado de clientes;
- clientes nuevos y activos.

---

## 8.4 Ventas reales

```text
controlador/ventasReales/
```

Coordina visualizaciones como:

- categoría/proyecto vs ingresos;
- cliente vs ingresos;
- clases vs ingresos;
- cantidad de clases vendidas.

---

## 8.5 Reportes y captura

```text
controlador/reportes/
```

Incluye coordinación para:

```text
Exceles
Metas
Presupuesto
Kilometraje
Planeación
Resumen de movilidad
```

---

## 8.6 Rendimiento

```text
controlador/rendimiento/
```

Coordina las funcionalidades relacionadas con rendimiento comercial.

---

# 9. Capa de vistas

La capa `vista/` contiene la mayor parte de los elementos visuales construidos con Streamlit.

Entre sus responsabilidades se encuentran:

- títulos;
- formularios;
- selectores;
- filtros;
- tablas;
- mensajes;
- gráficas;
- componentes de navegación;
- login;
- elementos visuales reutilizables.

Existe una clase:

```text
BaseVista
```

que proporciona operaciones comunes como:

```text
mostrar_titulo()
mostrar_error()
mostrar_exito()
mostrar_info()
mostrar_warning()
```

También existen componentes reutilizables en:

```text
vista/componentes/
```

como botones, logotipos, información de filtros y elementos del sidebar.

---

# 10. Capa de modelos

La carpeta `modelo/` concentra el acceso a datos y una parte importante de la lógica de procesamiento.

Los modelos identificados incluyen:

```text
gartner_modelo.py
ventas_reales_modelo.py
perfiles_modelo.py
exceles_modelo.py
metas_modelo.py
presupuesto_modelo.py
rendimiento_modelo.py
kilometraje_modelo.py
planeacion_modelo.py
resumen_movilidad_modelo.py
usuarios_modelo.py
vendedores_modelo.py
vendedores_registrados.py
cobertura_cartera_modelo.py
```

En términos generales los modelos realizan operaciones como:

```text
SQL Server
    │
    ▼
consultas SQL
    │
    ▼
Pandas DataFrame
    │
    ▼
transformación / cálculo
    │
    ▼
Controlador
```

No obstante, algunos modelos también contienen responsabilidades adicionales, especialmente `exceles_modelo.py`.

---

# 11. Acceso a SQL Server

La conexión principal está centralizada en:

```text
modelo/db_connection.py
```

mediante la clase:

```text
DatabaseConnection
```

El módulo carga variables del archivo `.env`:

```text
SERVER
DATABASE
USERNAME
PASSWORD
DRIVER
```

En la implementación activa observada, la cadena utiliza:

```text
Trusted_Connection=yes
```

por lo que la conexión efectiva utiliza autenticación integrada de Windows.

Esto es importante porque, aunque `USERNAME` y `PASSWORD` se cargan en la configuración, no son utilizados por la cadena activa.

Existe además código comentado para una conexión mediante:

```text
UID
PWD
```

pero no corresponde a la implementación activa.

---

# 12. Base de datos y dominio de información

La base identificada para CIC v1 es:

```text
ForceSyncDB_Worker
```

Las consultas del código hacen referencia, entre otras, a entidades como:

```text
Accounts
Activities
Calendars
Opportunities
Users
UsuariosCIC

dev_Detalle_Corregida

Metas
PresupuestoSegmentos

MovilidadRegistro
ResumenMovilidad

NotificacionesVendedores
StrikesVendedores

ClientesActivos
ClientesBase
ClientesNuevos
```

También existen consultas sobre objetos derivados o vistas, por ejemplo:

```text
vw_CategoriaIngresos
```

La documentación detallada de estas entidades se trasladará a:

```text
docs/database.md
```

---

# 13. Origen lógico de los datos

A nivel arquitectónico conviene distinguir dos grupos.

## 13.1 Información procedente del ecosistema ForceSync / ForceManager

Incluye información comercial y de actividad que CIC consulta para realizar análisis.

Conceptualmente:

```text
ForceManager / ForceSync
          │
          ▼
ForceSyncDB_Worker
          │
          ▼
         CIC
```

## 13.2 Información administrada por CIC

CIC también trabaja con información propia o complementaria, como metas, presupuestos, movilidad, usuarios de la aplicación y datos derivados necesarios para análisis y reportes.

Por tanto, CIC no funciona únicamente como visor de ForceManager.

También agrega información y reglas de negocio propias.

---

# 14. Flujo de autenticación y permisos

La navegación principal verifica:

```python
st.session_state.get("usuario_autenticado", False)
```

Si el usuario no está autenticado se muestra la vista de login.

Una vez autenticado, la aplicación utiliza información almacenada en sesión para determinar qué opciones deben mostrarse.

Conceptualmente:

```text
Usuario
   │
   ▼
LoginVista
   │
   ▼
UsuariosModelo / datos de usuario
   │
   ▼
Autenticación
   │
   ▼
st.session_state
   │
   ├── usuario_autenticado
   └── permisos_usuario
          │
          ▼
NavegacionControladorLogin
          │
          ▼
Módulos permitidos
```

Los permisos participan directamente en la construcción de la navegación.

---

# 15. Flujo de una consulta típica

Un flujo representativo puede expresarse así:

```text
1. Usuario selecciona un módulo
            │
            ▼
2. Streamlit genera evento / rerun
            │
            ▼
3. NavegacionControladorLogin
   identifica pantalla activa
            │
            ▼
4. Ejecuta controlador funcional
            │
            ▼
5. Vista obtiene filtros del usuario
            │
            ▼
6. Controlador solicita información
   al modelo
            │
            ▼
7. Modelo consulta SQL Server
            │
            ▼
8. Datos se cargan/procesan
   normalmente con Pandas
            │
            ▼
9. Controlador entrega resultados
   a la vista
            │
            ▼
10. Streamlit muestra tablas,
    indicadores o gráficas
```

---

# 16. Importación de ventas

La importación de información de ventas está concentrada principalmente en:

```text
modelo/exceles_modelo.py
controlador/reportes/exceles_controlador.py
vista/exceles_vista.py
```

El flujo conceptual es:

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
     ├── mapeo de columnas
     ├── validaciones
     ├── validación de periodos
     ├── procesamiento
     ├── tipo de cambio
     └── inserción
            │
            ▼
      SQL Server
```

El modelo contiene operaciones para:

- mapear columnas;
- detectar meses/años existentes;
- validar fechas duplicadas;
- insertar detalles;
- consultar vendedores;
- obtener información por vendedor y periodo.

---

# 17. Integración con Banxico

`exceles_modelo.py` consume la API de Banxico mediante `requests`.

Las variables utilizadas son:

```text
BANXICO
SERIE_BANXICO
```

El flujo es:

```text
Fecha de operación
       │
       ▼
ExcelesModelo
       │
       ▼
API SIE Banxico
       │
       ▼
Tipo de cambio
       │
       ▼
Procesamiento de ventas
```

La serie y el token no deben almacenarse directamente en el código.

Deben permanecer en `.env`.

---

# 18. Generación de reportes PDF

La generación de reportes se encuentra principalmente dentro de:

```text
modelo/exceles_modelo.py
```

y utiliza ReportLab.

El mismo módulo contiene funciones relacionadas con:

- consulta de datos del vendedor;
- metas;
- gráficas;
- categorías;
- clientes;
- actividades;
- construcción del PDF;
- elementos gráficos del reporte;
- envío posterior por correo.

Flujo conceptual:

```text
SQL Server
    │
    ▼
ExcelesModelo
    │
    ├── ventas
    ├── metas
    ├── clientes
    ├── actividades
    └── movilidad
    │
    ▼
Pandas / Matplotlib
    │
    ▼
ReportLab
    │
    ▼
Reporte PDF
```

Los recursos visuales se configuran mediante variables como:

```text
LOGO_PDF
ENCABEZADO_GRIS
ENCABEZADO_ROJO
PIE_ROJO
```

y los datos de control documental mediante:

```text
CODIGO_NORMA
REVISION_NORMA
FECHA_APLICACION_NORMA
```

---

# 19. Envío de correo

El proyecto utiliza `smtplib` para enviar reportes.

Variables observadas:

```text
CORREO_EMISOR
APP_PASSWORD
CORREO_REPORTES_1
CORREO_REPORTES_2
```

El servidor utilizado en el código actual es:

```text
smtp.gmail.com:587
```

Flujo:

```text
PDF generado
     │
     ▼
ExcelesModelo
     │
     ▼
SMTP
     │
     ▼
Destinatarios configurados
```

Esta integración se encuentra actualmente acoplada al modelo encargado de Excel/reportes.

---

# 20. Dependencias externas relevantes

La arquitectura depende de varios componentes externos.

| Componente | Uso |
|---|---|
| SQL Server | Persistencia y fuente principal de información |
| ODBC / pyodbc | Conexión Python ↔ SQL Server |
| ForceSync / ForceManager | Fuente de parte de la información comercial |
| Banxico SIE API | Consulta de tipo de cambio |
| SMTP Gmail | Envío de reportes |
| Sistema de archivos | Excel, PDF e imágenes de reportes |
| Streamlit | Interfaz y ciclo de ejecución |

Una falla en alguno de estos componentes puede afectar únicamente un módulo o impedir parte del flujo de la aplicación, dependiendo de la dependencia.

---

# 21. Configuración

La configuración se realiza principalmente mediante:

```text
.env
```

Variables observadas:

```text
SERVER
DATABASE
USERNAME
PASSWORD
DRIVER

BANXICO
SERIE_BANXICO

CORREO_REPORTES_1
CORREO_REPORTES_2
CORREO_EMISOR
APP_PASSWORD

LOGO_PDF
CARPETA_DESTINO

ENCABEZADO_GRIS
ENCABEZADO_ROJO
PIE_ROJO

CODIGO_NORMA
REVISION_NORMA
FECHA_APLICACION_NORMA
```

El README histórico también documenta `CORREO_REPORTES_3` y `CARPETA_REPORTES`; su uso efectivo debe verificarse antes de considerarlas dependencias obligatorias del código actual.

---

# 22. Características arquitectónicas positivas

La arquitectura existente presenta varias decisiones útiles.

## Separación por carpetas

La existencia de:

```text
controlador/
modelo/
vista/
```

facilita localizar responsabilidades.

## Organización por dominio

Los controladores se subdividen en áreas como:

```text
cuadrantesGartner
ventasReales
reportes
perfilesGraficas
admin
rendimiento
```

lo que refleja funcionalidades del negocio.

## Conexión centralizada

`DatabaseConnection` evita definir una cadena de conexión distinta en cada módulo.

## Configuración externa

Credenciales y rutas sensibles se obtienen mediante variables de entorno.

## Componentes visuales reutilizables

La carpeta:

```text
vista/componentes/
```

reduce parte de la duplicación de elementos de interfaz.

---

# 23. Acoplamientos y deuda arquitectónica observada

Esta sección describe el estado actual y no implica que deba refactorizarse inmediatamente.

## 23.1 Controlador de navegación grande

`navegacion_controlador_login.py` concentra:

- navegación;
- permisos;
- estado;
- instanciación de numerosos controladores;
- parte de la lógica de presentación;
- acceso directo a algunos modelos.

Esto lo convierte en un componente central con muchas dependencias.

### Riesgo

Un cambio en navegación puede afectar varias áreas de la aplicación.

---

## 23.2 `exceles_modelo.py` concentra múltiples responsabilidades

Este módulo contiene funciones relacionadas con:

```text
Excel
SQL
tipo de cambio Banxico
procesamiento de ventas
gráficas
PDF
correo
```

Arquitectónicamente actúa como varios servicios dentro de una misma clase/módulo.

### Riesgo

Las modificaciones en reportes, importación o correo pueden afectar un archivo compartido de gran tamaño.

---

## 23.3 Modelo con responsabilidades de presentación

La generación de gráficas y PDF se encuentra dentro de la capa denominada `modelo`.

Esto funciona actualmente, pero amplía la responsabilidad de dicha capa más allá del acceso a datos y reglas de negocio.

---

## 23.4 Estado de navegación distribuido

La aplicación utiliza múltiples valores booleanos de `st.session_state`:

```text
mostrar_comportamientos
mostrar_perfiles
mostrar_exceles
...
```

### Riesgo

A medida que aumenten los módulos puede crecer la complejidad necesaria para garantizar que solo una sección esté activa.

---

## 23.5 SQL embebido en modelos

Las consultas SQL están distribuidas en diferentes archivos de `modelo/`.

Esto hace que las reglas de acceso a datos dependan directamente de la implementación de SQL Server.

En CIC v1 esto es parte de la arquitectura actual.

Para CIC v2 debe evaluarse una separación más clara entre acceso a datos y lógica de negocio.

---

# 24. Arquitectura actual vs. arquitectura futura

## CIC v1 — situación actual

```text
Streamlit
   │
   ▼
Controladores
   │
   ├────────► Vistas
   │
   ▼
Modelos
   │
   ├────────► SQL Server
   ├────────► Banxico
   ├────────► Archivos
   ├────────► PDF
   └────────► SMTP
```

Esta arquitectura debe priorizar estabilidad sobre refactorizaciones extensas.

---

## CIC v2 — dirección conceptual

CIC v2 se está desarrollando como proyecto independiente y no debe documentarse aquí como arquitectura ya implementada.

Sin embargo, CIC v1 permite identificar una separación deseable:

```text
Frontend
   │
   ▼
API
   │
   ▼
Casos de uso / servicios
   │
   ├────────► Reglas de negocio
   │
   ├────────► Reportes
   │
   └────────► Integraciones
   │
   ▼
Capa de acceso a datos
   │
   ▼
SQL Server
```

Esta representación es únicamente una **dirección arquitectónica de referencia**.

Las decisiones reales de CIC v2 deben documentarse en el repositorio de CIC v2.

---

# 25. Recomendaciones de evolución para CIC v1

Las siguientes acciones pueden mejorar mantenibilidad sin transformar completamente la arquitectura.

## Alta prioridad

- documentar consultas y tablas críticas;
- documentar reglas de negocio;
- crear pruebas para cálculos importantes;
- mantener `.env` fuera de Git;
- crear `.env.example`;
- registrar cambios en `dev_log.csv`.

## Prioridad media

- extraer progresivamente responsabilidades de `exceles_modelo.py`;
- reducir acceso directo a modelos desde el controlador de navegación;
- centralizar constantes y configuración;
- revisar manejo de excepciones;
- documentar contratos de entrada/salida de los módulos.

## Baja prioridad mientras CIC v1 siga estable

- refactorización completa del patrón MVC;
- reemplazo total del sistema de navegación;
- migración tecnológica dentro de CIC v1.

Estas transformaciones profundas tienen mayor sentido dentro de CIC v2 que en una versión legacy que debe permanecer operativa.

---

# 26. Posible separación futura de servicios internos

Si se requiere mantener CIC v1 durante un periodo prolongado, `exceles_modelo.py` podría dividirse conceptualmente en:

```text
servicios/
├── importacion_ventas_service.py
├── tipo_cambio_service.py
├── reporte_pdf_service.py
├── correo_service.py
└── graficas_reporte_service.py
```

y la persistencia podría organizarse mediante repositorios:

```text
repositorios/
├── ventas_repository.py
├── metas_repository.py
├── movilidad_repository.py
└── usuarios_repository.py
```

**Estos directorios no forman parte de la arquitectura actual.**

Se documentan únicamente como una posible estrategia de refactorización incremental.

---

# 27. Diagrama de componentes consolidado

```text
┌─────────────────────────────────────────────────────────────┐
│                        USUARIO                              │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                       STREAMLIT                             │
│                                                             │
│  Login │ Sidebar │ Filtros │ Tablas │ Gráficas │ Formularios│
└───────────────┬───────────────────────────────┬─────────────┘
                │                               │
                │                    st.session_state
                │                    autenticación / permisos
                ▼
┌─────────────────────────────────────────────────────────────┐
│              NAVEGACION CONTROLADOR LOGIN                  │
│                                                             │
│      selección de módulo + permisos + coordinación          │
└────────────────────────────┬────────────────────────────────┘
                             │
              ┌──────────────┼───────────────────┐
              │              │                   │
              ▼              ▼                   ▼
       Cuadrantes        Ventas reales        Reportes
       Perfiles          Rendimiento          Admin
       Planeación        Movilidad            Metas
              │              │                   │
              └──────────────┼───────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                         MODELOS                             │
│                                                             │
│ SQL │ Pandas │ cálculos │ Excel │ gráficas │ PDF │ correo  │
└─────┬─────────────────┬────────────────┬──────────────┬─────┘
      │                 │                │              │
      ▼                 ▼                ▼              ▼
┌───────────┐     ┌────────────┐   ┌──────────┐   ┌─────────┐
│SQL Server │     │Banxico API │   │Archivos  │   │  SMTP   │
│           │     │            │   │Excel/PDF │   │ Gmail   │
└───────────┘     └────────────┘   └──────────┘   └─────────┘
```

---

# 28. Reglas para modificar la arquitectura

Cualquier cambio que altere alguno de los siguientes puntos debe actualizar este documento:

- estructura de carpetas;
- punto de entrada;
- navegación;
- autenticación;
- permisos;
- estrategia de estado;
- acceso a base de datos;
- integraciones externas;
- generación de reportes;
- responsabilidades entre modelo, vista y controlador.

El cambio también deberá registrarse en:

```text
logs/dev_log.csv
```

Si el cambio responde a una decisión técnica importante, deberá registrarse además en:

```text
docs/decisions.md
```

---

# 29. Documentos relacionados

```text
README.md
```

Puerta de entrada al proyecto, instalación y configuración.

```text
logs/development.md
```

Historia y evolución del proyecto.

```text
logs/roadmap.md
```

Prioridades y dirección futura.

```text
logs/dev_log.csv
```

Registro estructurado de modificaciones.

```text
docs/database.md
```

Siguiente documento recomendado para describir tablas, vistas, origen de datos y relaciones.

```text
docs/modules.md
```

Deberá documentar cada módulo funcional y sus dependencias.

```text
docs/reports.md
```

Deberá documentar específicamente el flujo y estructura de reportes.

```text
docs/decisions.md
```

Deberá registrar decisiones arquitectónicas relevantes.

---

# 30. Conclusión

CIC v1 evolucionó hacia un monolito modular de inteligencia comercial construido sobre Streamlit y SQL Server.

Su arquitectura presenta una separación MVC reconocible, aunque no estricta. Los controladores coordinan la interacción, las vistas concentran gran parte de la presentación y los modelos contienen acceso a datos junto con una cantidad importante de procesamiento y reglas de negocio.

El principal objetivo arquitectónico para CIC v1 debe ser:

> **comprender, documentar y estabilizar antes de refactorizar.**

La arquitectura actual representa además una fuente importante para identificar las reglas de negocio que deberán conservarse, validarse o rediseñarse durante la construcción de CIC v2.
