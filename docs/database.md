# CIC — Base de Datos y Mapa de Información

**Proyecto:** CIC — Centro de Inteligencia Comercial  
**Versión documentada:** CIC v1  
**Base de datos principal:** `ForceSyncDB_Worker`  
**Motor:** Microsoft SQL Server  
**Estado:** Reconstrucción técnica basada en el código actual  
**Última actualización:** 05/10/2026  

---

## 1. Propósito

Este documento describe cómo CIC v1 utiliza la base de datos.

La documentación fue reconstruida a partir de las consultas SQL presentes en el código del proyecto. Por lo tanto, describe con bastante precisión el **contrato de datos utilizado por CIC**, pero no sustituye el esquema oficial de SQL Server.

En particular, el repositorio revisado no contiene el DDL completo de la base (`CREATE TABLE`, `CREATE VIEW`, constraints, índices y claves foráneas).

Por este motivo, este documento distingue entre:

- **Confirmado por código:** tabla, vista, columna, consulta u operación visible en CIC.
- **Relación lógica observada:** relación utilizada explícitamente mediante `JOIN`, comparación o regla de aplicación.
- **Inferido:** interpretación razonable del propósito del objeto, pendiente de validar contra SQL Server.
- **Pendiente de validar:** información que requiere consultar directamente el catálogo de la base.

No se deben interpretar las relaciones lógicas aquí descritas como claves foráneas físicas salvo que posteriormente se confirme en SQL Server.

---

# 2. Conexión

La conexión está centralizada en:

```text
modelo/db_connection.py
```

mediante:

```text
DatabaseConnection
```

La configuración se obtiene del archivo `.env`.

Variables cargadas:

```text
SERVER
DATABASE
USERNAME
PASSWORD
DRIVER
```

La implementación activa observada utiliza autenticación integrada:

```text
Trusted_Connection=yes
```

Por lo tanto:

```text
CIC
 │
 ▼
pyodbc
 │
 ▼
ODBC Driver
 │
 ▼
SQL Server
 │
 ▼
ForceSyncDB_Worker
```

Aunque `USERNAME` y `PASSWORD` están disponibles en configuración, la cadena activa no los utiliza.

Existe código alternativo/comentado para autenticación SQL mediante `UID` y `PWD`.

---

# 3. Clasificación general de los datos

El código permite identificar tres grandes grupos.

## 3.1 Datos procedentes del ecosistema ForceSync / ForceManager

Entidades núcleo observadas:

```text
Users
Accounts
Activities
Calendars
Opportunities
vw_Activities
```

Estas estructuras representan vendedores, cuentas/clientes, actividades, planeación/calendario y oportunidades comerciales.

---

## 3.2 Datos procesados o complementarios utilizados por CIC

Objetos relevantes:

```text
dev_Detalle_Corregida
vw_CategoriaIngresos
```

`dev_Detalle_Corregida` funciona como una fuente central de ventas procesadas/importadas.

`vw_CategoriaIngresos` funciona como fuente derivada para análisis por categorías.

---

## 3.3 Datos administrados por CIC

Objetos identificados:

```text
UsuariosCIC
Metas
PresupuestoSegmentos
MovilidadRegistro
ResumenMovilidad
NotificacionesVendedores
StrikesVendedores
```

Estas estructuras almacenan información necesaria para funcionalidades propias de CIC.

---

# 4. Mapa lógico general

```text
                        ForceSync / ForceManager
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
           Users               Accounts          Activities
                                  │                   │
                                  │                   │
                                  ├──────────┐        │
                                  ▼          ▼        │
                              Calendars  Opportunities │
                                  │          │        │
                                  └──────┬───┴────────┘
                                         │
                                         ▼
                                       CIC
                                         │
            ┌────────────────────────────┼──────────────────────────┐
            │                            │                          │
            ▼                            ▼                          ▼
 dev_Detalle_Corregida              Metas / Presupuesto      Movilidad
            │                            │                          │
            ▼                            ▼                          ▼
 vw_CategoriaIngresos             Rendimiento             ResumenMovilidad
            │
            ▼
     Análisis de ventas
```

Además:

```text
UsuariosCIC
    │
    └── autenticación / permisos / correo

Calendars + Accounts
    │
    └── planeación
            │
            ├── NotificacionesVendedores
            └── StrikesVendedores
```

---

# 5. Inventario principal

| Objeto | Tipo observado | Origen lógico | Lectura | Escritura | Uso principal |
|---|---|---|---|---|---|
| `Users` | Tabla | ForceSync | Sí | No observada | Vendedores |
| `Accounts` | Tabla | ForceSync | Sí | No observada | Clientes/cuentas |
| `Activities` | Tabla | ForceSync | Sí | No observada | Actividad, visitas, GPS |
| `Calendars` | Tabla | ForceSync | Sí | No observada | Planeación/actividades |
| `Opportunities` | Tabla | ForceSync | Sí | No observada | Ventas/oportunidades/clientes |
| `vw_Activities` | Vista | ForceSync/derivada | Sí | No | Tiempo de visitas |
| `dev_Detalle_Corregida` | Tabla procesada | CIC/importación | Sí | INSERT | Ventas reales |
| `vw_CategoriaIngresos` | Vista | Derivada | Sí | No | Categorías vs ingresos |
| `UsuariosCIC` | Tabla | CIC | Sí | UPDATE | Login, usuarios, correo |
| `Metas` | Tabla | CIC | Sí | INSERT/UPDATE | Meta mensual |
| `PresupuestoSegmentos` | Tabla | CIC | Sí | INSERT/UPDATE | Presupuesto por segmento |
| `MovilidadRegistro` | Tabla | CIC | Sí | INSERT/DELETE | Kilometraje |
| `ResumenMovilidad` | Tabla | CIC | Sí | INSERT/UPDATE | Resumen mensual movilidad |
| `NotificacionesVendedores` | Tabla | CIC | Sí | INSERT/DELETE | Seguimiento ForceManager |
| `StrikesVendedores` | Tabla | CIC | Sí | INSERT | Seguimiento ForceManager |

> “Origen lógico” se refiere al papel que el objeto desempeña dentro de CIC; debe validarse contra el esquema oficial antes de utilizarlo como clasificación administrativa de la base.

---

# 6. `Users`

## Propósito observado

Fuente de usuarios/vendedores procedentes del sistema ForceSync.

Archivos que la utilizan incluyen:

```text
modelo/exceles_modelo.py
modelo/vendedores_modelo.py
modelo/admin/admin_modelo.py
```

## Columnas observadas

```text
Id
Name
LastName
```

Pueden existir más columnas en SQL Server; estas son las identificadas directamente en las consultas revisadas.

## Uso

Se utiliza principalmente para:

- identificar vendedores;
- relacionar vendedores con información comercial;
- obtener nombres e identificadores.

## Escritura

No se identificaron escrituras de CIC sobre `Users`.

**Tratamiento recomendado:** solo lectura desde CIC.

---

# 7. `Accounts`

## Propósito observado

Representa cuentas, clientes y prospectos.

Archivos consumidores:

```text
modelo/cobertura_cartera_modelo.py
modelo/perfiles_modelo.py
modelo/planeacion_modelo.py
modelo/reporte_pdf/*
```

## Columnas observadas

```text
Id
Name
DateCreated
Deleted
SalesRepId1_Value
TypeId_Value
```

## Valores de negocio observados

`TypeId_Value` es utilizado para clasificar cuentas.

Ejemplos visibles:

```text
Prospecto
Cliente
Antiguo cliente
Cliente con póliza de servicio
Cliente con plan de lealtad
```

## Relaciones lógicas observadas

### Accounts ↔ Calendars

```text
Accounts.Id = Calendars.AccountId
```

### Accounts ↔ Activities

```text
Accounts.Id = Activities.AccountId_Id
```

y en otras consultas aparece:

```text
Activities.AccountId_Value
```

### Accounts ↔ Opportunities

Se observa una relación basada en nombre:

```text
Accounts.Name = Opportunities.AccountId1_Value
```

Esta relación merece revisión porque utiliza un valor textual en lugar de una clave identificadora en las consultas observadas.

## Escritura

No se identificaron escrituras desde CIC.

---

# 8. `Activities`

## Propósito observado

Fuente de actividad registrada por los vendedores.

Se utiliza para:

- conteo de actividades;
- visitas;
- check-in;
- coordenadas;
- tiempos;
- cobertura de cartera;
- reportes.

## Columnas observadas

```text
Id
SalesRepId_Id
SalesRepId_Value
AccountId_Id
AccountId_Value
Checkin
CheckoutDate
Date
Latitude
Longitude
```

## Relaciones lógicas

```text
Activities.AccountId_Id = Accounts.Id
```

También se utilizan campos de vendedor para agrupar información por representante.

## Ejemplo de uso

CIC puede contar actividades de un vendedor dentro de un periodo y filtrar registros con:

```text
Checkin = 1
```

## Escritura

No se identificaron escrituras de CIC sobre `Activities`.

---

# 9. `Calendars`

## Propósito observado

Representa actividades de calendario/planeación comercial.

Principal consumidor:

```text
modelo/planeacion_modelo.py
```

También aparece en:

```text
modelo/vendedores_modelo.py
modelo/reporte_pdf/servicio_cliente_modelo.py
```

## Columnas observadas

```text
Id
Subject
SalesRepId_Value
DateCreated
TypeId_Value
AccountId
```

## Relación principal

```text
Calendars.AccountId = Accounts.Id
```

## Regla de negocio observada

En planeación se consultan actividades recientes asociadas a cuentas de tipo:

```text
Prospecto
```

Ejemplo conceptual:

```text
Calendars
   │
   └── AccountId
          │
          ▼
       Accounts
          │
          └── TypeId_Value = 'Prospecto'
```

El módulo revisa actividad de los últimos días para evaluar el registro de trabajo comercial.

---

# 10. `Opportunities`

## Propósito observado

Contiene información relacionada con oportunidades comerciales.

Se utiliza para:

- clientes activos;
- clientes nuevos;
- ventas;
- visitas/servicio;
- perfiles.

## Columnas observadas

```text
AccountId1_Id
AccountId1_Value
ClosedDate
Date
DateCreated
EstVisitTimeHrs
SalesRepId_Value
SalesRepName
StatusId_Value
Total
TypeName
```

## Estado de venta observado

Para identificar operaciones vendidas aparece:

```text
StatusId_Value = '7. Vendido'
```

## Relación lógica observada

En perfiles:

```text
Accounts.Name = Opportunities.AccountId1_Value
```

## Uso para clientes activos

Un cliente activo puede derivarse de:

```text
Account.TypeId_Value = 'Cliente'
AND Account.Deleted = 0
AND Opportunity.StatusId_Value = '7. Vendido'
AND YEAR(Opportunity.ClosedDate) = YEAR(GETDATE())
```

---

# 11. `vw_Activities`

## Tipo

Vista SQL.

## Propósito observado

Fuente simplificada para cálculos de tiempo de visitas.

## Columnas utilizadas

```text
SalesRepName
EstVisitTimeHrs
TypeName
Date
```

## Reglas observadas

Para visitas:

```text
TypeName = 'Visita'
```

CIC calcula:

```text
SUM(EstVisitTimeHrs)
AVG(EstVisitTimeHrs)
```

por vendedor y periodo.

## Escritura

No aplica.

---

# 12. `dev_Detalle_Corregida`

## Importancia

Esta es una de las estructuras más importantes para el análisis de ventas de CIC.

Es utilizada por:

```text
modelo/exceles_modelo.py
modelo/ventas_reales_modelo.py
modelo/rendimiento_modelo.py
modelo/vendedores_modelo.py
modelo/admin/admin_modelo.py
modelo/reporte_pdf/*
```

## Función

Recibe información procesada durante la importación de archivos Excel y posteriormente sirve como fuente para:

- ventas reales;
- rendimiento;
- reportes;
- análisis por vendedor;
- análisis por cliente;
- análisis por clase;
- análisis por categoría.

## Columnas observadas

```text
NumeroDeDocumento
Fecha
Tipo
EstadoTransaccion
Cliente_RFC
NombreCliente
Id_Cliente_FM
Articulo
Descripcion
Clase
CantidadVendida
PrecioDeVenta
PrecioUnitario
Importe
Moneda
TipoDeCambio
Ingresos
RepresentanteDeVentas
Id_Vendedor_FM
NumerosDeSerie
TipoDeCambioUSD
IngresosUSD
```

## Flujo

```text
Excel de ventas
      │
      ▼
ExcelesModelo
      │
      ├── mapeo
      ├── validación
      ├── transformación
      ├── tipo de cambio
      └── normalización
      │
      ▼
dev_Detalle_Corregida
      │
      ├── ventas reales
      ├── rendimiento
      ├── perfiles
      └── reportes
```

## Escritura

Se observan operaciones:

```text
INSERT
```

desde `exceles_modelo.py`.

## Riesgo de datos

Debido a que múltiples módulos dependen de esta tabla, cambios en:

- nombres de columnas;
- reglas de importación;
- cálculo de ingresos;
- moneda;
- asignación de vendedor;
- fechas;

pueden afectar varias funcionalidades simultáneamente.

Debe considerarse una estructura crítica.

---

# 13. `vw_CategoriaIngresos`

## Tipo

Vista SQL.

## Uso

Fuente para análisis:

```text
categorías vs ingresos
```

Es utilizada por:

```text
modelo/ventas_reales_modelo.py
modelo/exceles_modelo.py
```

## Columnas utilizadas

En las consultas revisadas aparecen al menos:

```text
RepresentanteDeVentas
Clase
IngresosUSD
FechaReal
```

## Transformación

CIC aplica reglas `CASE` sobre `Clase` para construir categorías comerciales.

Ejemplos:

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
No Categorizado
```

Estas reglas forman parte de la lógica de negocio y deberán documentarse también en `modules.md` o en una especificación específica de ventas.

---

# 14. `UsuariosCIC`

## Propósito

Usuarios propios de la aplicación CIC.

Se utiliza para:

- autenticación;
- estado del usuario;
- identificación personal;
- cargo;
- zona;
- correo;
- contraseña;
- destinatarios de reportes.

## Columnas observadas

```text
IdUsuario
Nombre
Apellido
Cargo
Zona
Status
Correo
Password
```

## Regla de usuario activo

```text
Status = 1
```

## Autenticación activa observada

La implementación activa consulta:

```text
Correo = ?
Password = ?
Status = 1
```

Existe código comentado que utiliza `bcrypt`, pero la función activa revisada compara el valor de `Password` directamente en SQL.

### Consideración de seguridad

Esto debe revisarse.

La existencia de código de migración/cifrado indica que se contempló el uso de hashes, pero no debe asumirse que la autenticación activa ya utiliza bcrypt.

**Recomendación:** validar el contenido real de `UsuariosCIC.Password` y migrar a validación mediante hash si todavía se almacenan contraseñas comparables directamente.

---

# 15. `Metas`

## Propósito

Almacena metas mensuales por vendedor.

## Columnas observadas

```text
idMeta
NombreVendedor
ValorMeta
MesMeta
FechaRegistro
YearMeta
```

## Identidad lógica utilizada por CIC

El código considera única conceptualmente la combinación:

```text
NombreVendedor
MesMeta
YearMeta
```

Antes de insertar verifica si ya existe un registro con esos tres valores.

Esto **no confirma** que exista un `UNIQUE CONSTRAINT` físico.

## Operaciones

```text
SELECT
INSERT
UPDATE
```

## Flujo

```text
Vendedor + Mes + Año
        │
        ▼
       Meta
        │
        ▼
Comparación con ventas reales
```

## Dependencias

Utilizada por:

```text
metas_modelo.py
ventas_reales_modelo.py
rendimiento_modelo.py
exceles_modelo.py
```

---

# 16. `PresupuestoSegmentos`

## Propósito

Almacena presupuesto comercial por vendedor, periodo y segmento.

## Columnas observadas

```text
idPresupuestoSegmento
NombreVendedor
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
MesPresupuesto
YearPresupuesto
FechaRegistro
```

## Identidad lógica

El código verifica existencia mediante:

```text
NombreVendedor
MesPresupuesto
YearPresupuesto
```

## Operaciones

```text
SELECT
INSERT
UPDATE
```

## Uso

Permite comparar ingresos reales con presupuesto por segmento comercial.

---

# 17. `MovilidadRegistro`

## Propósito

Almacena registros de kilometraje/movilidad introducidos en CIC.

## Columnas observadas

```text
id_MovilidadRegistro
Vendedor
Kilometros
Descripcion
Fecha_Movilidad
Fecha_Registro
```

## Operaciones

```text
SELECT
INSERT
DELETE
```

## Consultas

CIC puede calcular:

```text
SUM(Kilometros)
```

por vendedor, mes y año.

## Eliminación

Existen dos estrategias:

### Por valores

```text
Vendedor
Fecha_Movilidad
Kilometros
```

### Por identificador

```text
id_MovilidadRegistro
```

La eliminación por ID es más determinista y el propio código la describe como más confiable.

---

# 18. `ResumenMovilidad`

## Propósito

Almacena indicadores mensuales agregados de movilidad y visitas.

## Columnas observadas

```text
DiasHabiles
Mes
AvgDiarioRecorrido
CantidadVisitas
TiempoDestinadoAtencion
AvgTiempoConCliente
AvgVisitasPorDia
NombreVendedor
Año
FechaRegistro
```

## Identidad lógica

El código verifica existencia mediante:

```text
NombreVendedor
Mes
Año
```

## Operaciones

```text
SELECT
INSERT
UPDATE
```

## Significado

Esta tabla representa una capa agregada:

```text
datos de movilidad / visitas
          │
          ▼
     cálculo mensual
          │
          ▼
   ResumenMovilidad
          │
          ▼
 análisis / reporte
```

---

# 19. `NotificacionesVendedores`

## Propósito

Forma parte del módulo de seguimiento de planeación/uso de ForceManager.

## Columna observada

```text
VendedorId
```

## Operaciones

```text
SELECT
INSERT
DELETE
```

## Uso

El número de registros por vendedor se interpreta como:

```text
TotalNotificaciones
```

mediante:

```sql
COUNT(*)
GROUP BY VendedorId
```

El sistema también puede reiniciar las notificaciones eliminando los registros del vendedor.

---

# 20. `StrikesVendedores`

## Propósito

Registra strikes asociados a vendedores dentro del seguimiento comercial.

## Columna observada

```text
VendedorId
```

## Operaciones

```text
SELECT
INSERT
```

## Uso

El total se calcula mediante:

```text
COUNT(*)
GROUP BY VendedorId
```

## Relación

`VendedorId` funciona como identificador lógico del vendedor.

El código revisado no permite confirmar si existe una FK física hacia `Users`.

---

# 21. CTEs que no son tablas

Durante la revisión aparecen nombres que pueden parecer entidades persistentes, pero son `Common Table Expressions` creadas dentro de consultas.

No deben documentarse como tablas.

Ejemplos:

```text
ClientesActivos
ClientesNuevos
ClientesBase
TotalClientes
VisitasMensual
ActividadesFiltradas
ActividadesOrdenadas
CalculoDistancias
ParesCoordenadas
CategorizacionVentas
ConteoPorTipo
VentasPorTipo
```

Por ejemplo:

```sql
WITH ClientesActivos AS (...)
```

crea una estructura temporal válida únicamente durante esa consulta.

Esto es importante para evitar confundir lógica SQL con objetos físicos de la base.

---

# 22. Reglas de clientes activos y nuevos

La lógica observada en `perfiles_modelo.py` deriva clientes activos utilizando:

```text
Accounts
+
Opportunities
```

## Cliente activo

Condiciones observadas:

```text
Account.TypeId_Value = 'Cliente'
Account.Deleted = 0
Opportunity.StatusId_Value = '7. Vendido'
YEAR(Opportunity.ClosedDate) = YEAR(GETDATE())
```

## Cliente nuevo

Además de ser activo:

```text
YEAR(Account.DateCreated) = YEAR(GETDATE())
```

Conceptualmente:

```text
Accounts
   │
   ├── tipo Cliente
   ├── no eliminado
   │
   ▼
Opportunities
   │
   └── vendido en año actual
          │
          ▼
     Cliente Activo
          │
          └── Account creado en año actual
                    │
                    ▼
               Cliente Nuevo
```

---

# 23. Cobertura de cartera

La cobertura utiliza principalmente:

```text
Accounts
Activities
```

Se crea una CTE lógica `ClientesBase` con cuentas de tipos como:

```text
Antiguo cliente
Cliente con póliza de servicio
Cliente con plan de lealtad
Cliente
```

Después se analiza actividad/visitas dentro de un periodo.

Esto permite relacionar:

```text
cartera asignada
      │
      ▼
clientes visitados
      │
      ▼
cobertura comercial
```

---

# 24. Relaciones lógicas principales

Las relaciones observadas pueden representarse así:

```text
Users
  │
  └── vendedor / representante
           │
           ├─────────────────────────────┐
           ▼                             ▼
      Activities                    dev_Detalle_Corregida
           │                             │
           ▼                             ▼
       Accounts                      Ventas reales
           │
      ┌────┴─────┐
      ▼          ▼
 Calendars   Opportunities
```

Relaciones explícitas observadas:

```text
Accounts.Id
    =
Calendars.AccountId
```

```text
Accounts.Id
    =
Activities.AccountId_Id
```

```text
Accounts.Name
    =
Opportunities.AccountId1_Value
```

Relaciones funcionales por vendedor:

```text
Users / nombres de vendedor
       │
       ├── Metas.NombreVendedor
       ├── PresupuestoSegmentos.NombreVendedor
       ├── MovilidadRegistro.Vendedor
       ├── ResumenMovilidad.NombreVendedor
       └── dev_Detalle_Corregida.RepresentanteDeVentas
```

Estas últimas son relaciones de negocio observadas, no FKs confirmadas.

---

# 25. Problema potencial: relaciones por nombre

Varias funcionalidades relacionan información mediante nombres de vendedores.

Ejemplos:

```text
NombreVendedor
Vendedor
RepresentanteDeVentas
SalesRepId_Value
SalesRepName
```

Esto introduce riesgo de:

- diferencias de mayúsculas/minúsculas;
- acentos;
- espacios;
- cambios de nombre;
- abreviaturas;
- duplicados;
- vendedores de piso;
- inconsistencias entre fuentes.

Para CIC v1 debe documentarse y controlarse cuidadosamente.

Para CIC v2 conviene evaluar un identificador canónico de vendedor.

---

# 26. Problema potencial: IDs de vendedores en ventas importadas

`dev_Detalle_Corregida` contiene:

```text
RepresentanteDeVentas
Id_Vendedor_FM
```

Esto permite relacionar ventas importadas con ForceManager cuando existe correspondencia.

Sin embargo, las reglas de asignación de `Id_Vendedor_FM` forman parte del proceso de importación y deben considerarse una regla crítica.

Cualquier modificación debe probarse contra:

- vendedores normales;
- vendedores de piso;
- registros sin correspondencia;
- cambios de nombre.

---

# 27. Operaciones de escritura por objeto

Resumen:

```text
dev_Detalle_Corregida
    INSERT

UsuariosCIC
    UPDATE

Metas
    INSERT
    UPDATE

PresupuestoSegmentos
    INSERT
    UPDATE

MovilidadRegistro
    INSERT
    DELETE

ResumenMovilidad
    INSERT
    UPDATE

NotificacionesVendedores
    INSERT
    DELETE

StrikesVendedores
    INSERT
```

Las tablas núcleo ForceSync observadas son utilizadas principalmente en lectura:

```text
Users
Accounts
Activities
Calendars
Opportunities
```

---

# 28. Matriz módulo ↔ datos

| Módulo | Principales objetos |
|---|---|
| Cuadrantes | `Activities`, `vw_Activities`, ventas procesadas, movilidad |
| Ventas reales | `dev_Detalle_Corregida`, `vw_CategoriaIngresos`, `Metas` |
| Importación Excel | `dev_Detalle_Corregida`, `Users` |
| Metas | `Metas` |
| Presupuesto | `PresupuestoSegmentos` |
| Rendimiento | `dev_Detalle_Corregida`, `Metas`, `PresupuestoSegmentos` |
| Kilometraje | `MovilidadRegistro` |
| Resumen movilidad | `ResumenMovilidad` |
| Planeación | `Calendars`, `Accounts`, `NotificacionesVendedores`, `StrikesVendedores` |
| Perfiles | `Accounts`, `Opportunities` |
| Cobertura de cartera | `Accounts`, `Activities` |
| Login/usuarios | `UsuariosCIC` |
| PDF | `dev_Detalle_Corregida`, `Accounts`, `Activities`, `Calendars`, `Opportunities`, metas y datos derivados |

---

# 29. Objetos críticos

Por impacto funcional, los siguientes objetos deben considerarse de alta relevancia.

## `dev_Detalle_Corregida`

Porque alimenta gran parte de ventas y reportes.

## `Activities`

Porque participa en actividad, visitas, GPS y cobertura.

## `Accounts`

Porque representa clientes/prospectos y participa en múltiples relaciones.

## `Metas`

Porque alimenta comparaciones de desempeño.

## `PresupuestoSegmentos`

Porque alimenta análisis por segmentos.

## `MovilidadRegistro` / `ResumenMovilidad`

Porque contienen información complementaria de movilidad.

## `UsuariosCIC`

Porque controla acceso a la aplicación.

---

# 30. Integridad actualmente gestionada por aplicación

Se observan reglas de integridad implementadas desde Python.

Ejemplos:

## Metas

Antes de insertar:

```text
NombreVendedor + MesMeta + YearMeta
```

debe no existir.

## Presupuesto

Antes de insertar:

```text
NombreVendedor + MesPresupuesto + YearPresupuesto
```

debe no existir.

## Resumen de movilidad

Antes de insertar:

```text
NombreVendedor + Mes + Año
```

debe no existir.

Estas verificaciones reducen duplicados desde la aplicación, pero no demuestran la existencia de constraints equivalentes en SQL Server.

---

# 31. Transacciones

Las operaciones de escritura observadas siguen generalmente el patrón:

```python
conn = db.get_connection()
cursor = conn.cursor()

cursor.execute(...)

conn.commit()

cursor.close()
conn.close()
```

Esto significa que las operaciones individuales se confirman explícitamente mediante `commit()`.

Debe revisarse con especial cuidado cualquier proceso que realice múltiples inserciones consecutivas para determinar si requiere una transacción atómica más amplia.

---

# 32. Consultas parametrizadas

Gran parte de las consultas utiliza placeholders:

```text
?
```

con parámetros enviados mediante `cursor.execute()` o `pandas.read_sql()`.

Ejemplo conceptual:

```sql
WHERE NombreVendedor = ?
AND MesMeta = ?
AND YearMeta = ?
```

Esto es preferible a concatenar directamente valores proporcionados por usuario.

Sin embargo, también existen consultas construidas dinámicamente para listas, filtros o categorías.

Deben revisarse individualmente durante futuras auditorías de seguridad/mantenibilidad.

---

# 33. Fechas

CIC utiliza varios formatos y conceptos temporales:

```text
Fecha
FechaReal
Date
DateCreated
ClosedDate
CheckoutDate
Fecha_Movilidad
Fecha_Registro
FechaRegistro
Mes
Año
MesMeta
YearMeta
MesPresupuesto
YearPresupuesto
```

Esta variedad refleja diferentes fuentes.

Es recomendable que `modules.md` documente qué fecha se utiliza en cada indicador.

Un error al elegir entre fecha de creación, cierre, venta o visita puede producir resultados comercialmente incorrectos aun cuando la consulta SQL sea técnicamente válida.

---

# 34. Dinero y moneda

`dev_Detalle_Corregida` contiene campos observados como:

```text
PrecioDeVenta
PrecioUnitario
Importe
Moneda
TipoDeCambio
Ingresos
TipoDeCambioUSD
IngresosUSD
```

La existencia de valores originales y convertidos permite realizar análisis normalizados.

La lógica de tipo de cambio está relacionada con la integración de Banxico descrita en `architecture.md`.

Las reglas exactas de conversión deben documentarse como regla de negocio independiente.

---

# 35. Datos derivados

No toda la información que utiliza CIC está almacenada directamente.

El sistema genera indicadores mediante:

- `SUM`;
- `COUNT`;
- `AVG`;
- CTEs;
- agrupaciones por vendedor;
- agrupaciones por mes;
- reglas `CASE`;
- filtros por estado;
- filtros por tipo de cliente;
- filtros por periodos.

Por tanto:

```text
Dato SQL
   │
   ▼
Consulta
   │
   ▼
Regla de negocio
   │
   ▼
Indicador CIC
```

Un indicador debe documentarse con su consulta/regla y no únicamente con el nombre de la tabla fuente.

---

# 36. Información no confirmada por el repositorio

La revisión actual no permite afirmar con certeza:

- tipos SQL exactos de todas las columnas;
- longitudes de `varchar`/`nvarchar`;
- PK físicas;
- FK físicas;
- índices;
- constraints `UNIQUE`;
- defaults;
- triggers;
- procedimientos almacenados;
- definición SQL completa de las vistas;
- propietario/origen administrativo de cada objeto;
- volumen de registros;
- frecuencia de sincronización ForceManager → ForceSyncDB_Worker;
- políticas de backup;
- retención histórica.

Estas cuestiones deberán validarse directamente en SQL Server.

---

# 37. Consultas recomendadas para completar la documentación

En una siguiente etapa se recomienda obtener del servidor:

```sql
SELECT
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
ORDER BY TABLE_SCHEMA, TABLE_NAME;
```

Columnas:

```sql
SELECT
    TABLE_SCHEMA,
    TABLE_NAME,
    COLUMN_NAME,
    DATA_TYPE,
    CHARACTER_MAXIMUM_LENGTH,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
ORDER BY TABLE_NAME, ORDINAL_POSITION;
```

Claves:

```sql
SELECT
    OBJECT_NAME(parent_object_id) AS Tabla,
    name AS ConstraintName,
    type_desc
FROM sys.objects
WHERE type IN ('PK', 'F', 'UQ')
ORDER BY Tabla;
```

Índices:

```sql
SELECT
    OBJECT_NAME(i.object_id) AS Tabla,
    i.name AS Indice,
    i.is_unique,
    i.is_primary_key
FROM sys.indexes i
WHERE OBJECTPROPERTY(i.object_id, 'IsUserTable') = 1
ORDER BY Tabla, Indice;
```

Definición de vistas:

```sql
SELECT
    OBJECT_NAME(object_id) AS Vista,
    definition
FROM sys.sql_modules
WHERE OBJECTPROPERTY(object_id, 'IsView') = 1;
```

Estas consultas deben ejecutarse con permisos adecuados y revisarse antes de incorporar sus resultados al repositorio.

---

# 38. Recomendación para respaldo de esquema

Conviene conservar dentro de documentación una representación del esquema, no necesariamente un backup completo de datos.

Por ejemplo:

```text
docs/database/
├── schema_tables.sql
├── schema_views.sql
├── schema_keys.sql
└── data_dictionary.md
```

No deben incluirse:

- credenciales;
- información personal innecesaria;
- datos comerciales sensibles;
- backups `.bak` completos sin una política explícita.

---

# 39. Consideraciones para CIC v2

CIC v2 debería evitar depender de nombres de vendedor como relación principal siempre que exista un identificador estable.

Conceptualmente:

```text
Vendedor
   │
   └── vendedor_id canónico
          │
          ├── ventas
          ├── metas
          ├── presupuesto
          ├── movilidad
          ├── actividades
          └── reportes
```

También conviene separar:

```text
fuentes externas
       │
       ▼
capa de acceso a datos
       │
       ▼
reglas de negocio
       │
       ▼
API
```

Estas son recomendaciones para la nueva versión y no describen el esquema actual.

---

# 40. Reglas de mantenimiento de este documento

Actualizar `database.md` cuando ocurra alguno de los siguientes cambios:

- nueva tabla;
- nueva vista;
- eliminación de un objeto;
- cambio de columna utilizada;
- nueva relación entre entidades;
- nueva operación de escritura;
- modificación del proceso de importación;
- cambio en metas/presupuestos;
- cambio en movilidad;
- cambio de autenticación;
- cambio en reglas de ventas;
- migración de una fuente de datos.

El cambio técnico debe registrarse además en:

```text
logs/dev_log.csv
```

Si implica una decisión estructural, documentarla en:

```text
docs/decisions.md
```

---

# 41. Documentos relacionados

```text
README.md
```

Instalación y configuración general.

```text
docs/architecture.md
```

Arquitectura de aplicación e integraciones.

```text
docs/modules.md
```

Deberá describir reglas de negocio por funcionalidad.

```text
docs/reports.md
```

Deberá describir el origen de cada dato utilizado en reportes.

```text
logs/development.md
```

Historia del proyecto.

```text
logs/roadmap.md
```

Evolución planificada.

---

# 42. Conclusión

La base `ForceSyncDB_Worker` funciona como núcleo de integración de información para CIC v1.

CIC consume entidades operativas procedentes del ecosistema ForceSync/ForceManager, incorpora ventas procesadas y mantiene información complementaria propia para metas, presupuestos, movilidad, autenticación y seguimiento.

La estructura más crítica observada para ventas es:

```text
dev_Detalle_Corregida
```

mientras que la actividad comercial depende principalmente de:

```text
Accounts
Activities
Calendars
Opportunities
Users
```

La principal conclusión para mantenimiento es:

> **La base de datos de CIC no debe entenderse únicamente como un conjunto de tablas; gran parte del comportamiento del sistema está definido por relaciones lógicas y reglas SQL distribuidas en los modelos.**

Por ello, la siguiente etapa documental debe trasladar esas reglas hacia `modules.md`, donde cada funcionalidad pueda describirse junto con sus entradas, consultas, transformaciones y salidas.
