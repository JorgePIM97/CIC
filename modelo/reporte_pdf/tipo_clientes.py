#modelo/reporte_pdf/tipo_clientes.py
import streamlit as st
import pandas as pd
from ..db_connection import DatabaseConnection


class TipoClientesModelo:
    def __init__(self):
        self.db = DatabaseConnection()

    # --------------------------------------------------
    # UTILIDAD INTERNA
    # --------------------------------------------------
    def _get_id_vendedor(self, vendedor):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT TOP 1 Id_Vendedor_FM
                FROM ForceSyncDB_Worker.dbo.dev_Detalle_Corregida
                WHERE RepresentanteDeVentas = ?
            """

            cursor.execute(query, (vendedor,))
            row = cursor.fetchone()

            cursor.close()
            conn.close()

            return row[0] if row else None

        except Exception as e:
            st.error(f"Error obteniendo Id_Vendedor_FM: {e}")
            return None
        
    # --------------------------------------------------
    # 1. ACTIVIDAD POR TIPO DE CLIENTE
    # --------------------------------------------------
    def get_actividad_tipo_cliente(self, vendedor, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return pd.DataFrame()

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT TipoAgrupado, COUNT(*) AS Cantidad
                FROM (
                    SELECT 
                        CASE 
                            WHEN ac.TypeId_Value IN (
                                'Cliente con póliza de servicio',
                                'Cliente con plan de lealtad',
                                'Cliente'
                            ) THEN 'Cliente'
                            ELSE ac.TypeId_Value
                        END AS TipoAgrupado
                    FROM Activities AS act
                    INNER JOIN Accounts AS ac 
                        ON ac.Id = act.AccountId_Id
                    WHERE ac.TypeId_Value IN (
                        'Prospecto', 
                        'Antiguo cliente', 
                        'Cliente con póliza de servicio', 
                        'Cliente con plan de lealtad', 
                        'Cliente'
                    )
                    AND act.SalesRepId_Id = ?
                    AND YEAR(act.Date) = ?       -- ← filtro por año sobre la fecha de la actividad
                ) AS datos
                GROUP BY TipoAgrupado
            """

            cursor.execute(query, (id_vendedor, año))
            rows    = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            cursor.close()
            conn.close()

            if rows:
                return pd.DataFrame([dict(zip(columns, row)) for row in rows])
            return pd.DataFrame(columns=columns)

        except Exception as e:
            st.error(f"Error en actividad por tipo de cliente: {e}")
            return pd.DataFrame()