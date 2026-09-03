# modelo/planeacion_modelo.py
import pandas as pd
from .db_connection import DatabaseConnection
import streamlit as st
from vista.seleccion_usuarios.seleccion import SeleccionUsuarios

class PlaneacionModelo:
    def __init__(self):
        self.db = DatabaseConnection()
        self.vendedores_completos = SeleccionUsuarios()

    # ---------------------------------------------------
    # 1) Obtener todos los vendedores (aunque no registren)
    # ---------------------------------------------------
    def obtener_vendedores_completos(self):
        try:
            lista = self.vendedores_completos.obtener_vendedores_force()
            df = pd.DataFrame(lista, columns=["Vendedor"])
            return df

        except Exception as e:
            st.error(f"❌ Error al obtener lista completa de vendedores: {e}")
            return pd.DataFrame(columns=["Vendedor"])

    # ---------------------------------------------------
    # 2) Obtener actividades registradas en Calendars
    # ---------------------------------------------------
    def obtener_actividades_vendedores(self):
        query = """
        SELECT 
            c.SalesRepId_Value AS Vendedor,
            COUNT(*) AS TotalActividades
        FROM Calendars AS c
        INNER JOIN Accounts AS a ON a.Id = c.AccountId
        WHERE a.TypeId_Value = 'Prospecto'
          AND c.DateCreated >= DATEADD(DAY, -8, GETDATE())
        GROUP BY c.SalesRepId_Value
        """

        try:
            conn = self.db.get_connection()
            df = pd.read_sql(query, conn)
            conn.close()
            return df

        except Exception as e:
            st.error(f"❌ Error al obtener actividades por vendedor: {e}")
            return pd.DataFrame(columns=["Vendedor", "TotalActividades"])

    # ---------------------------------------------------
    # 3) Combinar vendedores completos + actividades
    # ---------------------------------------------------
    def obtener_tabla_completa_actividades(self):
        vendedores_df = self.obtener_vendedores_completos()
        actividades_df = self.obtener_actividades_vendedores()

        # Hacer merge para incluir vendedores con 0 registros
        df_final = vendedores_df.merge(
            actividades_df,
            on="Vendedor",
            how="left"
        )

        # Rellenar los NaN con ceros para vendedores sin registros
        df_final["TotalActividades"] = df_final["TotalActividades"].fillna(0)

        return df_final

    # ---------------------------------------------------
    # 4) Obtener detalle de actividades (consulta completa)
    # ---------------------------------------------------
    def obtener_detalle_actividades(self):
        query = """
        SELECT 
            c.Id,
            c.Subject,
            c.SalesRepId_Value,
            c.DateCreated,
            c.TypeId_Value,
            a.Name,
            a.TypeId_Value
        FROM Calendars AS c
        INNER JOIN Accounts AS a ON a.Id = c.AccountId
        WHERE a.TypeId_Value = 'Prospecto'
          AND c.DateCreated >= DATEADD(DAY, -8, GETDATE())
        ORDER BY c.DateCreated DESC
        """

        try:
            conn = self.db.get_connection()
            df = pd.read_sql(query, conn)
            conn.close()
            return df

        except Exception as e:
            st.error(f"❌ Error obteniendo detalle de actividades: {e}")
            return pd.DataFrame()

    # ---------------------------------------------------
    # 5) Obtener número de notificaciones
    # ---------------------------------------------------
    def obtener_notificaciones(self):
        query = """
        SELECT VendedorId, COUNT(*) AS TotalNotificaciones
        FROM NotificacionesVendedores
        GROUP BY VendedorId
        """

        try:
            conn = self.db.get_connection()
            df = pd.read_sql(query, conn)
            conn.close()
            return df

        except Exception as e:
            st.error(f"❌ Error obteniendo notificaciones: {e}")
            return pd.DataFrame(columns=["VendedorId", "TotalNotificaciones"])

    # ---------------------------------------------------
    # 6) Insertar notificación
    # ---------------------------------------------------
    def insertar_notificacion(self, vendedor):
        query = "INSERT INTO NotificacionesVendedores (VendedorId) VALUES (?)"

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, vendedor)
            conn.commit()
            cursor.close()
            conn.close()
            return True

        except Exception as e:
            st.error(f"❌ Error insertando notificación: {e}")
            return False

    # ---------------------------------------------------
    # 7) Insertar strike
    # ---------------------------------------------------
    def insertar_strike(self, vendedor):
        query = "INSERT INTO StrikesVendedores (VendedorId) VALUES (?)"

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, vendedor)
            conn.commit()
            cursor.close()
            conn.close()
            return True

        except Exception as e:
            st.error(f"❌ Error insertando strike: {e}")
            return False

    # ---------------------------------------------------
    # 8) Reiniciar notificaciones del vendedor
    # ---------------------------------------------------
    def reiniciar_notificaciones(self, vendedor):
        query = "DELETE FROM NotificacionesVendedores WHERE VendedorId = ?"

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, vendedor)
            conn.commit()
            cursor.close()
            conn.close()
            return True

        except Exception as e:
            st.error(f"❌ Error reiniciando notificaciones: {e}")
            return False


    # ---------------------------------------------------
    # 9) Obtener número de strikes
    # ---------------------------------------------------
    def obtener_strikes(self):
        query = """
        SELECT VendedorId, COUNT(*) AS TotalStrikes
        FROM StrikesVendedores
        GROUP BY VendedorId
        """

        try:
            conn = self.db.get_connection()
            df = pd.read_sql(query, conn)
            conn.close()
            return df

        except Exception as e:
            st.error(f"❌ Error obteniendo strikes: {e}")
            return pd.DataFrame(columns=["VendedorId", "TotalStrikes"])


    def obtener_detalle_planeacion(self):
        """
        Obtiene la consulta detallada de Calendars + Accounts para los últimos 8 días
        """

        query = """
            SELECT 
                c.Id,
                c.Subject,
                c.SalesRepId_Value,
                c.DateCreated,
                c.TypeId_Value,
                a.Name AS Cuenta,
                a.TypeId_Value AS StatusProspecto
            FROM Calendars AS c
            INNER JOIN Accounts AS a ON a.Id = c.AccountId
            WHERE a.TypeId_Value = 'Prospecto'
            AND c.DateCreated >= DATEADD(DAY, -8, GETDATE())
            ORDER BY c.DateCreated DESC
        """

        try:
            conn = self.db.get_connection()
            df = pd.read_sql(query, conn)
            conn.close()
            return df

        except Exception as e:
            st.error(f"❌ Error al obtener detalle de planeación: {e}")
            return pd.DataFrame()


    def obtener_strikes(self):
        query = """
            SELECT VendedorId, COUNT(*) AS TotalStrikes
            FROM StrikesVendedores
            GROUP BY VendedorId
        """

        try:
            conn = self.db.get_connection()
            df = pd.read_sql(query, conn)
            conn.close()
            return df

        except Exception as e:
            st.error(f"❌ Error obteniendo strikes: {e}")
            return pd.DataFrame()

    def obtener_actividad_semanal(self):
        """
        Regresa el conteo de actividades por día y por vendedor (últimos 8 días)
        """
        query = """
            SELECT 
                c.SalesRepId_Value AS Vendedor,
                CAST(c.DateCreated AS DATE) AS Fecha,
                COUNT(*) AS Total
            FROM Calendars AS c
            INNER JOIN Accounts AS a ON a.Id = c.AccountId
            WHERE a.TypeId_Value = 'Prospecto'
            AND c.DateCreated >= DATEADD(DAY, -8, GETDATE())
            GROUP BY 
                c.SalesRepId_Value,
                CAST(c.DateCreated AS DATE)
            ORDER BY Fecha ASC
        """

        try:
            conn = self.db.get_connection()
            df = pd.read_sql(query, conn)
            conn.close()
            return df

        except Exception as e:
            st.error(f"❌ Error obteniendo actividad semanal: {e}")
            return pd.DataFrame()
        
    def notificacion_existente_hoy(self, vendedor):
        """
        Regresa cuántas notificaciones tiene el vendedor en la fecha actual
        """
        query = """
            SELECT 
                COUNT(*) AS Total
            FROM NotificacionesVendedores
            WHERE VendedorId = ?
            AND CAST(Fecha AS DATE) = CAST(GETDATE() AS DATE)
        """

        try:
            conn = self.db.get_connection()
            df = pd.read_sql(query, conn, params=[vendedor])
            conn.close()

            if df.empty:
                return 0

            return int(df.iloc[0]["Total"])

        except Exception as e:
            st.error(f"❌ Error obteniendo notificación del día: {e}")
            return 0




#################################


