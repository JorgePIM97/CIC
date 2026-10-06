# CIC — Inteligencia Comercial

Aplicación de inteligencia comercial orientada al análisis del desempeño de la fuerza de ventas mediante la relación entre **ventas, movilidad, actividad comercial, visitas, metas y otros indicadores de seguimiento**.

CIC permite complementar el análisis tradicional de ventas con información sobre el comportamiento comercial de los vendedores, facilitando la identificación de patrones y diferencias entre resultados y actividad.

> **Estado del proyecto:** CIC v1 se encuentra operativo y en mantenimiento. Paralelamente se desarrolla CIC v2, tomando esta versión como referencia funcional y fuente de reglas de negocio.

---

## 1. Objetivo

CIC nació ante la necesidad de contar con mayor visibilidad sobre el desempeño comercial.

Analizar únicamente el monto vendido no permite explicar por completo el comportamiento de un vendedor. Por ello, CIC relaciona diferentes variables comerciales para observar escenarios como:

- ventas altas o bajas;
- movilidad alta o baja;
- nivel de actividad comercial;
- visitas y tiempo destinado a clientes;
- cumplimiento de metas o presupuestos;
- variaciones de desempeño entre periodos;
- uso y registro de actividad en ForceManager.

El propósito del sistema es proporcionar información para el análisis y seguimiento comercial; los indicadores deben interpretarse dentro del contexto de cada vendedor y periodo.

---

## 2. Tecnologías principales

CIC v1 está desarrollado principalmente con:

- **Python**
- **Streamlit**
- **SQL Server**
- **pyodbc**
- **Pandas**
- **NumPy**
- **Plotly / Matplotlib**
- **OpenPyXL / XLRD**
- **ReportLab**
- **Folium / streamlit-folium**
- **scikit-learn**
- **Requests**
- **python-dotenv**
- **bcrypt**

Las versiones específicas utilizadas por el proyecto deben consultarse en `requirements.txt`.

---

## 3. Arquitectura general

El proyecto utiliza una separación de responsabilidades basada principalmente en:

```text
Usuario
   │
   ▼
Streamlit
   │
   ▼
Controladores
   │
   ├────────────► Vistas
   │
   ▼
Modelos
   │
   ▼
SQL Server
   │
   ▼
ForceSyncDB_Worker
```

La organización principal del código sigue una estructura similar a **Modelo–Vista–Controlador (MVC)**:

```text
CIC/
├── controlador/
├── modelo/
├── vista/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── logs/
│   ├── development.md
│   ├── roadmap.md
│   └── dev_log.csv
└── docs/                    # Documentación técnica progresiva
```

> La estructura puede contener archivos o recursos adicionales según la versión local del proyecto.

---

## 4. Módulos funcionales

Entre las principales capacidades identificadas en CIC v1 se encuentran:

### Cuadrantes comerciales

Análisis que relaciona indicadores como ventas, movilidad, actividad, visitas y tiempos para facilitar la interpretación del comportamiento comercial.

### Visualización de ventas

Incluye análisis históricos como:

- categorías vs. ingresos;
- clases vs. cantidad;
- clases vs. ingresos;
- clientes vs. ingresos.

### Importación de ventas

Procesamiento de archivos Excel utilizados para incorporar información de ventas al flujo de análisis.

### Presupuesto y metas

Comparación entre objetivos comerciales e ingresos/resultados obtenidos.

### Seguimiento de ForceManager

Funciones orientadas al seguimiento del uso y registro de actividad comercial de los vendedores.

### Movilidad

Registro y análisis de información de movilidad para complementar los indicadores comerciales.

### Reportes PDF

Generación de reportes por vendedor y periodo con información de ventas, metas, movilidad y otros indicadores disponibles.

El reporte de seguimiento estratégico puede incorporar la **fotografía del vendedor** en la primera página. La fotografía se obtiene desde el módulo administrativo y se dibuja directamente sobre el `canvas` de ReportLab, evitando modificar los márgenes y la distribución de las tablas del reporte.

### Administración

Funciones relacionadas con usuarios, autenticación, navegación y administración de la aplicación.

El módulo **Administrar Vendedores** incluye una pestaña `📷 Fotografías` para registrar, visualizar, reemplazar y eliminar la fotografía asociada a cada vendedor. La relación vendedor → archivo se conserva en `modelo/admin/vendedores_activos.json`, mientras que las imágenes se almacenan en la carpeta configurada mediante `FOTOS_VENDEDORES`.

---

## 5. Base de datos

CIC utiliza **Microsoft SQL Server**.

La base utilizada por la aplicación actual es:

```text
ForceSyncDB_Worker
```

Entre las entidades identificadas en el proyecto se encuentran:

```text
Users
Accounts
Activities
Calendars
Opportunities
dev_Detalle_Corregida
UsuariosCIC
PresupuestoSegmentos
Metas
MovilidadRegistro
ResumenMovilidad
NotificacionesVendedores
StrikesVendedores
ClientesActivos
ClientesBase
ClientesNuevos
```

CIC combina información procedente de ForceSync/ForceManager con información generada o administrada por el propio sistema.

La descripción detallada de tablas, relaciones, origen de datos y reglas de negocio deberá mantenerse en `docs/database.md`.

---

## 6. Requisitos

### Software

- Python compatible con las dependencias definidas en `requirements.txt`.
- Microsoft SQL Server o acceso a la instancia correspondiente.
- Driver ODBC compatible con SQL Server.
- Git.
- Acceso de red a los servicios externos utilizados por el proyecto cuando corresponda.

### Accesos

Dependiendo de la funcionalidad utilizada pueden requerirse:

- credenciales de SQL Server;
- token/API de Banxico;
- cuenta de correo para envío de reportes;
- rutas de recursos utilizados en los PDF.

---

## 7. Instalación

### 7.1 Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd CIC
```

### 7.2 Crear un entorno virtual

En Windows:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

En CMD:

```cmd
python -m venv venv
venv\Scripts\activate
```

### 7.3 Instalar dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 8. Configuración

Crear un archivo `.env` en la raíz del proyecto.

**No subir `.env` al repositorio.**

Plantilla de referencia:

```dotenv
# Credenciales DB SQL Server
SERVER=
DATABASE=
USERNAME=
PASSWORD=
DRIVER=

# Banxico — tipo de cambio
BANXICO=
SERIE_BANXICO=

# Destinatarios de reportes
CORREO_REPORTES_1=
CORREO_REPORTES_2=
CORREO_REPORTES_3=

# Correo emisor
CORREO_EMISOR=
APP_PASSWORD=

# Recursos y rutas de reportes
LOGO_PDF=
CARPETA_REPORTES=
CARPETA_DESTINO=

# Márgenes / elementos gráficos de los reportes
ENCABEZADO_GRIS=C:\MargenesReporte\encabezado_gris.png
ENCABEZADO_ROJO=C:\MargenesReporte\encabezado_rojo.png
PIE_ROJO=C:\MargenesReporte\pie_rojo.png

# Nomenclatura de control documental / Norma ISO
CODIGO_NORMA=Código: FO-C1-CM-06
REVISION_NORMA=Revisión: 4.0
FECHA_APLICACION_NORMA=Fecha de aplicación: 17 de agosto 2026
```

Los valores anteriores asociados a rutas son referencias de configuración histórica. Deben ajustarse a la instalación correspondiente.

Se recomienda mantener también un archivo `.env.example` sin secretos para documentar la configuración requerida.

---

## 9. Seguridad de configuración

Nunca almacenar en Git:

- contraseñas;
- tokens;
- API keys;
- `APP_PASSWORD`;
- archivos `.env` reales;
- credenciales de SQL Server.

Verificar que `.gitignore` incluya como mínimo:

```gitignore
.env
venv/
.venv/
__pycache__/
*.pyc
```

Si una credencial fue subida accidentalmente a Git, eliminarla del archivo no es suficiente: la credencial debe considerarse comprometida y rotarse.

---

## 10. Ejecución

Con el entorno virtual activo y el archivo `.env` configurado:

```bash
streamlit run main.py
```

Streamlit mostrará en la terminal la dirección local desde la cual acceder a la aplicación.

---

## 11. Reportes PDF

CIC genera reportes comerciales que pueden incorporar información como:

- vendedor;
- periodo;
- ventas;
- metas;
- clases o categorías;
- comportamiento mensual;
- movilidad;
- actividad comercial;
- elementos de control documental.

Los reportes utilizan recursos externos configurados mediante variables de entorno, por ejemplo:

```text
LOGO_PDF
ENCABEZADO_GRIS
ENCABEZADO_ROJO
PIE_ROJO
FOTOS_VENDEDORES
CARPETA_REPORTES
CARPETA_DESTINO
```

Por este motivo, una instalación nueva debe validar estas rutas antes de probar la generación de reportes.

`FOTOS_VENDEDORES` debe apuntar a la carpeta donde CIC almacenará las fotografías administradas desde Streamlit. Ejemplo:

```env
FOTOS_VENDEDORES=C:\Users\Administrador\Documents\ReportesCIC\FotoVendedores
```

El usuario de Windows que ejecute CIC debe disponer de permisos de **lectura, escritura y modificación** sobre esa carpeta, ya que la aplicación crea, reemplaza y elimina archivos de imagen.

---

## 12. Flujo general de desarrollo

Para cambios nuevos se recomienda utilizar el siguiente flujo:

```text
Necesidad / incidencia
        │
        ▼
Análisis
        │
        ▼
Desarrollo
        │
        ▼
Pruebas
        │
        ▼
Commit Git
        │
        ▼
Registro en dev_log.csv
```

Los commits deben describir el cambio realizado y evitar mezclar modificaciones no relacionadas siempre que sea posible.

---

## 13. Documentación del proyecto

La documentación se divide según su propósito.

### `logs/development.md`

Describe **cómo evolucionó CIC hasta su estado actual**.

Incluye una reconstrucción retrospectiva de la etapa anterior al uso formal de Git y separa esa información del historial verificable mediante commits.

### `logs/roadmap.md`

Describe **hacia dónde se dirige CIC**.

Incluye:

- mantenimiento de CIC v1;
- deuda técnica;
- documentación pendiente;
- estabilización;
- criterios de migración;
- relación entre CIC v1 y CIC v2.

### `logs/dev_log.csv`

Registra **qué se modifica a partir de la formalización de la documentación**.

Cada cambio relevante debe registrar, cuando aplique:

- fecha;
- versión;
- módulo;
- tipo de cambio;
- descripción;
- motivo;
- estado;
- pruebas;
- commit;
- fuente;
- observaciones.

### Documentación técnica

Se contempla desarrollar progresivamente:

```text
docs/
├── architecture.md
├── database.md
├── modules.md
├── reports.md
└── decisions.md
```

---

## 14. CIC v1 y CIC v2

CIC v1 continúa siendo la aplicación operativa y una referencia importante de reglas de negocio.

CIC v2 se desarrolla como una nueva versión y debe mantenerse como proyecto separado.

La migración no debe consistir únicamente en trasladar código existente. Para cada funcionalidad de CIC v1 deberá determinarse si corresponde:

- mantenerla;
- rediseñarla;
- reemplazarla;
- combinarla;
- descartarla.

Cuando una regla de negocio sea reimplementada en CIC v2, los resultados deberán validarse contra CIC v1 cuando sea posible.

---

## 15. Estado de la documentación

La documentación formal del proyecto comenzó de manera retrospectiva después de que CIC ya contaba con una cantidad considerable de funcionalidades.

Por esta razón:

- algunas fechas históricas anteriores a Git no están disponibles;
- no deben inventarse fechas para completar el historial;
- los hechos reconstruidos deben distinguirse de los verificables mediante Git;
- a partir de la formalización documental, los cambios nuevos deben registrarse de manera consistente.

---

## 16. Próximos documentos técnicos

De acuerdo con el roadmap actual, las siguientes piezas recomendadas son:

1. `docs/architecture.md`
2. `docs/database.md`
3. `docs/modules.md`
4. `docs/reports.md`
5. `docs/decisions.md`

Estos documentos permitirán trasladar conocimiento que actualmente puede encontrarse únicamente en el código o en la experiencia del desarrollador hacia documentación mantenible.

---

## 17. Mantenimiento

Antes de modificar una funcionalidad existente:

1. identificar el módulo afectado;
2. comprender la regla de negocio;
3. revisar dependencias con otros módulos;
4. realizar el cambio de forma incremental;
5. validar el resultado;
6. crear un commit descriptivo;
7. registrar el cambio en `logs/dev_log.csv`;
8. actualizar documentación adicional si la modificación cambia arquitectura, configuración o comportamiento funcional.

---

## 18. Nota sobre documentación histórica

El historial Git disponible comienza cuando CIC ya se encontraba en una etapa avanzada de desarrollo.

Por lo tanto, Git debe considerarse una fuente verificable **a partir del punto en que comenzó a utilizarse**, pero no como representación completa del origen del proyecto.

Para conocer la evolución reconstruida del sistema, consultar:

```text
logs/development.md
```
