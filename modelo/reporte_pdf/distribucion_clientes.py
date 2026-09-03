#modelo/reporte_pdf/distribucion_cliente.py
import streamlit as st
import pandas as pd
import calendar
from ..db_connection import DatabaseConnection


class DistribucionClienteModelo:
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
    # 1. DISTRIBUCION CLIENTES
    # --------------------------------------------------
    def get_distribucion_clientes(self, vendedor, mes_nombre, año):
        try:
            id_vendedor = self._get_id_vendedor(vendedor)
            if not id_vendedor:
                return pd.DataFrame()

            # Convertir mes_nombre a número
            meses = {
                'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4,
                'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8,
                'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
            }
            mes_num = meses.get(mes_nombre)
            if not mes_num:
                st.error(f"Mes no reconocido: {mes_nombre}")
                return pd.DataFrame()

            # Fecha de referencia: último día del mes seleccionado
            ultimo_dia = calendar.monthrange(año, mes_num)[1]
            fecha_ref  = f"{año}-{mes_num:02d}-{ultimo_dia}"   # ej. '2024-06-30'

            conn = self.db.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT 
                    COUNT(CASE 
                        WHEN DateCreated >= DATEADD(MONTH, -4, CAST(? AS DATE))
                        AND Deleted = 0 
                        AND SalesRepId1_Id = ?
                        THEN Name 
                    END) AS Atendidos,
                    
                    COUNT(CASE 
                        WHEN DateCreated >= DATEADD(MONTH, -1, CAST(? AS DATE))
                        AND Deleted = 0 
                        AND SalesRepId1_Id = ?
                        THEN Name 
                    END) AS [Fuera de Cobertura]

                FROM [ForceSyncDB_Worker].[dbo].[Accounts]
                WHERE 
                    DateCreated >= DATEADD(MONTH, -4, CAST(? AS DATE))
                    AND DateCreated <= CAST(? AS DATE)
                    AND Deleted = 0
                    AND SalesRepId1_Id = ?
            """

            cursor.execute(query, (
                fecha_ref, id_vendedor,   # Activos
                fecha_ref, id_vendedor,   # Nuevos
                fecha_ref, fecha_ref,     # WHERE rango
                id_vendedor
            ))

            row     = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]

            cursor.close()
            conn.close()

            if row:
                # ✅ Fix: dict evita el error de shape al construir el DataFrame
                return pd.DataFrame([dict(zip(columns, row))])
            return pd.DataFrame(columns=columns)

        except Exception as e:
            st.error(f"Error en distribución de clientes: {e}")
            return pd.DataFrame()