# CIC — Historial de desarrollo

## 1. Propósito de este documento

Este documento registra la evolución técnica y funcional del proyecto **CIC (Inteligencia Comercial)**. Fue creado de manera retrospectiva debido a que las primeras etapas del proyecto no contaron con un historial formal de desarrollo.

Para evitar atribuir fechas o decisiones que no puedan comprobarse, el historial se divide en dos periodos:

- **Etapa pre-Git:** reconstruida a partir del código actual y del testimonio del desarrollador. Las fechas exactas no están documentadas.
- **Etapa con Git:** respaldada por el historial disponible del repositorio a partir del 2 de septiembre de 2026.

A partir de la creación de este documento, los cambios relevantes de CIC deberán registrarse de manera continua.

---

## 2. Origen y problema de negocio

CIC surge a partir de una necesidad planteada por la dirección de la empresa: comprender mejor el comportamiento de la fuerza comercial y no evaluar a los vendedores únicamente por el monto de sus ventas.

Se identificaron distintos escenarios entre los vendedores:

- bajas ventas y poca movilidad;
- altas ventas y poca movilidad;
- bajas ventas a pesar de una alta movilidad;
- altas ventas acompañadas de alta movilidad.

También se observó la necesidad de analizar la **continuidad del desempeño**. Un vendedor podía obtener ventas considerablemente altas durante un mes y presentar resultados mucho menores en los meses posteriores. Esto generó la necesidad de analizar si, después de alcanzar un buen resultado, disminuían su movilidad, visitas, actividad comercial o búsqueda de nuevas oportunidades.

Por esta razón, CIC comenzó como una herramienta orientada a relacionar **ventas, movilidad y actividad comercial**, con el propósito de proporcionar información objetiva para el seguimiento de vendedores y la toma de decisiones comerciales.

---

## 3. Evolución funcional reconstruida — etapa pre-Git

> **Nota:** las fechas exactas de esta sección no se encuentran registradas. El orden fue reconstruido retrospectivamente con base en el código actual y en información proporcionada por el desarrollador.

### 3.1 Cuadrantes de Gartner

La primera funcionalidad principal de CIC fue el desarrollo de cuadrantes internos para comparar el comportamiento de los vendedores utilizando diferentes indicadores comerciales.

Entre las relaciones implementadas o consideradas se encuentran:

- movilidad vs. ventas;
- actividad vs. movilidad;
- visitas vs. movilidad;
- visitas vs. ventas;
- ventas reales vs. movilidad/GPS;
- tiempos de visita;
- tiempos promedio de visita;
- tareas y actividades.

El objetivo fue facilitar la identificación de patrones de comportamiento que no podían observarse analizando únicamente el total de ventas.

El término **“Cuadrantes de Gartner”** se utiliza internamente en CIC para estas representaciones comparativas; no implica que se trate del Gartner Magic Quadrant comercial.

### 3.2 Módulo de visualización de ventas

Posteriormente se incorporaron herramientas para consultar y visualizar las ventas desde distintas perspectivas:

- categorías vs. ingresos;
- clases vs. cantidad;
- clases vs. ingresos;
- clientes vs. ingresos.

Este módulo amplió CIC desde el análisis del comportamiento del vendedor hacia el análisis de la composición de sus ventas.

### 3.3 Importación de archivos Excel de ventas

Se desarrolló un módulo para incorporar archivos Excel con información de ventas al flujo de CIC.

Esta funcionalidad permitió preparar e integrar los datos utilizados posteriormente por los módulos de análisis comercial.

### 3.4 Presupuesto / metas vs. ingresos

Se agregó la comparación entre los objetivos comerciales y los resultados reales obtenidos.

El sistema permite relacionar información de presupuesto o metas con los ingresos registrados, facilitando el seguimiento del cumplimiento comercial por vendedor y periodo.

### 3.5 Seguimiento del uso de ForceManager

Se incorporaron funcionalidades orientadas a verificar que los vendedores estuvieran utilizando la aplicación ForceManager y registrando la actividad necesaria para el seguimiento comercial.

Esta etapa amplió CIC desde una herramienta exclusivamente analítica hacia una herramienta de seguimiento de disciplina y actividad comercial.

### 3.6 Registro de movilidad

Se agregó un módulo para ingresar y procesar información de movilidad de los vendedores.

Los datos de movilidad complementan los registros comerciales y permiten relacionar desplazamiento, visitas y actividad con los resultados de ventas.

### 3.7 Generación de reportes PDF

Finalmente, se incorporó la generación de reportes PDF que consolidan información de ventas y movilidad.

Los reportes se generan considerando principalmente:

- vendedor;
- mes;
- año;
- ventas e ingresos;
- presupuesto y cumplimiento;
- distribución de ventas;
- movilidad;
- visitas y actividad comercial.

El reporte funciona como un medio consolidado para consultar y compartir el desempeño comercial de cada vendedor durante un periodo determinado.

---

## 4. Inicio del historial verificable mediante Git

El historial Git disponible comienza el **2 de septiembre de 2026**. Para ese momento CIC ya contenía una cantidad considerable de funcionalidades, por lo que esta fecha debe interpretarse como el inicio del control de versiones actualmente disponible y no como el inicio del proyecto.

### 2 de septiembre de 2026

Commits disponibles:

- `a9fa5ae` — `first commit`
- `8c60737` — `segundo commit`
- `92b092a` — `tercer commit`

Estos commits establecen la primera referencia verificable del código de CIC en el repositorio actual.

### 4 de septiembre de 2026

- `09f270b` — `requirements_corregido`
  - Correcciones relacionadas con las dependencias del proyecto.

- `ad2bff5` — `reporte_update_1`
  - Actualización importante del módulo de reportes.
  - El commit modifica `modelo/exceles_modelo.py` con 162 inserciones y 9 eliminaciones.

### 7 de septiembre de 2026

- `4e88d11` — `limpia_comentarios_1`
  - Limpieza de comentarios/código.

- `772a186` — merge de la rama `main` remota.

- `fb3a0d2` — `margenes`
  - Modificación del diseño de márgenes del reporte PDF.

- `78f3ee4` — `margenes_acomodados`
  - Ajustes posteriores a la posición y presentación de los márgenes del reporte.

---

## 5. Arquitectura observada en el estado actual

CIC está desarrollado principalmente en **Python y Streamlit**, con acceso a **SQL Server** y una organización de código basada en separación entre controlador, modelo y vista.

Estructura principal:

```text
CIC/
├── main.py
├── controlador/
├── modelo/
├── vista/
├── README.md
├── requirements.txt
└── .gitignore
```

### Controlador

Contiene la lógica de coordinación entre las vistas y los modelos. Incluye controladores para:

- navegación y autenticación;
- administración;
- cuadrantes Gartner;
- perfiles y gráficas;
- rendimiento;
- reportes;
- ventas reales.

### Modelo

Contiene acceso a datos y lógica relacionada con:

- conexión a SQL Server;
- ventas reales;
- vendedores;
- usuarios;
- Gartner;
- importación y procesamiento de Excel;
- kilometraje;
- metas;
- presupuesto;
- planeación;
- movilidad;
- rendimiento;
- perfiles;
- reportes PDF.

### Vista

Contiene las interfaces de Streamlit para:

- login;
- administración;
- vendedores;
- ventas reales;
- perfiles;
- rendimiento;
- importación de Excel;
- kilometraje;
- metas;
- presupuesto;
- planeación;
- movilidad.

---

## 6. Papel actual de CIC

A partir de la evolución observada, CIC puede describirse como una **aplicación interna de inteligencia comercial** que integra información de ventas, actividad y movilidad para apoyar el seguimiento de la fuerza comercial.

Su evolución puede resumirse en cuatro capacidades principales:

1. **Adquisición e integración de información** — ventas, movilidad y datos relacionados con ForceManager.
2. **Análisis comercial** — ventas, clientes, categorías, clases y cuadrantes comparativos.
3. **Seguimiento del desempeño** — metas, presupuesto, actividad y uso de herramientas comerciales.
4. **Comunicación de resultados** — visualizaciones y reportes PDF por vendedor y periodo.

---

## 7. Relación con CIC versión 2

El proyecto descrito en este documento corresponde a la implementación actual/legada de CIC.

Existe una **versión 2 en desarrollo paralelo**. CIC v2 deberá documentarse de manera independiente, utilizando el sistema actual como fuente de:

- requisitos funcionales existentes;
- reglas de negocio;
- consultas y fuentes de datos;
- funcionalidades que deben conservarse;
- problemas técnicos que deben corregirse o rediseñarse.

No se debe asumir que la arquitectura de CIC actual será replicada directamente en CIC v2.

---

## 8. Política de documentación a partir de este punto

A partir de octubre de 2026, todo cambio relevante deberá registrarse mediante:

- un commit descriptivo en Git;
- una entrada en `logs/dev_log.csv` cuando represente una actividad de desarrollo relevante;
- actualización de `development.md` cuando se alcance un nuevo hito o exista una decisión arquitectónica importante;
- actualización de `roadmap.md` cuando cambien prioridades, alcance o estado de funcionalidades;
- actualización del `README.md` cuando cambien requisitos de instalación, configuración o ejecución.

Los mensajes de commit deberán describir el cambio realizado y evitar nombres genéricos como `cambio`, `update`, `segundo commit` o similares.

---

## 9. Información histórica pendiente de reconstrucción

Aún no se cuenta con evidencia suficiente para establecer con precisión:

- fecha exacta de inicio de CIC;
- duración de cada etapa pre-Git;
- fechas de implementación de los siete módulos históricos;
- versiones o prototipos intermedios previos al repositorio actual;
- decisiones arquitectónicas tomadas durante las primeras etapas;
- cambios relevantes realizados antes del 2 de septiembre de 2026.

Estos datos podrán incorporarse posteriormente cuando exista evidencia o puedan ser confirmados por el desarrollador.
