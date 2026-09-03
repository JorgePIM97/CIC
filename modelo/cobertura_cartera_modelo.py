# modelo/cobertura_cartera_modelo.py
import pandas as pd
from modelo.db_connection import DatabaseConnection

class CoberturaCarteraModelo:
    def __init__(self):
        self.db = DatabaseConnection()

    def obtener_cobertura(
        self,
        fecha_inicio: str,
        fecha_fin: str,
        dias_actividad: int,
        vendedores: list,
    ) -> pd.DataFrame:
        """
        Ejecuta el KPI de Cobertura de Cartera Comercial.

        Parámetros
        ----------
        fecha_inicio   : str  - Fecha inicio del periodo  (YYYY-MM-DD)
        fecha_fin      : str  - Fecha fin del periodo     (YYYY-MM-DD)
        dias_actividad : int  - Días hacia atrás para definir cliente activo
        vendedores     : list - Lista de SalesRepId1_Value a filtrar

        Retorna
        -------
        pd.DataFrame con columnas:
            Rep. de ventas | Año | No. Mes | Mes |
            Clientes Visitados en el mes | Clientes activos | Cobertura de cartera (%)
        """
        if not vendedores:
            return pd.DataFrame()

        # Un placeholder '?' por cada vendedor (aparece 2 veces en el query)
        placeholders = ", ".join(["?" for _ in vendedores])

        query = f"""
            WITH ClientesBase AS (
                SELECT
                    a.Id,
                    a.SalesRepId1_Value
                FROM Accounts a
                WHERE a.TypeId_Value IN (
                    'Antiguo cliente',
                    'Cliente con póliza de servicio',
                    'Cliente con plan de lealtad',
                    'Cliente'
                )
                AND a.SalesRepId1_Value IN ({placeholders})
                AND EXISTS (
                    SELECT 1
                    FROM Activities act
                    WHERE act.AccountId_Id = a.Id
                      AND act.CheckoutDate >= DATEADD(DAY, -?, CAST(? AS DATE))
                      AND act.CheckoutDate <= CAST(? AS DATE)
                )
            ),

            TotalClientes AS (
                SELECT
                    SalesRepId1_Value,
                    COUNT(DISTINCT Id) AS TotalClientes
                FROM ClientesBase
                GROUP BY SalesRepId1_Value
            ),

            VisitasMensual AS (
                SELECT
                    act.AccountId_Id,
                    a.SalesRepId1_Value,
                    DATEPART(YEAR,  act.CheckoutDate) AS Anio,
                    DATEPART(MONTH, act.CheckoutDate) AS Mes,
                    DATENAME(MONTH, act.CheckoutDate) AS NombreMes
                FROM Activities act
                INNER JOIN Accounts a
                    ON act.AccountId_Id = a.Id
                WHERE a.TypeId_Value IN (
                    'Antiguo cliente',
                    'Cliente con póliza de servicio',
                    'Cliente con plan de lealtad',
                    'Cliente'
                )
                AND a.SalesRepId1_Value IN ({placeholders})
                AND act.CheckoutDate >= CAST(? AS DATE)
                AND act.CheckoutDate <  DATEADD(DAY, 1, CAST(? AS DATE))
            )

            SELECT
                vm.SalesRepId1_Value             AS [Rep. de ventas],
                vm.Anio                          AS [Año],
                vm.Mes                           AS [No. Mes],
                vm.NombreMes                     AS [Mes],
                COUNT(DISTINCT vm.AccountId_Id)  AS [Clientes Visitados en el mes],
                tc.TotalClientes                 AS [Clientes activos],
                CAST(
                    COUNT(DISTINCT vm.AccountId_Id) * 1.0 / tc.TotalClientes
                    AS DECIMAL(5,2)
                ) * 100                          AS [Cobertura de cartera (%)]
            FROM VisitasMensual vm
            INNER JOIN TotalClientes tc
                ON vm.SalesRepId1_Value = tc.SalesRepId1_Value
            GROUP BY
                vm.SalesRepId1_Value,
                vm.Anio,
                vm.Mes,
                vm.NombreMes,
                tc.TotalClientes
            ORDER BY
                vm.SalesRepId1_Value,
                vm.Anio,
                vm.Mes;
        """

        # Orden exacto de '?' en el query:
        # 1. ClientesBase  → vendedores x1, dias_actividad, fecha_fin (x2)
        # 2. VisitasMensual → vendedores x1, fecha_inicio, fecha_fin
        params = (
            vendedores                                 # IN (...) ClientesBase
            + [dias_actividad, fecha_fin, fecha_fin]   # DATEADD + EXISTS
            + vendedores                               # IN (...) VisitasMensual
            + [fecha_inicio, fecha_fin]                # rango VisitasMensual
        )

        conn = self.db.get_connection()
        try:
            df = pd.read_sql(query, conn, params=params)
        finally:
            conn.close()

        return df