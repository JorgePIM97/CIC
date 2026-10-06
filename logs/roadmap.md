# CIC — Roadmap de Desarrollo

**Proyecto:** CIC — Inteligencia Comercial  
**Documento:** Roadmap de desarrollo y evolución  
**Estado:** Activo  
**Última actualización:** 06/10/2026  

---

## 1. Propósito del roadmap

Este documento define la dirección de evolución de CIC a partir del estado actual de la aplicación y de la reconstrucción histórica documentada en `development.md`.

El roadmap no pretende asignar fechas retroactivas a funcionalidades desarrolladas antes del inicio del historial Git disponible. Su objetivo es establecer una línea base para organizar el mantenimiento de CIC v1, registrar mejoras futuras y orientar la transición progresiva hacia CIC v2.

---

## 2. Objetivo del proyecto

CIC surgió como una herramienta de inteligencia comercial para relacionar los resultados de ventas con el comportamiento y la actividad de los vendedores.

El sistema busca proporcionar información que permita analizar situaciones como:

- ventas bajas con baja movilidad;
- ventas altas con baja movilidad;
- ventas bajas con alta movilidad;
- ventas altas con alta movilidad;
- variaciones importantes de ventas entre periodos;
- nivel de actividad comercial;
- tiempos destinados a visitas y atención de clientes;
- cumplimiento de presupuestos o metas;
- uso de ForceManager;
- comportamiento comercial por vendedor, mes y año.

La evolución del proyecto ha ampliado este objetivo hacia la integración, visualización, seguimiento y generación de reportes de información comercial.

---

## 3. Estado general

Actualmente existen dos líneas de trabajo:

### CIC v1

Aplicación operativa desarrollada principalmente con Python, Streamlit y SQL Server.

CIC v1 continuará recibiendo mantenimiento, correcciones y mejoras necesarias mientras siga siendo utilizado.

### CIC v2

Nueva versión desarrollada en paralelo.

La versión 2 no debe considerarse una simple copia del sistema actual. CIC v1 servirá como referencia funcional y fuente de requisitos, mientras que las funcionalidades deberán evaluarse individualmente antes de ser migradas, rediseñadas o descartadas.

---

## 4. Capacidades consolidadas de CIC v1

Las siguientes áreas forman parte de la línea base funcional identificada en el proyecto actual.

### 4.1 Cuadrantes de análisis comercial

Los cuadrantes constituyen una de las funcionalidades que dieron origen a CIC.

Permiten comparar diferentes indicadores relacionados con el comportamiento comercial, entre ellos:

- ventas;
- movilidad;
- actividad;
- visitas;
- tiempo destinado a visitas o atención;
- otros indicadores derivados de la información comercial disponible.

El objetivo es facilitar la identificación de patrones de comportamiento entre actividad y resultados.

**Estado:** Implementado / mantenimiento.

---

### 4.2 Análisis y visualización de ventas

CIC permite analizar información comercial desde diferentes perspectivas.

Entre las visualizaciones históricamente incorporadas se encuentran:

- categorías vs. ingresos;
- clases vs. cantidad;
- clases vs. ingresos;
- clientes vs. ingresos.

El proyecto actual contiene además lógica asociada al procesamiento y consulta de información de ventas.

**Estado:** Implementado / mantenimiento.

---

### 4.3 Importación de archivos de ventas

El sistema cuenta con funcionalidad para incorporar información proveniente de archivos Excel de ventas.

Esta etapa permite alimentar posteriormente los análisis comerciales del sistema.

**Estado:** Implementado / mantenimiento.

**Línea de mejora:** fortalecer validaciones, trazabilidad de importaciones y manejo explícito de errores conforme evolucione el sistema.

---

### 4.4 Presupuesto y metas

CIC incorpora información de presupuesto/metas para comparar los objetivos comerciales contra los ingresos reales.

Esta información también participa en análisis y reportes.

**Estado:** Implementado / mantenimiento.

---

### 4.5 Seguimiento del uso de ForceManager

CIC contiene funcionalidades destinadas a ayudar a identificar si los vendedores están utilizando la aplicación ForceManager y registrando actividad comercial.

El objetivo es evitar que la ausencia de registros distorsione el análisis del desempeño.

**Estado:** Implementado / mantenimiento.

---

### 4.6 Movilidad

El sistema incorpora información de movilidad para complementar el análisis comercial.

La movilidad se utiliza junto con ventas y actividad para evaluar el comportamiento de los vendedores.

**Estado:** Implementado / mantenimiento.

---

### 4.7 Reportes PDF

CIC genera reportes de seguimiento por:

- vendedor;
- mes;
- año.

Los reportes integran información de ventas y movilidad, además de indicadores comerciales disponibles.

Durante septiembre de 2026 se realizaron cambios verificables mediante Git relacionados con la actualización del reporte y sus elementos visuales.

El 06/10/2026 se integró la fotografía administrable del vendedor en la primera página del reporte, utilizando `canvas` para conservar la distribución existente del documento.

**Estado:** Implementado / evolución activa.

---

### 4.8 Administración y autenticación

El proyecto actual contiene componentes relacionados con:

- autenticación;
- usuarios;
- administración;
- navegación;
- permisos o control de acceso;
- administración de fotografías de vendedores para reportes PDF.

**Estado:** Implementado / mantenimiento.

---

## 5. Prioridades de CIC v1

Mientras CIC v2 continúa su desarrollo, CIC v1 debe mantenerse estable y documentado.

### Prioridad 1 — Estabilidad operativa

Objetivo: evitar que las mejoras de CIC v1 afecten funcionalidades que ya son utilizadas.

Acciones:

- corregir errores detectados en operación;
- validar cambios antes de integrarlos;
- mantener compatibilidad con la base de datos actual;
- evitar refactorizaciones extensas sin necesidad funcional;
- mantener respaldos y control de versiones;
- registrar cambios relevantes en `dev_log.csv`.

---

### Prioridad 2 — Documentación

Objetivo: eliminar progresivamente la dependencia del conocimiento informal del desarrollador.

Documentos base:

- `README.md`;
- `development.md`;
- `roadmap.md`;
- `dev_log.csv`.

Documentación adicional recomendada:

- `docs/architecture.md`;
- `docs/database.md`;
- `docs/modules.md`;
- `docs/reports.md`;
- `docs/decisions.md`.

---

### Prioridad 3 — Trazabilidad del desarrollo

A partir de esta etapa, cada cambio relevante debe poder relacionarse con:

1. una necesidad;
2. un módulo;
3. una modificación;
4. una prueba;
5. un commit.

Los cambios futuros deben registrarse en `dev_log.csv` y Git.

---

### Prioridad 4 — Confiabilidad de los datos

Debido a que CIC utiliza información procedente de diferentes procesos y fuentes, las modificaciones futuras deben prestar especial atención a:

- validación de archivos importados;
- consistencia de vendedores;
- periodos de consulta;
- valores faltantes;
- duplicados;
- conversiones y cálculos;
- correspondencia entre actividad, movilidad y ventas;
- manejo de errores de base de datos.

---

## 6. Deuda técnica identificada o a evaluar

Esta sección distingue problemas observables del proyecto de mejoras que todavía requieren evaluación.

### 6.1 Archivos de gran tamaño

Existen módulos Python que concentran una cantidad considerable de lógica.

Esto puede incrementar:

- dificultad de mantenimiento;
- acoplamiento;
- tiempo necesario para localizar errores;
- riesgo de afectar funcionalidades no relacionadas.

**Acción propuesta:** identificar responsabilidades internas y dividir gradualmente solo cuando exista beneficio claro y pruebas suficientes.

**Prioridad:** Media.

---

### 6.2 Separación de responsabilidades

Aunque el proyecto presenta una organización `modelo/`, `vista/` y `controlador/`, algunos módulos han crecido considerablemente con el tiempo.

**Acción propuesta:** documentar primero las responsabilidades actuales antes de realizar refactorizaciones.

**Prioridad:** Media.

---

### 6.3 Configuración y variables de entorno

El proyecto utiliza configuración externa para información sensible y rutas.

**Acciones propuestas:**

- mantener `.env` fuera de Git;
- conservar una plantilla `.env.example` sin credenciales;
- documentar variables obligatorias;
- reducir rutas absolutas cuando sea viable;
- centralizar configuración progresivamente.

**Prioridad:** Alta.

---

### 6.4 Codificación de archivos

Durante la revisión documental se identificaron archivos que deben revisarse respecto a su codificación.

**Acción propuesta:** normalizar documentación y archivos de texto a UTF-8 cuando pueda hacerse sin afectar el funcionamiento.

**Prioridad:** Baja.

---

### 6.5 Pruebas automatizadas

La cobertura actual de pruebas automatizadas debe evaluarse formalmente.

**Acción propuesta:**

Comenzar por lógica crítica y determinista:

- cálculos de ventas;
- presupuestos;
- cumplimiento;
- importación/normalización de datos;
- cálculos de movilidad;
- funciones utilizadas en reportes.

**Prioridad:** Alta para la evolución futura.

---

### 6.6 Dependencias

El proyecto utiliza múltiples librerías para interfaz, análisis, Excel, gráficos, mapas, PDF y conexión con SQL Server.

**Acciones propuestas:**

- revisar dependencias realmente utilizadas;
- fijar versiones cuando sea necesario;
- eliminar dependencias obsoletas;
- documentar procedimiento reproducible de instalación.

**Prioridad:** Media.

---

## 7. Roadmap por fases

### Fase A — Recuperación documental

**Objetivo:** documentar correctamente el sistema existente antes de realizar cambios estructurales importantes.

- [x] Reconstruir origen del proyecto.
- [x] Identificar orden histórico de las principales funcionalidades.
- [x] Separar etapa pre-Git del historial verificable.
- [x] Crear `development.md`.
- [x] Crear `roadmap.md`.
- [ ] Crear `dev_log.csv`.
- [ ] Actualizar `README.md`.
- [ ] Documentar arquitectura.
- [ ] Documentar base de datos.
- [ ] Documentar módulos.
- [ ] Documentar generación de reportes.
- [ ] Registrar decisiones técnicas relevantes.

---

### Fase B — Estabilización de CIC v1

**Objetivo:** mantener la aplicación actual confiable mientras CIC v2 se desarrolla.

- [ ] Definir checklist mínimo de pruebas manuales.
- [ ] Identificar módulos críticos.
- [ ] Registrar errores conocidos.
- [ ] Revisar configuración y variables de entorno.
- [ ] Revisar rutas absolutas.
- [ ] Revisar dependencias.
- [ ] Identificar consultas SQL críticas.
- [ ] Revisar manejo de excepciones.
- [ ] Definir procedimiento de respaldo antes de cambios sensibles.

---

### Fase C — Calidad y mantenibilidad

**Objetivo:** reducir deuda técnica sin comprometer la operación de CIC v1.

- [ ] Identificar funciones y clases excesivamente grandes.
- [ ] Detectar código duplicado.
- [ ] Separar lógica de negocio de presentación cuando sea necesario.
- [ ] Centralizar configuración reutilizada.
- [ ] Incorporar pruebas para cálculos críticos.
- [ ] Incorporar validaciones para importaciones.
- [ ] Normalizar documentación a UTF-8.
- [ ] Mejorar comentarios y docstrings donde aporten contexto real.

Las refactorizaciones de esta fase deben realizarse de forma incremental.

---

### Fase D — Inventario funcional para CIC v2

**Objetivo:** convertir CIC v1 en una fuente explícita de requisitos para la nueva versión.

Para cada funcionalidad de CIC v1 se deberá decidir:

- mantener;
- rediseñar;
- reemplazar;
- combinar con otra funcionalidad;
- descartar.

Inventario inicial:

- [ ] Cuadrantes comerciales.
- [ ] Visualización de ventas.
- [ ] Importación de ventas.
- [ ] Presupuesto y metas.
- [ ] Seguimiento de ForceManager.
- [ ] Movilidad.
- [ ] Reportes PDF.
- [ ] Administración.
- [ ] Autenticación.
- [ ] Perfiles y rendimiento.
- [ ] Planeación.
- [ ] Kilometraje.

---

### Fase E — Transición hacia CIC v2

**Objetivo:** permitir una migración controlada sin perder reglas de negocio validadas en CIC v1.

Principios:

1. CIC v1 permanece como referencia funcional.
2. No se migra código únicamente porque ya exista.
3. Primero se identifica la regla de negocio.
4. Después se define su representación en CIC v2.
5. Los resultados de ambas versiones deberán compararse en funcionalidades críticas.
6. Las diferencias deberán documentarse.
7. CIC v1 no se retira hasta que las funciones necesarias estén cubiertas y validadas en CIC v2.

---

## 8. Criterios para decidir qué migrar a CIC v2

Cada módulo deberá evaluarse con preguntas como:

### Valor de negocio

- ¿La funcionalidad sigue siendo utilizada?
- ¿Ayuda a tomar una decisión comercial?
- ¿Responde al problema original de CIC?
- ¿Existe una alternativa mejor en la nueva arquitectura?

### Calidad de datos

- ¿La fuente seguirá existiendo?
- ¿Los datos son confiables?
- ¿La regla de cálculo continúa siendo válida?

### Diseño técnico

- ¿Conviene reutilizar la lógica?
- ¿Conviene reescribirla?
- ¿Está demasiado acoplada a Streamlit o SQL?
- ¿Debe convertirse en lógica de API?

### Validación

- ¿Cómo comprobaremos que CIC v2 produce el mismo resultado esperado?
- ¿Existe un conjunto de datos con el cual comparar ambas versiones?

---

## 9. Funcionalidades que no deben perderse durante la transición

Independientemente de la implementación técnica futura, CIC v2 deberá evaluar explícitamente las reglas de negocio relacionadas con:

- relación entre ventas y movilidad;
- comportamiento comercial por vendedor;
- análisis temporal de ventas;
- categorías, clases y clientes;
- presupuesto/meta contra resultados;
- actividad registrada en ForceManager;
- movilidad y visitas;
- generación de información de seguimiento por vendedor y periodo.

Esta lista es una línea base, no una especificación definitiva de CIC v2.

---

## 10. Gestión de cambios a partir de octubre de 2026

A partir de la formalización de la documentación:

### Antes de desarrollar

Definir:

- problema;
- módulo afectado;
- comportamiento esperado.

### Durante el desarrollo

Mantener:

- cambios pequeños cuando sea posible;
- commits descriptivos;
- separación entre correcciones y nuevas funcionalidades.

### Después del desarrollo

Registrar:

- fecha;
- módulo;
- cambio;
- motivo;
- resultado;
- pruebas realizadas;
- commit asociado.

El registro estructurado se mantendrá en `dev_log.csv`.

---

## 11. Convención de estados

Para mantener este roadmap actualizado se utilizarán los siguientes estados:

| Estado | Significado |
|---|---|
| Pendiente | Aún no iniciado |
| En análisis | Requiere investigación o definición |
| En desarrollo | Trabajo activo |
| En pruebas | Implementado y pendiente de validación |
| Implementado | Disponible en la aplicación |
| Mantenimiento | Funcionalidad existente que continúa recibiendo soporte |
| Bloqueado | Existe una dependencia que impide avanzar |
| Descartado | Se decidió no continuar |
| Migrado a v2 | Funcionalidad cubierta y validada en CIC v2 |

---

## 12. Riesgos principales

### Pérdida de conocimiento

Gran parte de la historia inicial no quedó registrada durante el desarrollo original.

**Mitigación:** documentación retrospectiva y registro obligatorio de cambios futuros.

### Regresiones en CIC v1

Una modificación puede afectar análisis que ya son utilizados.

**Mitigación:** cambios incrementales, pruebas y control de versiones.

### Diferencias entre CIC v1 y CIC v2

Una reimplementación puede producir resultados distintos sin que la diferencia sea evidente.

**Mitigación:** comparar resultados utilizando los mismos datos y documentar reglas de negocio.

### Dependencia de conocimiento individual

Algunas reglas pueden estar implícitas únicamente en el código o en el conocimiento del desarrollador.

**Mitigación:** trasladar progresivamente esas reglas a documentación técnica y pruebas.

---

## 13. Próximos pasos inmediatos

Orden recomendado:

1. Mantener `dev_log.csv` actualizado con cada cambio relevante. — **En curso**
2. Mantener `README.md` sincronizado con requisitos de instalación y configuración. — **En curso**
3. `docs/architecture.md`. — **Completado**
4. `docs/database.md`. — **Completado**
5. `docs/modules.md`. — **Completado**
6. `docs/reports.md`. — **Completado**
7. `docs/decisions.md`. — **Completado**
8. Definir checklist de pruebas de CIC v1. — **Pendiente**
9. Construir inventario funcional CIC v1 → CIC v2. — **Pendiente**
10. Continuar la evolución controlada del reporte PDF y registrar cada cambio en documentación y Git. — **En curso**

---

## 14. Regla de mantenimiento del roadmap

Este archivo debe reflejar el estado real del proyecto.

Cuando una tarea cambie de estado deberá actualizarse este documento. Las modificaciones técnicas concretas deberán registrarse además en `dev_log.csv` y Git.

`roadmap.md` define **hacia dónde va CIC**.

`development.md` explica **cómo llegó CIC hasta su estado actual**.

`dev_log.csv` registrará **qué se modifica a partir de ahora**.
